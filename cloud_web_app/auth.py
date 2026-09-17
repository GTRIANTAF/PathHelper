"""
auth.py — Student AM verification via webmail code.

MOCK MODE: The code is returned from send_code() so the UI can display it on screen.
When a real SMTP account is available, replace the mock block in send_code() with
smtplib logic and stop returning the code to the UI.
"""

import random
import time
from typing import Dict


# In-memory store: { am: {"code": "123456", "expires": <timestamp>} }
_pending: Dict[str, dict] = {}

CODE_TTL_SECONDS = 600  # 10 minutes


def generate_code() -> str:
    """Return a zero-padded 6-digit string."""
    return f"{random.randint(0, 999999):06d}"


def send_code(am: str) -> tuple[bool, str]:
    """
    Generate a code, store it, and 'send' it.
    Returns (True, "") on success, or (False, "error message") on failure.
    """
    code = generate_code()
    _pending[am] = {"code": code, "expires": time.time() + CODE_TTL_SECONDS}

    import smtplib, ssl
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    # Using the credentials provided
    smtp_user = "ceidpathadvisor@gmail.com"
    smtp_pass = "dqpdfeyazeetpfyv"
    
    recipient = f"up{am}@ac.upatras.gr"
    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Subject"] = "CEID Path Advisor — Κωδικός Επαλήθευσης"
    body = f"Ο κωδικός επαλήθευσής σου είναι: {code}\nΙσχύει για 10 λεπτά."
    msg.attach(MIMEText(body, "plain", "utf-8"))
    
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient, msg.as_string())
    except smtplib.SMTPAuthenticationError:
        return False, "Σφάλμα ταυτοποίησης email (SMTP Auth Error). Βεβαιωθείτε ότι χρησιμοποιείτε 'App Password' της Google και όχι τον κανονικό κωδικό."
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False, f"Αποτυχία αποστολής email: {str(e)}"
        
    return True, ""


def verify_code(am: str, entered: str) -> tuple[bool, str]:
    """
    Check the code.  Returns (success: bool, message: str).
    """
    record = _pending.get(am)
    if not record:
        return False, "Δεν έχει σταλεί κωδικός για αυτό το ΑΜ. Πάτησε «Αποστολή Κωδικού»."
    if time.time() > record["expires"]:
        _pending.pop(am, None)
        return False, "Ο κωδικός έληξε. Ζήτησε νέο κωδικό."
    if entered.strip() != record["code"]:
        return False, "Λάθος κωδικός. Δοκίμασε ξανά."
    _pending.pop(am, None)   # invalidate after use
    return True, "OK"


def is_valid_am(am: str) -> bool:
    """Basic sanity-check: AM should be 7 digits."""
    return am.isdigit() and 6 <= len(am) <= 8
