import streamlit as st
import socket
import requests
import time
from datetime import datetime

# 1. PAGE SETTINGS
st.set_page_config(page_title="POLAVIC", page_icon="🛡️", layout="centered")

# 2. PREMIUM AESTHETIC CSS
st.markdown("""
    <style>
        .stApp { background-color: #000000 !important; color: #ffffff !important; }
        [data-testid="stSidebarNav"], button[kind="header"], header { display: none !important; }
        
        /* New Logo Style */
        .logo-text {
            color: #ffffff;
            font-family: 'Courier New', monospace;
            font-size: 45px;
            font-weight: bold;
            text-align: center;
            margin-top: -50px;
            margin-bottom: 20px;
            letter-spacing: 12px;
            text-shadow: 0 0 15px #ff4b4b, 0 0 30px #ff4b4b;
        }

        .report-box { background: #0a0a0a; padding: 25px; border: 1px solid #222; border-top: 4px solid #ff4b4b; border-radius: 10px; margin-top: 20px; box-shadow: 0 10px 30px rgba(255, 75, 75, 0.1); }
        .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
        .data-item { background: #050505; padding: 12px; border: 1px solid #1a1a1a; border-radius: 5px; }
        .label { color: #666; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; display: block; }
        .value { color: #fff; font-size: 14px; font-weight: bold; display: block; margin-top: 4px; font-family: 'monospace'; }
        
        .stButton>button { background-color: #ff4b4b !important; color: white !important; width: 100%; border-radius: 5px; border: none; font-weight: bold; height: 48px; margin-top: 10px; letter-spacing: 2px; }
    </style>
""", unsafe_allow_html=True)

# 🏆 FORCE LOGO (Direct HTML)
st.markdown('<h1 class="logo-text">POLAVIC</h1>', unsafe_allow_html=True)

# 3. INPUT FORM
with st.form("polavic_scan_form"):
    url_input = st.text_input("", placeholder="ENTER DOMAIN (e.g. google.com)")
    submit = st.form_submit_button("RUN SECURITY SCAN")

if submit and url_input:
    target = url_input.replace("https://", "").replace("http://", "").split('/')[0]
    with st.spinner('PULSING TERMINAL...'):
        try:
            # 🔄 SCAN ENGINE
            ip_addr = socket.gethostbyname(target)
            res = requests.get(f"http://ip-api.com/json/{ip_addr}").json()
            
            start = time.time()
            socket.create_connection((target, 80), timeout=2)
            ping = f"{round((time.time() - start) * 1000, 2)}ms"
            
            response = requests.get(f"http://{target}", timeout=5)
            server_tech = response.headers.get('Server', 'PROTECTED')
            scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # 📦 RESULT UI
            st.markdown(f"""
            <div id="printable-area" class="report-box">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#ff4b4b; font-weight:bold; letter-spacing:2px;">🛡️ SYSTEM ACTIVE</span>
                    <span style="font-size:10px; color:#444;">POLAVIC INTELLIGENCE</span>
                </div>
                <div class="data-grid">
                    <div class="data-item"><span class="label">Target Host</span><span class="value">{target}</span></div>
                    <div class="data-item"><span class="label">IPv4 Address</span><span class="value">{ip_addr}</span></div>
                    <div class="data-item"><span class="label">City</span><span class="value">{res.get('city', 'N/A')}</span></div>
                    <div class="data-item"><span class="label">Country</span><span class="value">{res.get('country', 'N/A')}</span></div>
                    <div class="data-item"><span class="label">Server Technology</span><span class="value">{server_tech}</span></div>
                    <div class="data-item"><span class="label">Response Time</span><span class="value">{ping}</span></div>
                    <div class="data-item"><span class="label">ISP Provider</span><span class="value">{res.get('isp', 'N/A')}</span></div>
                    <div class="data-item"><span class="label">Scan Time</span><span class="value">{scan_time}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

            # 📥 DOWNLOAD BUTTON
            if st.button("📥 DOWNLOAD AUDIT REPORT (PDF)"):
                st.markdown("<script>window.parent.print();</script>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"SYSTEM ERROR: Try again.")

# FOOTER
st.markdown('<div style="text-align:center; color:#222; font-size:10px; margin-top:60px; letter-spacing:3px;">POLAVIC INTELLIGENCE // SECURE DATA PORTAL</div>', unsafe_allow_html=True)
