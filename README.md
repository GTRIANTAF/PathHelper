# 🎓 CEID Path Helper & AI Advisor

Ένα ολοκληρωμένο εργαλείο υποστήριξης φοιτητών για το τμήμα Μηχανικών Η/Υ και Πληροφορικής (CEID). Το project συνδυάζει έναν τοπικό scraper για την εξαγωγή βαθμολογιών και μια cloud εφαρμογή με AI Advisor και Path Checker.

## Αρχιτεκτονική Συστήματος

Το σύστημα αποτελείται από δύο ανεξάρτητα υποσυστήματα:

1.  **Local Scraper (CLI Tool):** Τρέχει τοπικά στον υπολογιστή του χρήστη για μέγιστη ασφάλεια. Συνδέεται στο "Progress" και εξάγει τους βαθμούς σε ένα αρχείο `my_grades.json`.
2.  **Cloud Web App (Streamlit):** Η κύρια εφαρμογή που φιλοξενείται στο Streamlit Cloud.
    * **AI Advisor:** Ένα RAG-based chatbot (Groq Llama 3.3/Mixtral) που αναλύει τους βαθμούς σου και προτείνει μαθήματα βάσει των κανόνων του τμήματος.
    * **Path Checker:** Ένα διαδραστικό εργαλείο ελέγχου των κανόνων λήψης διπλώματος και οργάνωσης εξαμήνων.

---

## 🚀 Οδηγίες Χρήσης

### 1. Εξαγωγή Βαθμών (Local)
Πριν ξεκινήσετε, πρέπει να έχετε το αρχείο με τις βαθμολογίες σας.
* Πλοηγηθείτε στον φάκελο `local_Scraper`.
* Εγκαταστήστε τις απαιτήσεις: `pip install -r requirements.txt`.
* Τρέξτε τον scraper: `python upnet_api.py`.
* Συνδεθείτε στο portal και το αρχείο `my_grades.json` θα δημιουργηθεί αυτόματα.

### 2. Χρήση του Web App
* Επισκεφθείτε την εφαρμογή: `ceidassistant.streamlit.app`
* Μεταβείτε στην καρτέλα ** AI Advisor**.
* Ανεβάστε το αρχείο `my_grades.json` στο ειδικό πεδίο.
* Συνομιλήστε με τον Advisor για προσωποποιημένες συμβουλές!

---

## 🛠️ Τεχνολογίες

* **Frontend:** [Streamlit](https://streamlit.io/)
* **AI/LLM:** [Groq Cloud API](https://groq.com/) (llama-4-scout-17b)
* **Web Scraping:** [Selenium](https://www.selenium.dev/) & WebDriver Manager
* **Styling:** Custom CSS & Streamlit Theming

---

## 🔒 Ασφάλεια & Προσωπικά Δεδομένα

* **Zero-Knowledge:** Οι κωδικοί του Upnet δεν αποθηκεύονται πουθενά και δεν στέλνονται ποτέ στο cloud.
* **Local Processing:** Η εξαγωγή των δεδομένων γίνεται αποκλειστικά στη δική σας συσκευή.
* **Cloud Integrity:** Το Web App επεξεργάζεται μόνο τα ονόματα των μαθημάτων και τους βαθμούς που εσείς επιλέγετε να ανεβάσετε.

---

## 📂 Δομή Φακέλων

```text
PathHelper/
├── local_Scraper/           # CLI Tool για scraping
│   ├── upnet_api.py         # Json scraper
|   ├── advisor.py           # CLI Llamma 3.2 advisor
│   └── requirements.txt
├── cloud_web_app/           # Streamlit Web App
│   ├── app.py               # Main entry point
│   ├── connector.py         # API connection
│   ├── knowledge_base.py    # CEID Course Data & Rules
│   └── assets/              # Logos & Images
├── .gitignore
└── requirements.txt         # Cloud dependencies
