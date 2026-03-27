import streamlit as st
import socket
import requests
import ssl
import re
import sqlite3
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from fpdf import FPDF
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# ===== Streamlit Page Config =====
st.set_page_config(layout="wide", page_title="POLAVIC CYBER AI PRO")

# ===== Database Setup =====
conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS scans(
    domain TEXT, result TEXT, time TEXT
)
""")
conn.commit()

# ===== UI STYLE =====
st.markdown("""
<style>
.stApp { font-family: monospace; }
.card { background: rgba(0,255,204,0.08); border:1px solid #00ffcc; border-radius:15px; padding:20px; margin:10px; text-align:center; backdrop-filter:blur(10px); transition:0.3s;}
.card:hover { transform:scale(1.07); box-shadow:0 0 30px #00ffcc;}
.row { display:flex; justify-content:space-around; flex-wrap:wrap;}
.stButton>button { background-color:#00ffcc; color:black; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ POLAVIC CYBER AI PRO")

# ===== Sidebar Navigation =====
menu = st.sidebar.radio("Navigation", ["Scan", "History"])
theme = st.sidebar.radio("Theme", ["Dark", "Light"])

# ===== Domain Validation =====
def valid_domain(domain):
    return re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", domain) or re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain)

# ===== Multi-threaded Port Scan =====
def check_port(domain, port, timeout=1):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((domain, port))
        return port
    except:
        return None
    finally:
        s.close()

def check_ports(domain, ports=[21,22,80,443,8080], timeout=1):
    open_ports = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_port = {executor.submit(check_port, domain, p, timeout): p for p in ports}
        for future in as_completed(future_to_port):
            result = future.result()
            if result: open_ports.append(result)
    return open_ports

# ===== Scan Function =====
def scan(domain):
    # Resolve IP
    try:
        ip = socket.gethostbyname(domain)
    except socket.gaierror:
        ip = "Unknown"

    # Geo Info
    try:
        api = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
    except:
        api = {}

    # HTTP(S) Request
    status_code = "No Response"
    title = "No Title"
    headers = {}
    urls = [f"https://{domain}", f"http://{domain}"]
    for url in urls:
        try:
            res = requests.get(url, timeout=5)
            status_code = res.status_code
            soup = BeautifulSoup(res.text,"html.parser")
            title = soup.title.string if soup.title else "No Title"
            headers = dict(res.headers)
            break
        except:
            continue

    # SSL Check
    ssl_status = "Not Secure"
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain,443))
        ssl_status = "Secure"
    except:
        ssl_status = "Not Secure"

    # Ports
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

# ===== Risk Score =====
def risk(data):
    score = 0
    if data["ssl"]=="Not Secure": score+=40
    if data["status"] !=200: score+=30
    if len(data["ports"])>2: score+=20
    if "login" in data["title"].lower(): score+=10
    return min(score,100)

# ===== AI Analysis =====
def ai_analysis(data):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        content = f"Analyze this website scan result for cybersecurity issues: {data}. Provide vulnerabilities, suggestions and risk assessment."
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a cybersecurity expert."},
                {"role":"user","content":content}
            ]
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"AI analysis unavailable: {str(e)}"

# ===== PDF Report =====
def generate_pdf(domain,data,ai_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"POLAVIC CYBER SCAN REPORT",ln=True,align='C')
    pdf.set_font("Arial",size=12)
    pdf.ln(5)
    for key in ["Domain","IP","City","Country","Status","SSL","Title","Open Ports"]:
        val = data.get(key.lower()) if key.lower()!="open ports" else data["ports"]
        pdf.multi_cell(0,8,f"{key}: {val}")
    pdf.ln(5)
    pdf.multi_cell(0,8,"AI Analysis:\n"+ai_text)
    pdf.output("report.pdf")

# ===== Session State =====
if "scan_result" not in st.session_state: st.session_state.scan_result=None
if "ai_text" not in st.session_state: st.session_state.ai_text=None

# ===== Scan Page =====
if menu=="Scan":
    domain = st.text_input("Enter Domain (without http:// or https://)")
    if st.button("Scan Now"):
        if not valid_domain(domain):
            st.error("Invalid domain or IP")
        else:
            # Real-time scanning messages
            status_text = st.empty()
            steps = ["Initializing...", "Scanning Ports...", "Fetching Data...", "AI Analysis..."]
            for s in steps:
                status_text.text(s)
                time.sleep(0.5)

            data = scan(domain)
            st.session_state.scan_result = (domain,data)

            # Save to DB
            c.execute("INSERT INTO scans VALUES (?,?,datetime('now'))",(domain,str(data)))
            conn.commit()

            # UI Cards
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
            """,unsafe_allow_html=True)

            # Risk Score
            score = risk(data)
            st.subheader("⚠️ Risk Score")
            st.progress(score)

            # Chart
            fig,ax=plt.subplots()
            fig.patch.set_facecolor('#121212' if theme=="Dark" else 'white')
            ax.set_facecolor('#121212' if theme=="Dark" else 'white')
            ax.bar(["Risk"],[score],color='#00ffcc')
            ax.tick_params(colors='#00ffcc' if theme=="Dark" else 'black')
            st.pyplot(fig)

            # Headers
            st.subheader("📡 Headers")
            st.json(data["headers"])

            # AI Analysis
            st.subheader("🤖 AI Analysis")
            ai_text=ai_analysis(data)
            st.session_state.ai_text=ai_text
            st.text(ai_text)

    # PDF Download
    if st.session_state.scan_result and st.session_state.ai_text:
        domain,data=st.session_state.scan_result
        ai_text=st.session_state.ai_text
        generate_pdf(domain,data,ai_text)
        with open("report.pdf","rb") as f:
            st.download_button("📄 Download POLAVIC Report",f,file_name="report.pdf")

# ===== History Page =====
elif menu=="History":
    st.subheader("Scan History")
    c.execute("SELECT * FROM scans ORDER BY time DESC")
    rows=c.fetchall()
    for r in rows: st.write(r)
    if st.button("Clear History"):
        c.execute("DELETE FROM scans")
        conn.commit()
        st.success("History Cleared")
