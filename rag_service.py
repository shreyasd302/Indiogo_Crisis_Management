"""RAG Service for IndiGo PR Review Workspace.
Retrieves matching rules from the team-authored Crisis Management Playbook
and generates grounded, policy-compliant responses using Gemini (or OpenAI).
Dynamically auto-discovers supported TEXT models to avoid modality mismatches.
"""
import json
import os
import requests

RULES_PATH = os.path.join(os.path.dirname(__file__), "playbook_rules.json")

def load_rules():
    if not os.path.exists(RULES_PATH):
        return []
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

PLAYBOOK_RULES = load_rules()

def retrieve_rules(mention: str, topic: str = "", top_k: int = 3):
    """Retrieve top-k most relevant rules for a given customer mention."""
    if not PLAYBOOK_RULES:
        return []
    
    keywords = set(mention.lower().replace(",", " ").replace(".", " ").replace("?", " ").split() + [topic.lower()])
    scored = []
    
    governance_codes = {"01.04", "02.04"}
    
    for r in PLAYBOOK_RULES:
        score = 0
        text = (r.get("code", "") + " " + r.get("title", "") + " " + r.get("body", "")).lower()
        for kw in keywords:
            if len(kw) > 3 and kw in text:
                score += 1
        if r.get("code") in governance_codes:
            score += 2
        scored.append((score, r))
        
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for s, r in scored[:top_k]]

def model_priority_score(name: str) -> int:
    name = name.lower()
    # Exclude non-text models (audio, tts, embeddings, images)
    if any(bad in name for bad in ["tts", "audio", "embed", "imagen", "robotics"]):
        return 9999
    # Prioritize trusted text-generation models
    if "gemini-2.0-flash" in name and "exp" not in name:
        return 1
    if "gemini-1.5-flash" in name and "latest" in name:
        return 2
    if "gemini-1.5-flash" in name:
        return 3
    if "gemini-2.0-flash-exp" in name:
        return 4
    if "gemini-1.5-pro" in name:
        return 5
    if "gemini-pro" in name:
        return 6
    if "flash" in name:
        return 7
    if "pro" in name:
        return 8
    return 20

def get_supported_gemini_models(api_key: str) -> list[tuple[str, str]]:
    """Dynamically query Google's ModelService to find TEXT models available for this specific API key."""
    for ver in ["v1beta", "v1"]:
        try:
            url = f"https://generativelanguage.googleapis.com/{ver}/models?key={api_key}"
            r = requests.get(url, timeout=7)
            if r.status_code == 200:
                data = r.json()
                valid = []
                for m in data.get("models", []):
                    methods = m.get("supportedGenerationMethods", [])
                    name = m.get("name", "").replace("models/", "")
                    score = model_priority_score(name)
                    if score < 9000 and "generateContent" in methods:
                        valid.append((ver, name, score))
                if valid:
                    valid.sort(key=lambda x: x[2])
                    return [(ver, name) for ver, name, score in valid]
        except Exception:
            continue
    return []

def generate_rag_draft(mention: str, topic: str, api_key: str, retrieved_rules: list = None) -> tuple[str, list]:
    """Calls Gemini (or OpenAI if sk- key) with retrieved playbook rules to draft a customer response."""
    api_key = (api_key or "").strip()
    if not api_key:
        return "Please enter a valid API key in the sidebar.", []

    if not retrieved_rules:
        retrieved_rules = retrieve_rules(mention, topic)
        
    rules_text = "\n\n".join([
        f"• Rule {r.get('code')}: {r.get('title')}\n  Guidance: {r.get('body')}"
        for r in retrieved_rules
    ])
    
    system_prompt = (
        "You are an IndiGo PR representative responding publicly to a customer on social media.\n\n"
        "OFFICIAL RETRIEVED PLAYBOOK RULES (MANDATORY TO FOLLOW):\n"
        f"{rules_text}\n\n"
        "STRICT COMPLIANCE CONSTRAINTS:\n"
        "1. Never promise refunds, specific compensation amounts, or flight departure times without verified clearance.\n"
        "2. Never ask for or expose PNR numbers, passenger phone numbers, or booking details publicly.\n"
        "3. Always direct the passenger to the airline's verified support channel or airport ground staff for booking-specific assistance.\n"
        "4. Keep the response polite, empathetic, concise (2 sentences), and strictly aligned with IndiGo brand voice.\n"
        "5. Output ONLY the response draft text, nothing else."
    )
    
    user_prompt = f"PASSENGER MENTION ({topic}): \"{mention}\"\n\nDraft the response:"

    # If user provided an OpenAI key (starts with sk-)
    if api_key.startswith("sk-"):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 200
        }
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                draft = resp.json()["choices"][0]["message"]["content"].strip()
                return draft, retrieved_rules
            else:
                err_data = resp.json().get("error", {})
                err_msg = err_data.get("message", resp.text)
                return f"OpenAI API Error ({resp.status_code}): {err_msg}", retrieved_rules
        except Exception as e:
            return f"OpenAI Connection Error: {str(e)}", retrieved_rules

    # Discover text-generating models for this key
    available_models = get_supported_gemini_models(api_key)
    
    if not available_models:
        available_models = [
            ("v1beta", "gemini-2.0-flash"),
            ("v1beta", "gemini-1.5-flash-latest"),
            ("v1beta", "gemini-1.5-flash"),
            ("v1", "gemini-1.5-flash"),
            ("v1beta", "gemini-pro"),
        ]

    last_error = ""
    for ver, model_name in available_models:
        url = f"https://generativelanguage.googleapis.com/{ver}/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": system_prompt + "\n\n" + user_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 200
            }
        }
        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                draft = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                return draft, retrieved_rules
            else:
                try:
                    err_json = resp.json()
                    err_msg = err_json.get("error", {}).get("message", resp.text)
                except Exception:
                    err_msg = resp.text
                last_error = f"Gemini API Error ({resp.status_code}): {err_msg}"
                # Only abort early if the API key itself is bad
                if "API_KEY_INVALID" in err_msg or "API key not valid" in err_msg or resp.status_code == 401:
                    break
                # Otherwise, continue to the next model in the list
        except Exception as e:
            last_error = f"Network Connection Error: {str(e)}"
            continue
            
    return last_error or "Error: Unable to connect to Gemini API. Please check your API key or network connection.", retrieved_rules
