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

# 🌌 3D + ANIMATION UI
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at 20% 20%, #0f0f0f, #000000);
    color: white;
}

/* LOGO */
.logo-text {
    text-align:center;
    font-size:48px;
    letter-spacing:12px;
    font-weight:bold;
    animation: float 3s ease-in-out infinite;
    text-shadow:0 0 20px red;
}
@keyframes float {
    0% {transform: translateY(0);}
    50% {transform: translateY(-10px);}
    100% {transform: translateY(0);}
}

/* SCAN LINE */
.scan-line {
    height:2px;
    background: linear-gradient(90deg, transparent, red, transparent);
    animation: scan 2s infinite;
}
@keyframes scan {
    0% {transform: translateX(-100%);}
    100% {transform: translateX(100%);}
}

/* CARD */
.box {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    padding:20px;
    border-radius:15px;
    border:1px solid rgba(255,0,0,0.3);
    box-shadow:0 10px 30px rgba(255,0,0,0.3);
    margin-top:20px;
    transition:0.3s;
}
.box:hover {
    transform: scale(1.02);
}

/* FADE */
.fade-in {
    animation: fadeIn 1s ease-in;
}
@keyframes fadeIn {
    from {opacity:0; transform:translateY(20px);}
    to {opacity:1; transform:translateY(0);}
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
st.markdown('<div class="logo-text">🛡️ POLAVIC</div>', unsafe_allow_html=True)
st.markdown('<div class="scan-line"></div>', unsafe_allow_html=True)

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

# 🤖 AI ANALYSIS (SMART LOGIC)
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
        issues.append("Website not stable")

    if score >= 0:
        status = "🟢 Safe"
    elif score == -1:
        status = "🟡 Medium Risk"
    else:
        status = "🔴 Risky"

    return status, issues

# FORM
with st.form("scan"):
    url = st.text_input("", placeholder="Enter domain (example.com)")
    submit = st.form_submit_button("RUN FULL SCAN")

if submit:
    if not is_valid_domain(url):
        st.error("❌ Invalid domain")
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

            st.success("✅ SCAN COMPLETE")

            c1,c2,c3 = st.columns(3)
            c1.metric("⚡ Speed", f"{load} ms")
            c2.metric("🔐 SSL", ssl_status)
            c3.metric("🌐 Ports", str(ports))

            st.markdown(f"""
            <div class="box fade-in">
            <b>Target:</b> {url}<br>
            <b>IP:</b> {ip}<br>
            <b>City:</b> {api.get('city','N/A')}<br>
            <b>Country:</b> {api.get('country','N/A')}<br>
            <b>ISP:</b> {api.get('isp','N/A')}<br>
            <b>Owner:</b> {owner}<br>
            <b>Server:</b> {res.headers.get('Server','Hidden')}<br>
            <b>Status:</b> {res.status_code}<br>
            <b>Time:</b> {datetime.now()}
            </div>
            """, unsafe_allow_html=True)

            # SUBDOMAINS
            st.markdown("### 🔎 Subdomains")
            for s in subs:
                st.write(f"• {s}")

            # AI RESULT
            st.markdown("### 🤖 AI Security Analysis")
            st.write(f"**Status:** {ai_status}")
            if issues:
                for i in issues:
                    st.write(f"⚠️ {i}")
            else:
                st.write("No major issues detected")

        except:
            st.error("⚠️ Error occurred")

# FOOTER
st.markdown('<div style="text-align:center;color:#444;font-size:10px;margin-top:60px;">POLAVIC INTELLIGENCE</div>', unsafe_allow_html=True)
