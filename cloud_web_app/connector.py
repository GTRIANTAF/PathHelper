import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Φορτώνει τα τοπικά κλειδιά από το .env αρχείο (όταν το τρέχεις στο δικό σου PC)
load_dotenv()


def get_ai_response(chat_history):

    # --- 1. ΑΣΦΑΛΗΣ ΕΥΡΕΣΗ ΤΟΥ API KEY ---
    api_key = None
    try:
        # Προσπαθεί να το βρει στα Streamlit Secrets (όταν είναι live στο Cloud)
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        # Αν δεν το βρει εκεί, το παίρνει από το .env (όταν τρέχει τοπικά)
        api_key = os.getenv("GROQ_API_KEY")

    # Αν για κάποιο λόγο δεν βρει κανένα κλειδί, βγάζει μήνυμα λάθους αντί να "σκάσει"
    if not api_key:
        return "⚠️ Σφάλμα: Το GROQ_API_KEY δεν βρέθηκε! Βεβαιώσου ότι υπάρχει στο αρχείο .env ή στα Streamlit Secrets."

    # --- 2. ΕΠΙΚΟΙΝΩΝΙΑ ΜΕ ΤΟ ΜΟΝΤΕΛΟ ---
    try:
        client = Groq(api_key=api_key)

        # Στέλνουμε το ιστορικό στο μοντέλο της Meta (Llama 3.3)
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=chat_history,
            temperature=0.9,  # Πόσο "δημιουργικό" θα είναι (το 0.7 είναι ιδανικό για συμβουλές)
            max_completion_tokens=2048
        )

        # Επιστρέφουμε καθαρό το κείμενο που μας απάντησε το AI
        return response.choices[0].message.content

    except Exception as e:
        # Αν πέσει το internet ή υπάρξει πρόβλημα με το Groq
        return f"⚠️ Προέκυψε σφάλμα επικοινωνίας με τον σέρβερ: {e}"