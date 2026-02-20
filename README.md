# CEID AI Academic Advisor

A local Retrieval-Augmented Generation (RAG) application that acts as an academic advisor for University of Patras (CEID) students. 

This tool scrapes a student's academic history, processes it against the 2025-2026 CEID Curriculum Rules, and uses a local Large Language Model (Llama 3.2) to recommend a "Direction of Deepening" based on actual academic performance.

Features:
* Automated Data Pipeline: A custom Selenium scraper (`upnet_api.py`) navigates the university portal, pauses for manual CAPTCHA solving, and parses HTML tables.
* Local RAG Architecture: Combines scraped user data with official curriculum rules stored in a JSON knowledge base, passing them to the LLM context window.
* Privacy-First: Executes entirely on local hardware. No student data is transmitted to external APIs.
* Rule Pre-processing: Python logic calculates course completion for "Group A" and "Group B" requirements prior to LLM inference to ensure accurate tracking.

Tech Stack:
* Language: Python 3.13
* AI Engine: Ollama (Llama 3.2)
* Automation: Selenium WebDriver (Chromium)
* OS: Linux (Ubuntu)
