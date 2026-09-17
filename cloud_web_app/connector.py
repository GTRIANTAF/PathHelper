import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import json

load_dotenv()

def validate_response(client, draft_response):
    """
    Acts as a secondary agent to validate the primary agent's response.
    Ensures the response is in natural Greek and contains no Chinese characters or hallucinations.
    """
    st.toast("🔍 Quality Control: Checking response...", icon="🛡️")
    
    validator_prompt = """You are a strict Quality Control Agent for a Greek University Advisor.
Your job is to review the draft response below.
RULES:
1. The response MUST be entirely in natural Greek (except for specific course codes or English terminology if necessary).
2. If you see ANY Chinese characters, garbage text, or severe hallucinations, you must FIX the text and translate it properly to Greek.
3. If the draft response is already good and in Greek, you must output it EXACTLY AS IT IS.
4. DO NOT add conversational filler like "Here is the corrected text:". ONLY output the final text.
"""
    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {"role": "system", "content": validator_prompt},
                {"role": "user", "content": f"DRAFT RESPONSE TO REVIEW:\n{draft_response}"}
            ],
            temperature=0.1, # Strict and deterministic
            max_completion_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Validation failed: {e}")
        return draft_response # Fallback to original if validation fails

def get_ai_response(chat_history, mcp_client=None, tools=None):

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

        kwargs = {
            "model": "meta-llama/llama-4-scout-17b-16e-instruct",
            "messages": chat_history,
            "temperature": 0.7,
            "max_completion_tokens": 2048
        }
        if tools:
            kwargs["tools"] = tools

        response = client.chat.completions.create(**kwargs)
        response_message = response.choices[0].message

        # Check if the model wants to call a tool
        tool_calls = response_message.tool_calls

        if tool_calls and mcp_client:
            # We append the assistant's request to the history
            chat_history.append({
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": [
                     {
                         "id": tool_call.id,
                         "type": tool_call.type,
                         "function": {
                             "name": tool_call.function.name,
                             "arguments": tool_call.function.arguments
                         }
                     } for tool_call in tool_calls
                ]
            })

            # Execute each tool
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Show in UI temporarily
                st.toast(f"Running MCP Tool: {function_name}...")

                # Call MCP tool
                function_response = mcp_client.call_tool(function_name, function_args)

                # Append result to history
                chat_history.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(function_response),
                })

            # Make a second call to get the final answer with tool context
            second_response = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=chat_history,
                temperature=0.7,
                max_completion_tokens=2048
            )
            draft_answer = second_response.choices[0].message.content
            return validate_response(client, draft_answer)

        # Επιστρέφουμε καθαρό το κείμενο που μας απάντησε το AI (μέσω του validator)
        draft_answer = response_message.content
        return validate_response(client, draft_answer)

    except Exception as e:
        # Αν πέσει το internet ή υπάρξει πρόβλημα με το Groq
        return f"⚠️ Προέκυψε σφάλμα επικοινωνίας με τον σέρβερ: {e}"