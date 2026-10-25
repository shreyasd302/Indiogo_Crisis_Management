"""Educational UI only. No live feeds, models, retrieval, or publishing."""
import html
import pandas as pd
import streamlit as st

st.set_page_config(page_title="IndiGo | PR review workspace", page_icon="✈", layout="wide")
st.markdown('''<style>
.block-container{padding-top:1.6rem;padding-bottom:1rem;max-width:1500px}
h1{font-size:2rem!important;letter-spacing:-.045em;color:#102454}h3{font-size:1.05rem!important;color:#102454}
[data-testid="stMetric"]{background:#f4f7fc;border:1px solid #e1e7f2;border-radius:12px;padding:12px 18px}
[data-testid="stMetricValue"]{font-size:1.8rem;color:#102454}
[data-testid="stMetricLabel"]{color:#52627d;font-size:.85rem}
.notice{background:#edf2fa;border:1px solid #dae3f3;padding:9px 14px;border-radius:8px;color:#3d5376;font-size:12px;margin:8px 0 16px}
.eyebrow{font-size:11px;letter-spacing:.13em;color:#526789;font-weight:700}
.quote{font-size:16px;line-height:1.5;color:#18294a;margin:12px 0}
.badge{display:inline-block;padding:4px 9px;border-radius:6px;background:#edf1f8;color:#27416e;font-size:11px;margin:0 4px 6px 0}
.alert{background:#fff3e8;border-left:3px solid #d9822b;padding:9px 12px;font-size:12px;line-height:1.5;margin:8px 0}
.footer{font-size:11px;color:#66758c;border-top:1px solid #e1e7f2;padding-top:10px;margin-top:12px}
</style>''', unsafe_allow_html=True)

# All records and annotations are invented for this demonstration.
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

st.markdown('<div class="eyebrow">INDIGO CASE STUDY / PR OPERATIONS</div>',unsafe_allow_html=True)
st.title("Social Listening and Crisis Response")
st.caption("PR review workspace · Fictional sample mentions · Demo data")
st.markdown('<div class="notice">Educational UI prototype • Illustrative data • No live monitoring or AI models connected • Not affiliated with IndiGo</div>',unsafe_allow_html=True)
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
metrics=st.columns(4)
counts=[len(filtered),int((filtered.Sentiment=="Negative").sum()),int(filtered.Alert.sum()),sum(st.session_state.reviews.get(i,"Pending") not in ["Approved","Rejected"] for i in filtered.ID)]
for c,label,n in zip(metrics,["Demo mentions in view","Negative mentions","Illustrative crisis alerts","Drafts awaiting review"],counts):c.metric(label,n)
st.caption("Demo summaries reflect current filters. Spread categories and alert flags are manually assigned.")
left,right=st.columns([1.15,1],gap="large")
with left:
    st.subheader("Mentions queue")
    if filtered.empty:
        st.info("No demo mentions match these filters. Reset filters to continue.")
    else:
        view=filtered[["ID","Mention","Sentiment","Topic","Urgency","Spread"]].copy()
        view["Review"]=view.ID.map(lambda x:st.session_state.reviews.get(x,"Pending"))
        st.dataframe(view,hide_index=True,width="stretch",height=335,column_config={"Mention":st.column_config.TextColumn("Mention",width="large"),"Spread":st.column_config.TextColumn("Demo spread")})
        st.caption("Choose a post below to inspect its full mention and review its draft.")
        selected=st.selectbox("Select mention",filtered.ID.tolist(),format_func=lambda x:x+" · "+data.set_index("ID").loc[x,"Topic"],key="selected_"+"_".join(filtered.ID))
        st.caption("Session only: review decisions reset when the app session ends. No external actions are taken.")
with right:
    st.subheader("Response review")
    if filtered.empty:
        st.caption("Select a matching mention to begin.")
    else:
        row=data[data.ID==selected].iloc[0]
        with st.container(border=True):
            st.caption(f"{row['ID']} · {row.Handle} · {row.Language} · Fictional mention")
            st.markdown('<div class="quote">'+html.escape(row.Mention)+'</div>',unsafe_allow_html=True)
            st.markdown(''.join('<span class="badge">'+html.escape(v)+'</span>' for v in [row.Sentiment,row.Topic,row.Urgency+" urgency",row.Spread+" demo spread"]),unsafe_allow_html=True)
            st.markdown('<div class="alert"><b>Demo '+('crisis alert' if row.Alert else 'review rationale')+' · Manually assigned</b><br>'+html.escape(row.Rationale)+'</div>',unsafe_allow_html=True)
            st.caption("Static sample draft — no LLM or retrieval connected")
            editor="editor_"+selected
            if editor not in st.session_state:st.session_state[editor]=st.session_state.drafts[selected]
            st.text_area("Response draft",key=editor,height=110)
            with st.expander("Supporting guidance · Team-authored sample"):
                st.caption("Proposed team playbook — illustrative, not official IndiGo policy.")
                st.write(PLAYBOOK)
            b1,b2,b3=st.columns(3)
            b1.button("Approve draft",type="primary",width="stretch",on_click=review,args=(selected,"Approved"))
            b2.button("Save edits",width="stretch",on_click=review,args=(selected,"Edited"))
            b3.button("Reject draft",width="stretch",on_click=review,args=(selected,"Rejected"))
            if "flash" in st.session_state:st.info(st.session_state.pop("flash"))
            st.caption("Review status: "+st.session_state.reviews.get(selected,"Pending"))
st.markdown('<div class="footer">Human approval required before any external response. Classification, spread labels and response drafts are illustrative. This UI does not reproduce the project’s model evaluation results.</div>',unsafe_allow_html=True)
