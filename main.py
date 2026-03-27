import streamlit as st
import socket
import requests
import ssl
import re
import sqlite3
import time
from bs4 import BeautifulSoup
from fpdf import FPDF
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime

# Optional: plotly import try
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

# ===== Streamlit Page Config =====
st.set_page_config(layout="wide", page_title="POLAVIC CYBER AI NEON")

# ===== Database Setup =====
conn = sqlite3.connect("data.db", check_same_thread=False)
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
.stButton>button { background-color:#00ffcc; color:black; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.title("🛡️ POLAVIC CYBER AI NEON")

# ===== Sidebar =====
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
            if result:
                open_ports.append(result)
    return open_ports

# ===== Scan Function =====
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

    ssl_status = "Not Secure"
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain,443))
        ssl_status = "Secure"
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
            else: severity_lines.append((line,None))
        return severity_lines
    except Exception as e:
        return [("AI analysis unavailable: "+str(e),"red")]

# ===== PDF =====
def generate_pdf(domain,data,ai_lines):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",14)
    pdf.cell(0,10,"POLAVIC CYBER AI NEON REPORT",ln=True,align='C')
    pdf.set_font("Arial",size=12)
    pdf.ln(5)
    for key in ["Domain","IP","City","Country","Status","SSL","Title","Open Ports"]:
        val = data.get(key.lower()) if key.lower()!="open ports" else data["ports"]
        pdf.multi_cell(0,8,f"{key}: {val}")
    pdf.ln(5)
    pdf.multi_cell(0,8,"AI Analysis:")
    for text,color in ai_lines:
        pdf.multi_cell(0,8,text)
    pdf.output("report.pdf")

# ===== Session State =====
if "scan_result" not in st.session_state: st.session_state.scan_result=None
if "ai_lines" not in st.session_state: st.session_state.ai_lines=None

# ===== Scan Page =====
if menu=="Scan":
    domain = st.text_input("Enter Domain (without http:// or https://)")
    if st.button("Scan Now"):
        if not valid_domain(domain):
            st.error("Invalid domain or IP")
        else:
            status_text = st.empty()
            progress_bar = st.progress(0)
            steps = ["Initializing","Port Scanning","Fetching Data","AI Analysis"]
            for i, step in enumerate(steps):
                status_text.text(f"{step}...")
                time.sleep(0.5)
                progress_bar.progress(int((i+1)/len(steps)*100))

            data = scan(domain)
            st.session_state.scan_result = (domain,data)
            score = risk(data)

            # Save to DB
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO scans (domain,result,risk,time) VALUES (?,?,?,?)",(domain,str(data),score,now))
            conn.commit()

            # Cards
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

            # Risk chart (plotly optional)
            if PLOTLY_AVAILABLE:
                fig = go.Figure([go.Bar(x=["Risk Score"], y=[score], marker_color='#FF5733' if score>60 else '#FFC300' if score>30 else '#28B463')])
                fig.update_layout(plot_bgcolor='#121212' if theme=="Dark" else 'white', paper_bgcolor='#121212' if theme=="Dark" else 'white', font_color='#00ffcc' if theme=="Dark" else 'black')
                st.plotly_chart(fig,use_container_width=True)
            else:
                st.write(f"Risk Score: {score}")

            # Headers
            st.subheader("📡 Headers")
            st.json(data["headers"])

            # AI Analysis
            st.subheader("🤖 AI Analysis")
            ai_lines = ai_analysis(data)
            st.session_state.ai_lines = ai_lines
            for text,color in ai_lines:
                st.markdown(f"<span style='color:{color}'>{text}</span>" if color else text,unsafe_allow_html=True)

    # PDF Download
    if st.session_state.scan_result and st.session_state.ai_lines:
        domain,data = st.session_state.scan_result
        ai_lines = st.session_state.ai_lines
        generate_pdf(domain,data,ai_lines)
        with open("report.pdf","rb") as f:
            st.download_button("📄 Download POLAVIC NEON Report",f,file_name="report.pdf")

# ===== History Page =====
elif menu=="History":
    st.subheader("Scan History Dashboard")
    c.execute("SELECT domain,risk,time FROM scans ORDER BY time DESC")
    rows = c.fetchall()
    for r in rows:
        st.write(f"Domain: {r[0]}, Risk: {r[1]}, Time: {r[2]}")
    if st.button("Clear History"):
        c.execute("DELETE FROM scans")
        conn.commit()
        st.success("History Cleared")
