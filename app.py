import streamlit as st
import json
import litellm
import os
from dotenv import load_dotenv

# .env API Key(s)
load_dotenv()

MODEL_OPTIONS = []

# Check available keys
if os.environ.get("OPENAI_API_KEY"):
    MODEL_OPTIONS.extend([
        "gpt-4o",
        "gpt-4o-mini",
    ])

if os.environ.get("ANTHROPIC_API_KEY"):
    MODEL_OPTIONS.extend([
        "claude-sonnet-4-20250514",
        "claude-haiku-4-5-20251001",
    ])

if os.environ.get("GEMINI_API_KEY"):
    MODEL_OPTIONS.extend([
        "gemini/gemini-2.5-flash",
        "gemini/gemini-2.5-pro",
    ])

# Streamlit Setup
st.set_page_config(page_title="Client Enquiry Parser", page_icon="📬", layout="centered")

# System prompt
SYSTEM_INSTRUCTION = """
You are an intelligent customer support assistant. Your job is to analyze incoming client enquiries and route them appropriately.

Analyze the user's input and provide a JSON response with the following structure:
{
  "classification": "One of: 'New Client', 'Support Request', 'Complaint', 'General Question', or 'Invalid/Spam'",
  "confidence_score": <float between 0.0 and 1.0 representing your certainty>,
  "suggested_action": "A brief instruction for the internal team on how to handle this (e.g., 'Route to Billing', 'Discard')",
  "draft_response": "A polite, professional draft email response. If the input is Invalid/Spam, leave this blank."
}

Rules:
1. Empathy is key for complaints. Always apologize and de-escalate.
2. If the input is a single word, gibberish, or highly vague (e.g., "help", "asdflkj", "hi"), classify it as 'Invalid/Spam' with a low confidence score, and suggest asking the user for more details.
3. ONLY output valid JSON. No markdown formatting, no conversational text before or after the JSON.
"""

def analyze_enquiry(enquiry_text, model):
    """Sends the enquiry to the AI and parses the JSON response."""
    try:
        response = litellm.completion(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": enquiry_text}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

# Streamlit Web UI
st.title("📬 AI Client Enquiry Parser")
st.write("Paste a customer email or web form submission below to classify it, score it, and generate a draft response.")

if not MODEL_OPTIONS:
    st.error("No API keys found in your .env file. Please add at least one.")
    st.stop()

enquiry_input = st.text_area("Client Enquiry:", height=150, placeholder="E.g., Hello, I'm interested in a property you guys have listed.")

# AI model selection
model = st.selectbox("Choose Model", MODEL_OPTIONS)

if st.button("Process Enquiry", type="primary"):
    if not enquiry_input.strip():
        st.warning("Please enter an enquiry.")
    else:
        with st.spinner("Analyzing with AI..."):
            result = analyze_enquiry(enquiry_input, model)

            if "error" in result:
                st.error(f"Failed to process via AI: {result['error']}")
            else:
                # Print JSON for debug
                print(json.dumps(result, indent=4))
                
                st.subheader("Analysis Results")
                col1, col2 = st.columns(2)
                
                # Category
                category = result.get("classification", "Unknown")
                if category == "Complaint":
                    col1.error(f"**Category:** {category}")
                elif category == "Support Request":
                    col1.warning(f"**Category:** {category}")
                elif category == "New Client":
                    col1.success(f"**Category:** {category}")
                else:
                    col1.info(f"**Category:** {category}")
                
                # Confidence
                score = result.get('confidence_score', 0)
                col2.metric(label="AI Confidence", value=f"{score * 100:.1f}%")

                # Suggested action
                st.info(f"**Internal Action Recommended:** {result.get('suggested_action', 'N/A')}")
                
                # Staff draft response
                draft = result.get("draft_response", "")
                if draft:
                    st.text_area("Draft Response (Ready to Copy):", value=draft, height=200)
                else:
                    st.write("*No draft response generated (likely invalid or spam).*")