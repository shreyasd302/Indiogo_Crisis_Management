# IndiGo Social Listening Dashboard

An educational Streamlit UI for the MBA social listening project. All 12 posts, labels, alert flags and response drafts are fictional and predefined. No model, LLM, retrieval, live social monitoring or publishing is connected. No API keys are required.

## Run locally

Install Python 3.11 or later, open a terminal in this folder, and run:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed in the terminal (usually http://localhost:8501). Keep that terminal running.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository and upload app.py, requirements.txt and the .streamlit folder at its root. Do not upload the outer project folder as an extra nesting level unless you adjust the app path.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Create a new app, choose your repository and branch, and set the entry point to app.py.
4. Deploy. No secrets or credentials are needed by this app.

## Screenshot for your report

Use a desktop browser around 1440 pixels wide, leave filters on All and select IG01. Keep the demo notice visible. If needed, reduce browser zoom slightly to fit the workspace. Caption:

“Proposed PR dashboard using illustrative data; predictive and LLM components are not yet integrated.”

## Working controls

Topic/sentiment/urgency filters, reset filters, post selection, editable drafts, approval, save edits and rejection work within the current session. Summary cards reflect the filtered records. Edited drafts still require approval. Empty drafts cannot be saved or approved. Approving records a demo decision only and never sends or publishes anything. State resets when the session ends. Saved edits persist when switching posts during the session; unsaved edits may be discarded when switching posts. Save edits before changing the selected post.

The urgent low-spread example IG12 demonstrates that urgent assistance and predicted reach are separate review considerations. This prototype is not affiliated with IndiGo. The sample playbook is team-authored, not official airline guidance.
