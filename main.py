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

# CSS
st.markdown("""
<style>
.stApp { background-color: #000000; color: #ffffff; }
.logo-text {
    text-align:center;
    font-size:42px;
    letter-spacing:10px;
    font-weight:bold;
    text-shadow:0 0 10px red;
}
.box {
    background:#0a0a0a;
    padding:20px;
    border-left:4px solid red;
    border-radius:8px;
    margin-top:20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="logo-text">POLAVIC</div>', unsafe_allow_html=True)

# VALIDATION
def is_valid_domain(domain):
    pattern = r"^(?!:\/\/)([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
    return re.match(pattern, domain)

# SSL CHECK
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
    ports = [21, 22, 80, 443, 8080]
    open_ports = []
    for port in ports:
        try:
            s = socket.socket()
            s.settimeout(1)
            s.connect((domain, port))
            open_ports.append(port)
            s.close()
        except:
            pass
    return open_ports if open_ports else ["None"]

# WHOIS
def get_whois(domain):
    try:
        w = whois.whois(domain)
        return w.org if w.org else "Hidden"
    except:
        return "Unavailable"

# SUBDOMAIN CHECK (basic)
def subdomain_scan(domain):
    common = ["www", "mail", "ftp", "test", "dev"]
    found = []
    for sub in common:
        try:
            socket.gethostbyname(f"{sub}.{domain}")
            found.append(f"{sub}.{domain}")
        except:
            pass
    return found if found else ["None"]

# FORM
with st.form("scan"):
    url = st.text_input("", placeholder="Enter domain (example.com)")
    submit = st.form_submit_button("RUN FULL SCAN")

if submit:
    if not is_valid_domain(url):
        st.error("❌ Invalid domain")
    else:
        with st.spinner("Running deep scan..."):
            try:
                start = time.time()

                ip = socket.gethostbyname(url)
                api = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
                response = requests.get(f"http://{url}", timeout=5)

                load_time = round((time.time() - start) * 1000, 2)

                ssl_status = check_ssl(url)
                ports = scan_ports(url)
                owner = get_whois(url)
                subs = subdomain_scan(url)

                st.success("✅ FULL SCAN COMPLETE")

                # METRICS
                c1, c2, c3 = st.columns(3)
                c1.metric("⚡ Speed", f"{load_time} ms")
                c2.metric("🔐 SSL", ssl_status)
                c3.metric("🌐 Ports", str(ports))

                # MAIN INFO
                st.markdown(f"""
                <div class="box">
                <b>Target:</b> {url}<br>
                <b>IP:</b> {ip}<br>
                <b>City:</b> {api.get('city','N/A')}<br>
                <b>Country:</b> {api.get('country','N/A')}<br>
                <b>ISP:</b> {api.get('isp','N/A')}<br>
                <b>Owner (WHOIS):</b> {owner}<br>
                <b>Server:</b> {response.headers.get('Server','Hidden')}<br>
                <b>Status:</b> {response.status_code}<br>
                <b>Time:</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </div>
                """, unsafe_allow_html=True)

                # SUBDOMAINS
                st.markdown("### 🔎 Subdomains Found")
                for s in subs:
                    st.write(f"• {s}")

            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout")
            except socket.gaierror:
                st.error("🌐 Domain not found")
            except Exception:
                st.error("⚠️ Error occurred")

# FOOTER
st.markdown('<div style="text-align:center; color:#333; font-size:10px; margin-top:60px;">POLAVIC INTELLIGENCE</div>', unsafe_allow_html=True)
