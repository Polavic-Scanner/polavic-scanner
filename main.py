import streamlit as st
import socket
from datetime import datetime

# 1. PAGE SETTINGS
st.set_page_config(page_title="POLAVIC", page_icon="🛡️", layout="centered")

# 2. DESIGNER CSS (Clean & Aesthetic)
st.markdown("""
    <style>
        .stApp { background-color: #000000 !important; color: #ffffff !important; }
        [data-testid="stSidebarNav"], button[kind="header"], header { display: none !important; }
        .main-title { color: #ffffff; font-family: 'Courier New', monospace; font-size: 35px; font-weight: bold; text-align: center; margin-bottom: 20px; letter-spacing: 5px; }
        .report-box { background: #0a0a0a; padding: 25px; border: 1px solid #222; border-top: 4px solid #ff4b4b; border-radius: 10px; margin-top: 20px; }
        .data-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
        .data-item { background: #050505; padding: 12px; border: 1px solid #1a1a1a; border-radius: 5px; }
        .label { color: #666; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
        .value { color: #fff; font-size: 14px; font-weight: bold; display: block; margin-top: 4px; }
        .stButton>button { background-color: #ff4b4b !important; color: white !important; width: 100%; border-radius: 5px; border: none; font-weight: bold; height: 45px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛡️ POLAVIC</div>', unsafe_allow_html=True)

# 3. INPUT FORM
with st.form("scan_form"):
    url_input = st.text_input("", placeholder="ENTER DOMAIN (e.g. google.com)")
    submit = st.form_submit_button("RUN SECURITY SCAN")

if submit and url_input:
    target = url_input.replace("https://", "").replace("http://", "").split('/')[0]
    
    with st.spinner("PULSING SYSTEM..."):
        try:
            ip_addr = socket.gethostbyname(target)
            scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Results UI
            st.markdown(f"""
            <div id="printable-area" class="report-box">
                <div style="color:#ff4b4b; font-weight:bold; margin-bottom:10px;">SYSTEM ACTIVE</div>
                <div class="data-grid">
                    <div class="data-item"><span class="label">Target</span><span class="value">{target}</span></div>
                    <div class="data-item"><span class="label">IP Address</span><span class="value">{ip_addr}</span></div>
                    <div class="data-item"><span class="label">Scan Date</span><span class="value">{scan_time}</span></div>
                    <div class="data-item"><span class="label">Status</span><span class="value">SECURE</span></div>
                </div>
                <div style="margin-top:20px; font-size:10px; color:#444; text-align:center;">POLAVIC INTELLIGENCE // SECURE REPORT</div>
            </div>
            """, unsafe_allow_html=True)
            st.balloons()

            # 4. SMART PDF BUTTON (Jugaad)
            # Ye button browser ka 'Print' command use karega jo PDF save kar deta hai
            st.button("📥 DOWNLOAD REPORT (PDF)", on_click=None, help="Save this scan as PDF")
            st.info("💡 Tip: Click 'Print' and select 'Save as PDF' in the next window.")
            
            # JavaScript to trigger print
            st.markdown("""
                <script>
                const btn = window.parent.document.querySelectorAll('button')[1];
                btn.onclick = function() { window.parent.print(); }
                </script>
            """, unsafe_allow_html=True)

        except:
            st.error(f"Error: {target} unreachable.")

# Footer
st.markdown('<div style="text-align:center; color:#333; font-size:10px; margin-top:50px;">POLAVIC v8.5 // SECURE PORTAL</div>', unsafe_allow_html=True)
