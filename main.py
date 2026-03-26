import streamlit as st
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
import re

st.set_page_config(page_title="POLAVIC Scanner", layout="centered")

# -------- CLEAN DARK UI --------
st.markdown("""
<style>
.stApp {
    background: #0a0a0a;
    color: #00ffcc;
    font-family: monospace;
}

.title {
    text-align: center;
    font-size: 40px;
    letter-spacing: 5px;
    margin-bottom: 20px;
}

.card {
    padding: 15px;
    margin: 10px 0;
    border-radius: 10px;
    background: #111;
    border: 1px solid #222;
    transition: 0.3s;
}

.card:hover {
    box-shadow: 0 0 20px #00ffcc;
    transform: scale(1.02);
}

button {
    width: 100%;
    height: 45px;
    background: #00ffcc !important;
    color: black !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">⚡ POLAVIC SCANNER</div>', unsafe_allow_html=True)

# -------- INPUT --------
url = st.text_input("Enter Website (example: https://google.com)")

# -------- FIX URL --------
def fix_url(u):
    if not u.startswith("http"):
        u = "https://" + u
    return u

# -------- HEADER ANALYSIS --------
def analyze_headers(headers):
    security_headers = {
        "Content-Security-Policy": "XSS protection",
        "X-Frame-Options": "Clickjacking protection",
        "Strict-Transport-Security": "HTTPS enforcement",
        "X-Content-Type-Options": "MIME protection"
    }

    result = []
    for key, desc in security_headers.items():
        if key in headers:
            result.append((key, "SAFE ✅", desc))
        else:
            result.append((key, "MISSING ❌", desc))
    return result

# -------- PDF --------
def generate_pdf(url, analysis):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="POLAVIC REPORT", ln=True)
    pdf.cell(200, 10, txt=f"URL: {url}", ln=True)

    for h in analysis:
        pdf.cell(200, 10, txt=f"{h[0]} - {h[1]}", ln=True)

    pdf.output("report.pdf")

# -------- SCAN --------
if st.button("SCAN NOW"):

    if not url:
        st.error("Enter URL first")
    else:
        url = fix_url(url)

        try:
            with st.spinner("Scanning..."):
                response = requests.get(url, timeout=5)

            st.success("Scan Done ✅")

            # -------- INFO --------
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "No title"

            st.markdown(f"""
            <div class="card">
                <h3>🌐 {title}</h3>
                <p>Status: {response.status_code}</p>
            </div>
            """, unsafe_allow_html=True)

            # -------- HEADERS --------
            st.subheader("🛡️ Security Check")

            analysis = analyze_headers(response.headers)

            for h in analysis:
                color = "#00ffcc" if "SAFE" in h[1] else "#ff4b4b"

                st.markdown(f"""
                <div class="card" style="border:1px solid {color}">
                    <b style="color:{color}">{h[0]}</b><br>
                    {h[1]}<br>
                    <small>{h[2]}</small>
                </div>
                """, unsafe_allow_html=True)

            # -------- PDF --------
            if st.button("DOWNLOAD REPORT"):
                generate_pdf(url, analysis)
                with open("report.pdf", "rb") as f:
                    st.download_button("Click to Download", f)

        except:
            st.error("Website not reachable ❌")
