import streamlit as st
import socket
import requests
import time
import ssl
from datetime import datetime

# 1. PAGE SETTINGS
st.set_page_config(page_title="POLAVIC", page_icon="🛡️", layout="centered")

# 2. DESIGNER CSS (Wahi Original Aesthetic)
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; color: #ffffff !important; }
    .logo-container { text-align: center; margin-top: -20px; }
    .logo-shield { 
        width: 80px; height: 100px; border: 3px solid #ff4b4b; 
        border-radius: 10px 10px 40px 40px; display: inline-block; 
        position: relative; box-shadow: 0 0 20px #ff4b4b; 
    }
    .logo-bolt { position: absolute; top: 20px; left: 18px; color: #ff4b4b; font-size: 50px; font-weight: bold; }
    .main-title { color: #ffffff; font-family: 'Courier New', monospace; font-size: 35px; font-weight: bold; text-align: center; letter-spacing: 8px; margin-top: 15px; }
    
    .stTextInput>div>div>input { background-color: #0a0a0a !important; color: #ff4b4b !important; border: 1px solid #333 !important; text-align: center; }
    .stButton>button { background-color: #ff4b4b !important; color: white !important; width: 100%; font-weight: bold; height: 50px; border: none; }

    .report-box { background: #0a0a0a; padding: 25px; border: 1px solid #222; border-top: 4px solid #ff4b4b; margin-top: 30px; border-radius: 5px; }
    .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
    .data-item { background: #050505; padding: 12px; border: 1px solid #1a1a1a; border-radius: 4px; border-left: 2px solid #333; }
    .label { color: #666; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
    .value { color: #fff; font-size: 14px; font-weight: bold; display: block; margin-top: 4px; }
    .status-tag { color: #00ff00; font-size: 12px; font-weight: bold; }
    
    /* Form Border Hatane ke liye */
    [data-testid="stForm"] { border: none; padding: 0; }
    </style>
    
    <div class="logo-container">
        <div class="logo-shield"><div class="logo-bolt">⚡</div></div>
    </div>
    <div class="main-title">POLAVIC</div>
    """, unsafe_allow_html=True)

st.write("---")

# 3. ENTER KEY SUPPORT (Using st.form)
with st.form("polavic_scan_form", clear_on_submit=False):
    url_input = st.text_input("", placeholder="ENTER DOMAIN (e.g. google.com)")
    submit_button = st.form_submit_button("RUN SECURITY SCAN")

if submit_button:
    if url_input:
        target = url_input.replace("https://", "").replace("http://", "").split('/')[0]
        with st.spinner('PULSING SYSTEM...'):
            try:
                # --- GATHERING ALL 8 FEATURES ---
                ip_addr = socket.gethostbyname(target)
                res = requests.get(f"http://ip-api.com/json/{ip_addr}").json()
                
                start = time.time()
                socket.create_connection((target, 80), timeout=2)
                ping = round((time.time() - start) * 1000, 2)

                response = requests.get(f"http://{target}", timeout=5, allow_redirects=True)
                server_tech = response.headers.get('Server', 'HIDDEN')
                redirected = "YES" if len(response.history) > 0 else "NO"
                
                expiry_str = "INACTIVE"
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((target, 443), timeout=3) as sock:
                        with context.wrap_socket(sock, server_hostname=target) as ssock:
                            cert = ssock.getpeercert()
                            expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                            expiry_str = expiry.strftime('%Y-%m-%d')
                except: pass

                # --- DISPLAYING ALL 8 BOXES ---
                st.markdown(f"""
                <div class="report-box">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="color:#ff4b4b; font-weight:bold; font-size:20px;">REPORT: {target.upper()}</span>
                        <span class="status-tag">● SYSTEM ACTIVE</span>
                    </div>
                    <div class="data-grid">
                        <div class="data-item"><span class="label">IPv4 Address</span><span class="value">{ip_addr}</span></div>
                        <div class="data-item"><span class="label">Location</span><span class="value">{res.get('city')}, {res.get('country')}</span></div>
                        <div class="data-item"><span class="label">Response Time</span><span class="value">{ping} ms</span></div>
                        <div class="data-item"><span class="label">Server Tech</span><span class="value">{server_tech}</span></div>
                        <div class="data-item"><span class="label">HTTPS Redirect</span><span class="value">{redirected}</span></div>
                        <div class="data-item"><span class="label">ISP Provider</span><span class="value">{res.get('isp', 'N/A')}</span></div>
                        <div class="data-item"><span class="label">SSL Security</span><span class="value">{'ENCRYPTED' if expiry_str != 'INACTIVE' else 'OPEN'}</span></div>
                        <div class="data-item"><span class="label">SSL Expiry</span><span class="value">{expiry_str}</span></div>
                    </div>
                    <div style="margin-top:20px; font-size:10px; color:#333; text-align:center;">
                        POLAVIC INTELLIGENCE // SECURE DATA PORTAL
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.balloons()
            except:
                st.error("SYSTEM ERROR: Target Unreachable.")
    else:
        st.error("INPUT REQUIRED.")

st.sidebar.caption("POLAVIC v8.5 | Advanced Hub")
