"""IndiGo Social Listening & Crisis Response PR Workspace
Educational UI prototype with live Retrieval-Augmented Generation (RAG)
grounded in the IndiGo Crisis Management Playbook and powered by Google Gemini.
Features aviation-grade UI styling, custom flight cursor, and audit trail export.
"""
import html
import io
import os
import pandas as pd
import streamlit as st
from rag_service import retrieve_rules, generate_rag_draft, PLAYBOOK_RULES

st.set_page_config(page_title="IndiGo | Navigating Turbulence", page_icon="✈️", layout="wide")

# ----------------- AVIATION THEME & FLIGHT ANIMATIONS -----------------
st.markdown('''<style>
/* Custom Airplane Cursors */
html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
    cursor: url('data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2228%22%20height%3D%2228%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22%2360A5FA%22%20stroke%3D%22%231D4ED8%22%20stroke-width%3D%221.5%22%3E%3Cpath%20d%3D%22M21%2016v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10%202.67%2010%203.5V9l-8%205v2l8-2.5V19l-2%201.5V22l3.5-1%203.5%201v-1.5L13%2019v-5.5l8%202.5z%22/%3E%3C/svg%3E') 14 14, auto !important;
}

button, [role="button"], a, select, input, textarea, [data-baseweb="select"] {
    cursor: url('data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22%20width%3D%2228%22%20height%3D%2228%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22%2393C5FD%22%20stroke%3D%22%233B82F6%22%20stroke-width%3D%221.5%22%3E%3Cpath%20d%3D%22M21%2016v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10%202.67%2010%203.5V9l-8%205v2l8-2.5V19l-2%201.5V22l3.5-1%203.5%201v-1.5L13%2019v-5.5l8%202.5z%22/%3E%3C/svg%3E') 14 14, pointer !important;
}

.block-container { padding-top: 1.4rem; padding-bottom: 1.5rem; max-width: 1520px; }

/* Flight Flight Icon Floating Animation */
@keyframes jetFly {
    0% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-5px) rotate(2deg); }
    100% { transform: translateY(0px) rotate(0deg); }
}

.jet-icon {
    display: inline-block;
    animation: jetFly 3.5s ease-in-out infinite;
    font-size: 2.2rem;
    vertical-align: middle;
    margin-right: 8px;
    filter: drop-shadow(0 0 10px rgba(96, 165, 250, 0.6));
}

/* Radar Pulse for Crisis Alerts */
@keyframes radarPulse {
    0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.45); border-left-color: #EF4444; }
    50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0.1); border-left-color: #F87171; }
    100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); border-left-color: #EF4444; }
}

.alert-radar {
    background: linear-gradient(135deg, #261614, #1B1214);
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 11px 14px;
    font-size: 12.5px;
    line-height: 1.5;
    margin: 10px 0;
    color: #FCA5A5;
    animation: radarPulse 2.8s infinite;
}

.alert-standard {
    background: #172136;
    border-left: 3px solid #3B82F6;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 12.5px;
    line-height: 1.5;
    margin: 10px 0;
    color: #BFDBFE;
}

/* Boarding Pass Badge */
.boarding-pass-badge {
    display: inline-block;
    background: #101B33;
    border: 1px dashed #3B82F6;
    color: #93C5FD;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}

/* Glassmorphism Metric Cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #131D33, #0E1626);
    border: 1px solid #1E2D4A;
    border-radius: 12px;
    padding: 14px 18px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    transition: all 0.25s ease-in-out;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #3B82F6;
    box-shadow: 0 6px 22px rgba(59, 130, 246, 0.25);
}
[data-testid="stMetricValue"] { font-size: 1.85rem; color: #F8FAFC; font-weight: 700; }
[data-testid="stMetricLabel"] { color: #94A3B8; font-size: 0.85rem; letter-spacing: 0.02em; }

/* Runway Light Divider */
.runway-divider {
    height: 2px;
    background: repeating-linear-gradient(90deg, #3B82F6 0, #3B82F6 14px, transparent 14px, transparent 24px);
    margin: 14px 0 18px 0;
    opacity: 0.45;
}

.eyebrow { font-size: 11px; letter-spacing: .15em; color: #818CF8; font-weight: 700; }
.notice { background: #131B2E; border: 1px solid #23304B; padding: 9px 14px; border-radius: 8px; color: #94A3B8; font-size: 12px; margin: 8px 0 14px; }
.quote { font-size: 15.5px; line-height: 1.55; color: #F1F5F9; margin: 10px 0; font-weight: 450; }
.badge { display: inline-block; padding: 4px 9px; border-radius: 6px; background: #17243F; border: 1px solid #26385C; color: #93C5FD; font-size: 11px; margin: 0 4px 6px 0; }
.footer { font-size: 11px; color: #64748B; border-top: 1px solid #1E2D4A; padding-top: 12px; margin-top: 16px; }
</style>''', unsafe_allow_html=True)

# ----------------- SIDEBAR CONFIGURATION -----------------
with st.sidebar:
    st.markdown("### ✈️ IndiGo PR Intelligence")
    st.caption("Aviation Social Listening & Crisis Control")
    st.markdown('<div class="runway-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("### ⚙️ GenAI & RAG Engine")
    default_key = os.environ.get("GEMINI_API_KEY", "")
    try:
        if not default_key and "GEMINI_API_KEY" in st.secrets:
            default_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
        
    api_key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state.get("gemini_api_key", default_key),
        type="password",
        help="Free key from Google AI Studio (aistudio.google.com). Automatic text model auto-discovery enabled."
    )
    if api_key_input:
        st.session_state.gemini_api_key = api_key_input
        st.success("🟢 Gemini API connected (Auto-RAG Active)")
    else:
        st.session_state.gemini_api_key = ""
        st.info("⚪ Offline prototype mode active (using cached playbook drafts)")
        
    st.markdown(f"**Indexed Playbook Rules:** `{len(PLAYBOOK_RULES)}`")
    st.caption("Grounding Source: *IndiGo Crisis Management Playbook Expanded*")
    st.markdown('<div class="runway-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("### 🛡️ Non-Negotiable Governance")
    st.caption("• **Rule 01.04**: AI drafts; human approves before publishing\n• **Rule 02.04**: PNR & personal data masked\n• **Rule 10.04**: Zero unverified refund/departure promises")

# ----------------- DATA & MOCK RECORDS -----------------
RAW = [
    ("IG01","@demo_traveller01","My flight was cancelled and I’m still waiting for a clear update. The queues keep growing and nobody knows what happens next.","English","Negative","Cancellations","High","High",True,"Cancellation complaint with unclear updates and reported queues. High spread is manually assigned for this demo."),
    ("IG02","@demo_traveller02","Three hours delayed. Could someone tell us when the next update is coming?","English","Negative","Delays","Medium","Medium",False,"Request for a clear delay update; route to passenger support."),
    ("IG03","@demo_traveller03","My refund is still pending. How can I check its status?","English","Negative","Refunds","Medium","Low",False,"Booking-specific refund query; do not make an eligibility or timing promise."),
    ("IG04","@demo_traveller04","Waah IndiGo, airport pe hi vacation karwa diya. Ab ghar kab jayenge?","Hinglish","Negative","Delays","Medium","Medium",False,"Sarcastic praise interpreted as dissatisfaction in this manually labelled example."),
    ("IG05","@demo_traveller05","Smooth flight and a helpful crew today. Thank you!","English","Positive","Customer service","Low","Low",False,"Routine positive feedback; no crisis escalation assigned."),
    ("IG06","@demo_traveller06","My bag has not arrived. Where do I report this?","English","Negative","Baggage","Medium","Low",False,"Missing-baggage support request."),
    ("IG07","@demo_traveller07","Multiple cancellations and conflicting messages at the airport. Please give passengers one clear update.","English","Negative","Cancellations","High","High",True,"Repeated cancellations and inconsistent information; illustrative PR escalation."),
    ("IG08","@demo_traveller08","Flight status kahan check kar sakte hain?","Hinglish","Neutral","Customer service","Low","Low",False,"General information request."),
    ("IG09","@demo_traveller09","Support team ne patiently meri baat suni. Thanks for helping.","Hinglish","Positive","Customer service","Low","Low",False,"Positive service experience."),
    ("IG10","@demo_traveller10","The baggage desk keeps redirecting me. I still need help locating my bag.","English","Negative","Baggage","Medium","Medium",False,"Unresolved baggage complaint needing a support handoff."),
    ("IG11","@demo_traveller11","Cancellation ke baad refund process samajh nahi aa raha. Please guide.","Hinglish","Negative","Refunds","Medium","Low",False,"Request for refund process guidance; consult verified policy before responding."),
    ("IG12","@demo_traveller12","Our flight was cancelled and an elderly passenger here needs assistance. Please connect us with ground staff.","English","Negative","Cancellations","High","Low",True,"Urgent assistance request warrants review despite low illustrative spread."),
]
COLS=["ID","Handle","Mention","Language","Sentiment","Topic","Urgency","Spread","Alert","Rationale"]
data=pd.DataFrame(RAW,columns=COLS)

DEFAULT_DRAFT="We’re sorry for the uncertainty and inconvenience. Please contact our verified support channel for assistance with your booking, and avoid sharing booking details publicly."
PLAYBOOK="Acknowledge the passenger’s concern. Ask them to use the airline’s verified support channel for booking-specific assistance. Do not request booking details publicly. Do not promise refunds, compensation, departure times or resolution deadlines without verified information."

def initial_draft(row):
    if row.Sentiment=="Positive": return "Thank you for sharing your experience. We’re glad to hear your journey went well."
    if row.Sentiment=="Neutral": return "Please use the airline’s official website or verified support channel for flight-specific information. Avoid sharing booking details publicly."
    if row.Topic=="Refunds": return "We’re sorry you’re waiting for an update. Please contact our verified support channel to check your booking-specific refund status, and avoid sharing booking details publicly."
    if row.Topic=="Baggage": return "We’re sorry for the inconvenience with your baggage. Please contact our verified support channel for assistance, and avoid sharing baggage tags or booking details publicly."
    return DEFAULT_DRAFT

if "reviews" not in st.session_state: st.session_state.reviews={}
if "drafts" not in st.session_state: st.session_state.drafts={r.ID:initial_draft(r) for r in data.itertuples()}
if "retrieved_rules" not in st.session_state: st.session_state.retrieved_rules={}

def reset_filters():
    for key in ["topic","sentiment","urgency"]:st.session_state[key]="All"

def review(post_id, action):
    value=st.session_state.get("editor_"+post_id,st.session_state.drafts[post_id])
    if not value.strip() and action!="Rejected":
        st.session_state.flash="Enter a response before saving or approving."
        return
    st.session_state.drafts[post_id]=value
    st.session_state.reviews[post_id]=action
    st.session_state.flash=("Draft approved in demo workspace. Nothing was published." if action=="Approved" else "Draft rejected in demo workspace. Nothing was published." if action=="Rejected" else "Edits saved in this demo session. Draft still awaits approval.")

# ----------------- HEADER & CONTROLS -----------------
st.markdown('<div class="eyebrow">INDIGO OPERATIONS • AI PR INTELLIGENCE & CRISIS CONTROL</div>', unsafe_allow_html=True)
st.markdown('<h1><span class="jet-icon">✈️</span>Navigating Turbulence: AI Crisis Radar & Response Copilot</h1>', unsafe_allow_html=True)
st.caption("Early Virality Forecasting • Crisis Playbook RAG • Human-in-the-Loop Governance")
st.markdown('<div class="notice">Educational UI prototype • Grounded in team-authored Crisis Playbook (112 rules) • Human sign-off required before release • Not affiliated with IndiGo</div>', unsafe_allow_html=True)

# Filters
f1,f2,f3,f4=st.columns([2,2,2,1])
with f1: topic=st.selectbox("Topic",["All"]+sorted(data.Topic.unique()),key="topic")
with f2: sentiment=st.selectbox("Sentiment",["All","Negative","Neutral","Positive"],key="sentiment")
with f3: urgency=st.selectbox("Urgency",["All","High","Medium","Low"],key="urgency")
with f4:
    st.write("")
    st.button("Reset filters",on_click=reset_filters,width="stretch")

filtered=data.copy()
for col,v in [("Topic",topic),("Sentiment",sentiment),("Urgency",urgency)]:
    if v!="All":filtered=filtered[filtered[col]==v]

# Executive Metrics Row
metrics=st.columns(4)
counts=[len(filtered),int((filtered.Sentiment=="Negative").sum()),int(filtered.Alert.sum()),sum(st.session_state.reviews.get(i,"Pending") not in ["Approved","Rejected"] for i in filtered.ID)]
for c,label,n in zip(metrics,["Mentions in Radar","Negative Mentions","Active Crisis Alerts (Radar)","Drafts Awaiting Review"],counts):c.metric(label,n)

st.markdown('<div class="runway-divider"></div>', unsafe_allow_html=True)

# ----------------- DUAL-PANE WORKSPACE -----------------
left,right=st.columns([1.15,1],gap="large")

with left:
    st.subheader("✈️ Mentions Queue (Flight Radar)")
    if filtered.empty:
        st.info("No flight mentions match these filters. Reset filters to continue.")
    else:
        view=filtered[["ID","Mention","Sentiment","Topic","Urgency","Spread"]].copy()
        view["Review"]=view.ID.map(lambda x:st.session_state.reviews.get(x,"Pending"))
        st.dataframe(view,hide_index=True,width="stretch",height=310,column_config={"Mention":st.column_config.TextColumn("Mention",width="large"),"Spread":st.column_config.TextColumn("Virality Risk")})
        
        selected=st.selectbox("Select mention to review:",filtered.ID.tolist(),format_func=lambda x:f"{x} · {data.set_index('ID').loc[x,'Topic']} · {data.set_index('ID').loc[x,'Language']}",key="selected_"+"_".join(filtered.ID))
        st.caption("Boarding gate view: select any post to inspect risk rationale, retrieve playbook articles, and verify draft.")

    # Audit Trail Export Button for Compliance
    reviewed_count = sum(st.session_state.reviews.get(i,"Pending") != "Pending" for i in data.ID)
    if reviewed_count > 0:
        audit_records = []
        for r in data.itertuples():
            status = st.session_state.reviews.get(r.ID, "Pending")
            audit_records.append({
                "Post_ID": r.ID,
                "Handle": r.Handle,
                "Topic": r.Topic,
                "Sentiment": r.Sentiment,
                "Review_Status": status,
                "Final_Approved_Draft": st.session_state.drafts.get(r.ID, "")
            })
        audit_df = pd.DataFrame(audit_records)
        csv_buffer = io.StringIO()
        audit_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Export PR Governance Audit Trail (CSV)",
            data=csv_buffer.getvalue(),
            file_name="indigo_pr_governance_audit.csv",
            mime="text/csv",
            help="Download the complete human-in-the-loop review decisions for compliance reporting."
        )

    # Audience Interactive Custom Tweet Tester
    with st.expander("✍️ Live Audience Simulation: Test Any Custom Flight Tweet"):
        st.caption("Simulate an incoming tweet from the presentation audience or a live passenger:")
        custom_input = st.text_area("Custom Passenger Post:", placeholder="e.g. IndiGo flight 6E-204 delayed by 5 hours at Mumbai, elderly passenger requires medical assistance and water!", key="custom_tweet_text")
        if st.button("⚡ Evaluate & Draft with Gemini (RAG)", key="btn_run_custom"):
            api_key = st.session_state.get("gemini_api_key", "")
            if not api_key:
                st.warning("Please enter your Gemini API Key in the left sidebar to generate live responses.")
            elif not custom_input.strip():
                st.info("Please enter some text in the custom mention box above.")
            else:
                with st.spinner("Searching Crisis Playbook rules and generating response..."):
                    c_draft, c_rules = generate_rag_draft(custom_input, "Custom", api_key)
                    if any(c_draft.startswith(err) for err in ["Gemini API Error", "OpenAI API Error", "Network Connection Error", "Error"]):
                        st.error(c_draft)
                    else:
                        st.markdown("**AI Response Draft (Grounded in Playbook):**")
                        st.info(c_draft)
                        st.markdown("**Retrieved Playbook Rules Enforced:**")
                        for r in c_rules:
                            st.caption(f"• **Rule {r['code']} ({r['title']})**: {r['body']}")

with right:
    st.subheader("🛡️ Response & Governance Review")
    if filtered.empty:
        st.caption("Select a matching mention to begin.")
    else:
        row=data[data.ID==selected].iloc[0]
        with st.container(border=True):
            st.markdown(f'<div class="boarding-pass-badge">🎫 FLIGHT CASE {row["ID"]} • {row.Handle} • {row.Language}</div>', unsafe_allow_html=True)
            st.markdown('<div class="quote">'+html.escape(row.Mention)+'</div>',unsafe_allow_html=True)
            st.markdown(''.join('<span class="badge">'+html.escape(v)+'</span>' for v in [row.Sentiment,row.Topic,row.Urgency+" urgency",row.Spread+" spread risk"]),unsafe_allow_html=True)
            
            # Pulsing radar alert box if crisis
            if row.Alert:
                st.markdown('<div class="alert-radar"><b>🚨 CRITICAL PR ALERT • Radar Escalation Triggered</b><br>'+html.escape(row.Rationale)+'</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-standard"><b>ℹ️ Review Rationale</b><br>'+html.escape(row.Rationale)+'</div>', unsafe_allow_html=True)
            
            # Live RAG Generation Controls
            col_rag_btn, col_rag_status = st.columns([1.5, 1])
            with col_rag_btn:
                if st.button("⚡ Generate with Gemini (RAG)", key="btn_rag_"+selected, help="Retrieves matching rules from the team's crisis playbook and drafts an AI response"):
                    api_key = st.session_state.get("gemini_api_key", "")
                    if not api_key:
                        st.warning("Please enter your Gemini API Key in the sidebar for live generation.")
                    else:
                        with st.spinner("Retrieving playbook rules & drafting with Gemini..."):
                            new_draft, rules_used = generate_rag_draft(row.Mention, row.Topic, api_key)
                            if any(new_draft.startswith(err) for err in ["Gemini API Error", "OpenAI API Error", "Network Connection Error", "Error"]):
                                st.session_state.flash = new_draft
                            else:
                                editor_key = "editor_" + selected
                                st.session_state[editor_key] = new_draft
                                st.session_state.drafts[selected] = new_draft
                                st.session_state.retrieved_rules[selected] = rules_used
                                st.session_state.flash = "Generated fresh draft grounded in Crisis Playbook rules!"
                            st.rerun()
                            
            with col_rag_status:
                if st.session_state.get("gemini_api_key"):
                    st.caption("🟢 Live Gemini RAG Ready")
                else:
                    st.caption("⚪ Curated Playbook Draft")

            editor="editor_"+selected
            if editor not in st.session_state:st.session_state[editor]=st.session_state.drafts[selected]
            st.text_area("Response draft (Human Editable):",key=editor,height=100)

            # Show retrieved RAG rules
            active_rules = st.session_state.retrieved_rules.get(selected, retrieve_rules(row.Mention, row.Topic, top_k=2))
            with st.expander(f"📚 RAG Retrieved Playbook Rules ({len(active_rules)} rules cited)"):
                st.caption("These exact rules from your team's Crisis Playbook constrain the AI response:")
                for r in active_rules:
                    st.markdown(f"**Rule {r.get('code')}: {r.get('title')}**\n\n> {r.get('body')}")

            with st.expander("Supporting guidance · Team-authored sample"):
                st.caption("Proposed team playbook — illustrative, not official IndiGo policy.")
                st.write(PLAYBOOK)

            b1,b2,b3=st.columns(3)
            b1.button("Approve draft",type="primary",width="stretch",on_click=review,args=(selected,"Approved"))
            b2.button("Save edits",width="stretch",on_click=review,args=(selected,"Edited"))
            b3.button("Reject draft",width="stretch",on_click=review,args=(selected,"Rejected"))
            if "flash" in st.session_state:st.info(st.session_state.pop("flash"))
            
            review_status = st.session_state.reviews.get(selected, "Pending")
            st.caption(f"Status: **{review_status}** • Changes logged to audit trail.")

st.markdown('<div class="footer">Human approval required before any external response. Classification, virality labels and response drafts are illustrative. Grounded in IndiGo Crisis Management Playbook.</div>',unsafe_allow_html=True)
