import streamlit as st
import socket
import requests
import ssl
import time
import re
import sqlite3
import matplotlib.pyplot as plt
from openai import OpenAI

st.set_page_config(layout="wide", page_title="POLAVIC CYBER AI DASHBOARD")

# ================= DB =================
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS scans(domain TEXT, result TEXT, time TEXT)")
conn.commit()

# ================= Live Cyber Background =================
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #00ffcc;
    font-family: monospace;
}
@keyframes gradientBG {
    0%{background-position:0% 50%}
    50%{background-position:100% 50%}
    100%{background-position:0% 50%}
}
.card {
    background: rgba(0,255,204,0.15);
    border:1px solid #00ffcc;
    border-radius:15px;
    padding:20px;
    margin:10px;
    text-align:center;
    transition: transform 0.3s, box-shadow 0.3s;
}
.card:hover {
    transform:scale(1.07);
    box-shadow:0 0 40px #00ffcc;
}
.row {
    display:flex;
    justify-content:space-around;
    flex-wrap:wrap;
}
.stButton>button {
    background-color:#00ffcc;
    color:black;
    font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ POLAVIC CYBER AI DASHBOARD")

# ================= Sidebar =================
menu = st.sidebar.radio("📂 Navigation", ["Scan", "History", "Dashboard"])

# ================= Validation =================
def valid_domain(domain):
    return re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", domain)

# ================= Scan =================
def scan(domain):
    try:
        ip = socket.gethostbyname(domain)
        api = requests.get(f"http://ip-api.com/json/{ip}").json()
    except:
        ip = "Unknown"
        api = {}
    try:
        res = requests.get(f"http://{domain}", timeout=3)
        status_code = res.status_code
    except:
        status_code = "No Response"

    ssl_status = "Secure"
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain,443))
    except:
        ssl_status = "Not Secure"

    return {
        "ip": ip,
        "city": api.get("city"),
        "country": api.get("country"),
        "isp": api.get("isp"),
        "status": status_code,
        "ssl": ssl_status
    }

# ================= AI =================
def ai_analysis(data):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"Cybersecurity expert"},
                {"role":"user","content":f"Analyze:\n{data}"}
            ]
        )
        return res.choices[0].message.content
    except:
        return "AI unavailable"

# ================= Risk =================
def risk_score(data):
    score = 0
    if data["ssl"] == "Not Secure":
        score += 40
    if data["status"] != 200:
        score += 30
    return min(score,100)

# ================= Scan Page =================
if menu == "Scan":
    domain = st.text_input("🌐 Enter Domain")
    if st.button("🚀 Scan"):
        if not valid_domain(domain):
            st.error("Invalid domain")
        else:
            with st.spinner("Connecting..."):
                time.sleep(0.5)
            with st.spinner("Scanning..."):
                time.sleep(0.5)
            with st.spinner("Analyzing..."):
                time.sleep(0.5)

            data = scan(domain)

            # Save to DB
            c.execute("INSERT INTO scans VALUES (?,?,datetime('now'))",(domain,str(data)))
            conn.commit()

            # UI Cards
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

            # Risk
            score = risk_score(data)
            st.subheader("⚠️ Risk Score")
            st.progress(score)

            # Chart
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('none')
            ax.set_facecolor('none')
            ax.bar(["Risk"], [score], color='#00ffcc')
            ax.tick_params(colors='#00ffcc')
            st.pyplot(fig)

            # AI
            st.subheader("🤖 AI Analysis")
            st.write(ai_analysis(data))

# ================= History =================
elif menu == "History":
    st.subheader("📜 Scan History")
    c.execute("SELECT * FROM scans ORDER BY time DESC")
    rows = c.fetchall()
    for r in rows:
        st.write(r)

    if st.button("🗑️ Clear History"):
        c.execute("DELETE FROM scans")
        conn.commit()
        st.success("History Cleared")

# ================= Dashboard =================
elif menu == "Dashboard":
    st.subheader("📊 Overview")
    c.execute("SELECT COUNT(*) FROM scans")
    total = c.fetchone()[0]
    st.metric("Total Scans", total)

    # Timeline Chart
    c.execute("SELECT time FROM scans")
    data = c.fetchall()
    if data:
        fig, ax = plt.subplots()
        ax.set_facecolor('none')
        fig.patch.set_facecolor('none')
        ax.plot(range(len(data)), color='#00ffcc', marker='o')
        ax.tick_params(colors='#00ffcc')
        st.pyplot(fig)
