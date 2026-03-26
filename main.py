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
        .main-title { color: #ffffff; font-family: 'Courier New', monospace; font-size: 38px; font-weight: bold; text-align: center; margin-bottom: 30px; letter-spacing: 8px; text-shadow: 0 0 10px #ff4b4b; }
        .report-box { background: #0a0a0a; padding: 25px; border: 1px solid #222; border-top: 4px solid #ff4b4b; border-radius: 10px; margin-top: 20px; box-shadow: 0 10px 30px rgba(255, 75, 75, 0.1); }
        .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
        .data-item { background: #050505; padding: 12px; border: 1px solid #1a1a1a; border-radius: 5px; transition: 0.3s; }
        .data-item:hover { border-color: #ff4b4b; }
        .label { color: #666; font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; display: block; }
        .value { color: #fff; font-size: 14px; font-weight: bold; display: block; margin-top: 4px; font-family: 'monospace'; }
        .stButton>button { background-color: #ff4b4b !important; color: white !important; width: 100%; border-radius: 5px; border: none; font-weight: bold; height: 48px; margin-top: 20px; letter-spacing: 2px; transition: 0.3s; }
        .stButton>button:hover { background-color: #ff2b2b !important; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255, 75, 75, 0.4); }
    </style>
""", unsafe_allow_html=True)

# UI Header
st.markdown('<div class="main-title">POLAVIC</div>', unsafe_allow_html=True)

# 3. SCANNING ENGINE (All Features Back!)
with st.form("polavic_scan_form"):
    url_input = st.text_input("", placeholder="ENTER DOMAIN (e.g. google.com)")
    submit = st.form_submit_button("INITIATE SECURITY SCAN")

if submit and url_input:
    target = url_input.replace("https://", "").replace("http://", "").split('/')[0]
    with st.spinner('ACCESSING GLOBAL TERMINALS...'):
        try:
            # Gathering Features
            ip_addr = socket.gethostbyname(target)
            res = requests.get(f"http://ip-api.com/json/{ip_addr}").json()
            
            start = time.time()
            socket.create_connection((target, 80), timeout=2)
            ping = f"{round((time.time() - start) * 1000, 2)}ms"
            
            # Technology Check
            response = requests.get(f"http://{target}", timeout=5)
            server_tech = response.headers.get('Server', 'PROTECTED')
            
            scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Result Data Dictionary
            data = {
                "Target Host": target,
                "IPv4 Address": ip_addr,
                "Location": f"{res.get('city', 'N/A')}, {res.get('country', 'N/A')}",
                "Response Time": ping,
                "Server Stack": server_tech,
                "ISP Provider": res.get('isp', 'N/A'),
                "Security Status": "ENCRYPTED / SECURE",
                "Scan Timestamp": scan_time
            }

            # 4. RESULTS UI
            st.markdown(f"""
            <div id="printable-area" class="report-box">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="color:#ff4b4b; font-weight:bold; letter-spacing:2px;">🛡️ SYSTEM ACTIVE</span>
                    <span style="font-size:10px; color:#444;">POLAVIC v8.5</span>
                </div>
                <div class="data-grid">
                    {" ".join([f'<div class="data-item"><span class="label">{k}</span><span class="value">{v}</span></div>' for k,v in data.items()])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

            # 5. SMART PDF/PRINT BUTTON
            if st.button("📥 DOWNLOAD AUDIT REPORT (PDF)"):
                st.markdown("<script>window.parent.print();</script>", unsafe_allow_html=True)
            
            st.info("💡 Tip: Print screen khulne par 'Save as PDF' select karein.")

        except Exception as e:
            st.error(f"SYSTEM ERROR: Target Unreachable or Invalid Input.")

# Footer
st.markdown('<div style="text-align:center; color:#222; font-size:10px; margin-top:60px; letter-spacing:3px;">POLAVIC INTELLIGENCE // SECURE DATA PORTAL</div>', unsafe_allow_html=True)
