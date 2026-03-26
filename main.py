import streamlit as st
import socket
import requests
import time
from datetime import datetime
import re
import ssl
import whois

# PAGE CONFIG
st.set_page_config(page_title="POLAVIC", page_icon="🛡️", layout="centered")

# 🌌 FULL UI (3D BACKGROUND + ANIMATION)
st.markdown("""
<style>

/* BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #000000, #0a0a0a, #111111);
    background-size: 400% 400%;
    animation: bgMove 12s ease infinite;
    color: white;
}

/* MOVING BG */
@keyframes bgMove {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* GLOW ORBS */
.stApp::before {
    content: "";
    position: fixed;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(255,0,0,0.2), transparent);
    top: 20%;
    left: 10%;
    filter: blur(120px);
    z-index: -1;
}

.stApp::after {
    content: "";
    position: fixed;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(255,0,0,0.15), transparent);
    bottom: 10%;
    right: 10%;
    filter: blur(100px);
    z-index: -1;
}

/* LOGO */
.logo {
    text-align:center;
    font-size:48px;
    letter-spacing:10px;
    font-weight:bold;
    animation: float 3s ease-in-out infinite;
    text-shadow:0 0 20px red;
}
@keyframes float {
    0% {transform: translateY(0);}
    50% {transform: translateY(-10px);}
    100% {transform: translateY(0);}
}

/* CARD */
.box {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    padding:20px;
    border-radius:15px;
    border:1px solid rgba(255,0,0,0.3);
    box-shadow:0 10px 40px rgba(255,0,0,0.25);
    margin-top:20px;
    transition:0.3s;
}
.box:hover {
    transform: scale(1.02);
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(135deg, red, darkred);
    border-radius:10px;
    height:45px;
    font-weight:bold;
    color:white;
}

/* INPUT */
.stTextInput input {
    background: rgba(255,255,255,0.05);
    border:1px solid rgba(255,0,0,0.3);
    border-radius:10px;
    color:white;
}

</style>
""", unsafe_allow_html=True)

# LOGO
st.markdown('<div class="logo">🛡️ POLAVIC</div>', unsafe_allow_html=True)

# VALIDATION
def is_valid_domain(domain):
    return re.match(r"^(?!:\/\/)([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$", domain)

# SSL
def check_ssl(domain):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain, 443))
            return "Secure ✅"
    except:
        return "Not Secure ❌"

# PORT SCAN
def scan_ports(domain):
    ports = [21,22,80,443,8080]
    open_ports = []
    for p in ports:
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect((domain,p))
            open_ports.append(p)
            s.close()
        except:
            pass
    return open_ports if open_ports else ["None"]

# WHOIS
def get_whois(domain):
    try:
        return whois.whois(domain).org or "Hidden"
    except:
        return "Unavailable"

# SUBDOMAIN
def subdomain_scan(domain):
    subs = ["www","mail","ftp","dev","test"]
    found = []
    for s in subs:
        try:
            socket.gethostbyname(f"{s}.{domain}")
            found.append(f"{s}.{domain}")
        except:
            pass
    return found if found else ["None"]

# AI LOGIC
def ai_analysis(ssl_status, ports, response_code):
    score = 0
    issues = []

    if "Not Secure" in ssl_status:
        score -= 2
        issues.append("No SSL encryption")

    if 21 in ports or 22 in ports:
        score -= 1
        issues.append("Sensitive ports open")

    if response_code != 200:
        score -= 1
        issues.append("Site not stable")

    if score >= 0:
        return "🟢 Safe", issues
    elif score == -1:
        return "🟡 Medium Risk", issues
    else:
        return "🔴 Risky", issues

# FORM
with st.form("scan"):
    url = st.text_input("", placeholder="Enter domain (example.com)")
    submit = st.form_submit_button("RUN FULL SCAN")

if submit:
    if not is_valid_domain(url):
        st.error("Invalid domain ❌")
    else:
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress.progress(i+1)

        try:
            start = time.time()

            ip = socket.gethostbyname(url)
            api = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
            res = requests.get(f"http://{url}", timeout=5)

            load = round((time.time()-start)*1000,2)

            ssl_status = check_ssl(url)
            ports = scan_ports(url)
            owner = get_whois(url)
            subs = subdomain_scan(url)

            ai_status, issues = ai_analysis(ssl_status, ports, res.status_code)

            st.success("Scan Complete ✅")

            st.metric("Speed", f"{load} ms")
            st.metric("SSL", ssl_status)
            st.metric("Ports", str(ports))

            # 💎 3D CARD
            st.markdown(f"""
            <div class="box">
            <h3 style="text-align:center;color:#ff4d4d;">🌐 TARGET DETAILS</h3>
            <hr>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
                <div><b>Domain</b><br>{url}</div>
                <div><b>IP</b><br>{ip}</div>
                <div><b>City</b><br>{api.get('city')}</div>
                <div><b>Country</b><br>{api.get('country')}</div>
                <div><b>ISP</b><br>{api.get('isp')}</div>
                <div><b>Owner</b><br>{owner}</div>
                <div><b>Server</b><br>{res.headers.get('Server')}</div>
                <div><b>Status</b><br>{res.status_code}</div>
            </div>

            <div style="text-align:center;margin-top:10px;font-size:12px;">
            {datetime.now()}
            </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🔎 Subdomains")
            for s in subs:
                st.write(s)

            st.markdown("### 🤖 AI Analysis")
            st.write(ai_status)
            for i in issues:
                st.write("⚠️", i)

        except:
            st.error("Error occurred ⚠️")
