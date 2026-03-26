import streamlit as st
import socket
import requests
import ssl
import time
import re
import sqlite3
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

st.set_page_config(layout="wide", page_title="CYBER AI PRO")

# ===== DATABASE =====
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS scans(domain TEXT, result TEXT, time TEXT)")
conn.commit()

# ===== UI STYLE =====
st.markdown("""
<style>
@keyframes bgmove {
  0% {background-position:0%}
  100% {background-position:100%}
}
.stApp {
    background: linear-gradient(270deg,#000000,#001f1f,#000000);
    background-size:400% 400%;
    animation:bgmove 12s infinite alternate;
    color:#00ffcc;
    font-family:monospace;
}

.card {
    background:rgba(0,255,204,0.08);
    border:1px solid #00ffcc;
    border-radius:15px;
    padding:20px;
    margin:10px;
    text-align:center;
    backdrop-filter:blur(10px);
    transition:0.3s;
}
.card:hover {
    transform:scale(1.07);
    box-shadow:0 0 30px #00ffcc;
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

st.title("🛡️ CYBER AI PRO DASHBOARD")

menu = st.sidebar.radio("Navigation", ["Scan", "History"])

# ===== VALID DOMAIN =====
def valid_domain(domain):
    return re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", domain)

# ===== PORT SCAN =====
def check_ports(domain):
    ports = [21,22,80,443,8080]
    open_ports = []
    for p in ports:
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect((domain,p))
            open_ports.append(p)
        except:
            pass
        s.close()
    return open_ports

# ===== SCAN =====
def scan(domain):
    try:
        ip = socket.gethostbyname(domain)
    except:
        ip = "Unknown"

    try:
        api = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
    except:
        api = {}

    try:
        res = requests.get(f"http://{domain}", timeout=5)
        status_code = res.status_code
        soup = BeautifulSoup(res.text,"html.parser")
        title = soup.title.string if soup.title else "No Title"
        headers = dict(res.headers)
    except:
        status_code = "No Response"
        title = "No Title"
        headers = {}

    ssl_status = "Secure"
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain,443))
    except:
        ssl_status = "Not Secure"

    ports = check_ports(domain)

    return {
        "ip": ip,
        "city": api.get("city"),
        "country": api.get("country"),
        "status": status_code,
        "ssl": ssl_status,
        "title": title,
        "headers": headers,
        "ports": ports
    }

# ===== RISK =====
def risk(data):
    score = 0
    if data["ssl"] == "Not Secure":
        score += 40
    if data["status"] != 200:
        score += 30
    if len(data["ports"]) > 2:
        score += 20
    if "login" in data["title"].lower():
        score += 10
    return min(score,100)

# ===== SESSION STATE =====
if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

# ===== SCAN PAGE =====
if menu == "Scan":
    domain = st.text_input("Enter Domain (without http://)")
    if st.button("Scan Now"):
        if not valid_domain(domain):
            st.error("Invalid domain")
        else:
            term = st.empty()
            for t in ["Initializing...", "Scanning Ports...", "Fetching Data..."]:
                term.text(t)
                time.sleep(0.5)

            data = scan(domain)
            st.session_state.scan_result = (domain, data)

            # Save to DB
            c.execute("INSERT INTO scans VALUES (?,?,datetime('now'))",(domain,str(data)))
            conn.commit()

            # ===== UI CARDS =====
            st.markdown(f"""
            <div class="row">
            <div class="card"><h3>IP</h3>{data['ip']}</div>
            <div class="card"><h3>Status</h3>{data['status']}</div>
            <div class="card"><h3>SSL</h3>{data['ssl']}</div>
            </div>

            <div class="row">
            <div class="card"><h3>Country</h3>{data['country']}</div>
            <div class="card"><h3>City</h3>{data['city']}</div>
            <div class="card"><h3>Ports</h3>{data['ports']}</div>
            </div>

            <div class="card"><h3>Title</h3>{data['title']}</div>
            """, unsafe_allow_html=True)

            # Risk
            score = risk(data)
            st.subheader("⚠️ Risk Score")
            st.progress(score)

            # Chart
            fig, ax = plt.subplots()
            fig.patch.set_facecolor('black')
            ax.set_facecolor('black')
            ax.bar(["Risk"], [score], color='#00ffcc')
            ax.tick_params(colors='#00ffcc')
            st.pyplot(fig)

            # Headers
            st.subheader("📡 Headers")
            st.json(data["headers"])

# ===== HISTORY PAGE =====
elif menu == "History":
    st.subheader("Scan History")
    c.execute("SELECT * FROM scans ORDER BY time DESC")
    rows = c.fetchall()
    for r in rows:
        st.write(r)

    if st.button("Clear History"):
        c.execute("DELETE FROM scans")
        conn.commit()
        st.success("History Cleared")
