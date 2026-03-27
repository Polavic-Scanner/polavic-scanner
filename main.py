import streamlit as st
import socket
import requests
import ssl
import re
import sqlite3
import time
import datetime
from bs4 import BeautifulSoup
from fpdf import FPDF
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed

# Optional: plotly import
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

# ===== Streamlit Page Config =====
st.set_page_config(layout="wide", page_title="POLAVIC CYBER AI")

# ===== Database Setup (Error Fixed for Cloud) =====
def get_db_connection():
    conn = sqlite3.connect("data.db", check_same_thread=False)
    return conn

conn = get_db_connection()
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS scans(
    domain TEXT, result TEXT, risk INTEGER, time TEXT
)
""")
conn.commit()

# ===== UI Neon Style =====
st.markdown("""
<style>
@keyframes bgmove {0% {background-position:0%} 100% {background-position:100%}}
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
.card:hover { transform:scale(1.07); box-shadow:0 0 30px #00ffcc;}
.row { display:flex; justify-content:space-around; flex-wrap:wrap;}
.stButton>button { background-color:#00ffcc !important; color:black !important; font-weight:bold !important; width:100%; border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ POLAVIC CYBER AI")

# ===== Sidebar =====
menu = st.sidebar.radio("Navigation", ["Scan", "History"])
theme = st.sidebar.radio("Theme", ["Dark", "Light"])

# ===== Domain Validation =====
def valid_domain(domain):
    return re.match(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", domain) or re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain)

# ===== Multi-threaded Port Scan =====
def check_port(domain, port, timeout=1):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((domain, port))
        if result == 0:
            return port
        return None
    except:
        return None
    finally:
        s.close()

def check_ports(domain, ports=[21,22,80,443,8080], timeout=1):
    open_ports = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_port = {executor.submit(check_port, domain, p, timeout): p for p in ports}
        for future in as_completed(future_to_port):
            res = future.result()
            if res:
                open_ports.append(res)
    return open_ports

# ===== Scan Function (Error Handling Added) =====
def scan(domain):
    try:
        ip = socket.gethostbyname(domain)
    except:
        ip = "Unknown"
    
    try:
        api = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
    except:
        api = {}

    status_code = "No Response"
    title = "No Title"
    headers = {}
    
    # Try HTTPS first, then HTTP
    for proto in ["https://", "http://"]:
        try:
            res = requests.get(f"{proto}{domain}", timeout=5, verify=False)
            status_code = res.status_code
            soup = BeautifulSoup(res.text, "html.parser")
            title = soup.title.string if soup.title else "No Title"
            headers = dict(res.headers)
            break 
        except:
            continue

    ssl_status = "Not Secure"
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with socket.create_connection((domain, 443), timeout=3) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                ssl_status = "Secure"
    except:
        ssl_status = "Not Secure"

    ports = check_ports(domain)
    return {
        "ip": ip,
        "city": api.get("city", "N/A"),
        "country": api.get("country", "N/A"),
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
    if data["status"] != 200: score+=30
    if len(data["ports"])>2: score+=20
    if "login" in str(data["title"]).lower(): score+=10
    return min(score, 100)

# ===== AI Analysis =====
def ai_analysis(data):
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        content = f"Analyze this website scan result: {data}. Provide vulnerabilities, categorize severity as Critical, Medium, Low, and suggestions."
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a cybersecurity expert."},
                {"role":"user","content":content}
            ]
        )
        analysis = res.choices[0].message.content
        severity_lines = []
        for line in analysis.split("\n"):
            if "Critical" in line: severity_lines.append(("🔴 "+line, "red"))
            elif "Medium" in line: severity_lines.append(("🟠 "+line, "orange"))
            elif "Low" in line: severity_lines.append(("🟢 "+line, "green"))
            else: severity_lines.append((line, None))
        return severity_lines
    except Exception as e:
        return [("AI Analysis Error: Check your API Key in Secrets.", "red")]

# ===== PDF Generator =====
def generate_pdf(domain, data, ai_lines):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "POLAVIC CYBER AI NEON REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Domain: {domain}", ln=True)
    pdf.cell(0, 10, f"IP Address: {data['ip']}", ln=True)
    pdf.cell(0, 10, f"Location: {data['city']}, {data['country']}", ln=True)
    pdf.cell(0, 10, f"SSL Status: {data['ssl']}", ln=True)
    pdf.cell(0, 10, f"Open Ports: {data['ports']}", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, "AI Vulnerability Assessment:", ln=True)
    pdf.set_font("Arial", size=10)
    for text, color in ai_lines:
        pdf.multi_cell(0, 7, text.encode('latin-1', 'ignore').decode('latin-1'))
    pdf.output("report.pdf")

# ===== Session State =====
if "scan_result" not in st.session_state: st.session_state.scan_result=None
if "ai_lines" not in st.session_state: st.session_state.ai_lines=None

# ===== Scan Page =====
if menu=="Scan":
    domain_input = st.text_input("Enter Domain (e.g. google.com)")
    if st.button("INITIATE NEON SCAN"):
        if not valid_domain(domain_input):
            st.error("❌ Invalid domain or IP format")
        else:
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            with st.spinner("PULSING SYSTEM..."):
                data = scan(domain_input)
                progress_bar.progress(50)
                ai_lines = ai_analysis(data)
                progress_bar.progress(100)
                
                st.session_state.scan_result = (domain_input, data)
                st.session_state.ai_lines = ai_lines
                score = risk(data)

                # Save to DB
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                try:
                    c.execute("INSERT INTO scans (domain,result,risk,time) VALUES (?,?,?,?)", (domain_input, str(data), score, now))
                    conn.commit()
                except:
                    pass

            # Display Results
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
            """, unsafe_allow_html=True)

            # Plotly Chart
            if PLOTLY_AVAILABLE:
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = score,
                    title = {'text': "RISK LEVEL"},
                    gauge = {'axis': {'range': [None, 100]},
                             'bar': {'color': "red" if score > 60 else "orange" if score > 30 else "green"}}
                ))
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font={'color': "#00ffcc"})
                st.plotly_chart(fig)

            # AI Analysis Display
            st.subheader("🤖 AI Security Audit")
            for text, color in ai_lines:
                st.markdown(f"<p style='color:{color if color else '#fff'}'>{text}</p>", unsafe_allow_html=True)

    # PDF Download
    if st.session_state.scan_result and st.session_state.ai_lines:
        d, dt = st.session_state.scan_result
        al = st.session_state.ai_lines
        generate_pdf(d, dt, al)
        with open("report.pdf", "rb") as f:
            st.download_button("📄 DOWNLOAD AUDIT REPORT", f, file_name=f"Polavic_{d}.pdf")

# ===== History Page =====
elif menu=="History":
    st.subheader("Previous Security Audits")
    try:
        c.execute("SELECT domain, risk, time FROM scans ORDER BY time DESC LIMIT 10")
        rows = c.fetchall()
        for r in rows:
            st.write(f"🌐 {r[0]} | ⚠️ Risk: {r[1]}% | 📅 {r[2]}")
    except:
        st.info("No history found.")
