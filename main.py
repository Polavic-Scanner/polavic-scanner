import streamlit as st
import socket
import requests
import ssl
import time
import matplotlib.pyplot as plt
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

st.set_page_config(layout="wide")

# ================= UI =================
st.markdown("""
<style>
.stApp {
    background: black;
    color: #00ffcc;
    font-family: monospace;
}
h1 {
    text-align:center;
    text-shadow:0 0 20px #00ffcc;
}
.card {
    background: rgba(0,255,204,0.05);
    border:1px solid #00ffcc;
    border-radius:15px;
    padding:20px;
    margin:10px;
    text-align:center;
    transition:0.3s;
}
.card:hover {
    transform:scale(1.05);
    box-shadow:0 0 40px #00ffcc;
}
.row {
    display:flex;
    justify-content:space-around;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ POLAVIC CYBER AI SCANNER")

# ================= SCAN =================
def scan(domain):
    ip = socket.gethostbyname(domain)
    api = requests.get(f"http://ip-api.com/json/{ip}").json()
    res = requests.get(f"http://{domain}")

    ssl_status = "Secure"
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain,443))
    except:
        ssl_status = "Not Secure"

    return {
        "ip": ip,
        "city": api.get("city"),
        "country": api.get("country"),
        "isp": api.get("isp"),
        "status": res.status_code,
        "ssl": ssl_status
    }

# ================= AI =================
def ai_analysis(data):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a cybersecurity expert."},
                {"role":"user","content":f"Analyze this data:\n{data}"}
            ]
        )
        return res.choices[0].message.content
    except:
        return "AI unavailable (API issue)"

# ================= RISK =================
def risk_score(data):
    score = 0
    if data["ssl"] == "Not Secure":
        score += 40
    if data["status"] != 200:
        score += 30
    return min(score,100)

# ================= PDF =================
def make_pdf(text):
    file="report.pdf"
    doc=SimpleDocTemplate(file)
    styles=getSampleStyleSheet()
    doc.build([Paragraph(text, styles["Normal"])])
    return file

# ================= UI =================
domain = st.text_input("🌐 Enter Target Domain")

if st.button("🚀 Scan"):
    if domain:

        # ===== Terminal Effect =====
        terminal = st.empty()
        logs = ["Connecting...", "Fetching IP...", "Checking SSL...", "Analyzing..."]
        for log in logs:
            terminal.text(log)
            time.sleep(0.5)

        data = scan(domain)

        # ===== Cards =====
        st.markdown(f"""
        <div class="row">
        <div class="card"><h3>IP</h3><p>{data['ip']}</p></div>
        <div class="card"><h3>City</h3><p>{data['city']}</p></div>
        <div class="card"><h3>Country</h3><p>{data['country']}</p></div>
        </div>
        <div class="row">
        <div class="card"><h3>ISP</h3><p>{data['isp']}</p></div>
        <div class="card"><h3>Status</h3><p>{data['status']}</p></div>
        <div class="card"><h3>SSL</h3><p>{data['ssl']}</p></div>
        </div>
        """, unsafe_allow_html=True)

        # ===== Risk =====
        score = risk_score(data)
        st.subheader("⚠️ Risk Score")
        st.progress(score)

        # ===== Chart =====
        fig, ax = plt.subplots()
        ax.bar(["Risk"], [score])
        st.pyplot(fig)

        # ===== AI =====
        st.subheader("🤖 AI Analysis")
        ai = ai_analysis(data)
        st.write(ai)

        # ===== PDF =====
        pdf = make_pdf(str(data)+"\n\n"+ai)
        with open(pdf,"rb") as f:
            st.download_button("📄 Download Report", f, file_name="report.pdf")

    else:
        st.warning("Enter domain")
