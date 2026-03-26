import streamlit as st
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Cyber Scanner", layout="wide")

# ---------------- BACKGROUND ----------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}

.stApp {
    background: url("https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.gif");
    background-size: cover;
    background-attachment: fixed;
}

.card {
    padding: 15px;
    margin: 10px;
    border-radius: 12px;
    background: rgba(0,0,0,0.6);
    transition: 0.3s;
}

.card:hover {
    transform: scale(1.03);
    box-shadow: 0 0 20px cyan;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("💀 Hacker Style Website Scanner")

url = st.text_input("Enter Website URL")

# ---------------- FUNCTIONS ----------------
def analyze_headers(headers):
    security_headers = {
        "Content-Security-Policy": "Prevents XSS attacks",
        "X-Frame-Options": "Prevents clickjacking",
        "Strict-Transport-Security": "Forces HTTPS",
        "X-Content-Type-Options": "Prevents MIME sniffing",
        "Referrer-Policy": "Controls referrer data"
    }

    result = []

    for key, desc in security_headers.items():
        if key in headers:
            result.append((key, "✅ Present", desc))
        else:
            result.append((key, "❌ Missing", desc))

    return result


def generate_pdf(url, headers_analysis):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Cyber Report", ln=True)

    pdf.cell(200, 10, txt=f"URL: {url}", ln=True)

    for h in headers_analysis:
        pdf.cell(200, 10, txt=f"{h[0]} - {h[1]}", ln=True)

    pdf.output("report.pdf")


# ---------------- SCAN BUTTON ----------------
if st.button("🚀 Scan Now"):
    try:
        response = requests.get(url)
        headers = response.headers

        st.success("Scan Completed ✅")

        # -------- HEADERS UI --------
        st.subheader("🛡️ Security Headers")

        analysis = analyze_headers(headers)

        for h in analysis:
            color = "#00ffcc" if "Present" in h[1] else "#ff4b4b"

            st.markdown(f"""
            <div class="card" style="border:1px solid {color}; box-shadow:0 0 15px {color};">
                <h4 style="color:{color}">{h[0]}</h4>
                <p>{h[1]}</p>
                <small>{h[2]}</small>
            </div>
            """, unsafe_allow_html=True)

        # -------- PAGE DATA --------
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No title"

        st.subheader("🌐 Website Info")

        st.markdown(f"""
        <div class="card">
            <h3>Title: {title}</h3>
            <p>Status Code: {response.status_code}</p>
        </div>
        """, unsafe_allow_html=True)

        # -------- PDF --------
        if st.button("📄 Download Report"):
            generate_pdf(url, analysis)
            with open("report.pdf", "rb") as f:
                st.download_button("Download PDF", f, file_name="report.pdf")

    except:
        st.error("Invalid URL or Site Down ❌")
