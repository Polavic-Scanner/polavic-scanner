import streamlit as st
import sqlite3
import hashlib
import socket
import requests
import ssl
from datetime import datetime
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ================= DB =================
conn = sqlite3.connect("app.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS scans(username TEXT, domain TEXT, result TEXT, time TEXT)")
conn.commit()

# ================= AUTH =================
def hash_pass(p):
    return hashlib.sha256(p.encode()).hexdigest()

def signup_user(u,p):
    c.execute("INSERT INTO users VALUES (?,?)",(u,hash_pass(p)))
    conn.commit()

def login_user(u,p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,hash_pass(p)))
    return c.fetchone()

# ================= AI =================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ai_analysis(text):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":f"Analyze security:\n{text}"}]
        )
        return res.choices[0].message.content
    except:
        return "AI Error"

# ================= SCAN =================
def scan(domain):
    ip = socket.gethostbyname(domain)
    api = requests.get(f"http://ip-api.com/json/{ip}").json()
    res = requests.get(f"http://{domain}")

    ssl_status = "Secure"
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.connect((domain,443))
    except:
        ssl_status = "Not Secure"

    return {
        "ip":ip,
        "city":api.get("city"),
        "country":api.get("country"),
        "isp":api.get("isp"),
        "status":res.status_code,
        "ssl":ssl_status
    }

# ================= PDF =================
def make_pdf(text):
    file = "report.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    story = [Paragraph(text, styles["Normal"])]
    doc.build(story)
    return file

# ================= UI =================
st.set_page_config(layout="wide")

# 🎥 VIDEO BG
st.markdown("""
<style>
video {
position: fixed;
right:0;bottom:0;
min-width:100%;
min-height:100%;
z-index:-1;
opacity:0.2;
}
</style>
<video autoplay muted loop>
<source src="https://www.w3schools.com/howto/rain.mp4" type="video/mp4">
</video>
""", unsafe_allow_html=True)

# ================= LOGIN SYSTEM =================
if "user" not in st.session_state:
    st.session_state.user = None

menu = st.sidebar.radio("Menu", ["Login","Signup"])

if st.session_state.user is None:

    if menu=="Signup":
        st.subheader("Signup")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Create Account"):
            signup_user(u,p)
            st.success("Account created")

    if menu=="Login":
        st.subheader("Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(u,p):
                st.session_state.user = u
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Wrong credentials")

# ================= DASHBOARD =================
if st.session_state.user:

    st.sidebar.write(f"👤 {st.session_state.user}")

    page = st.sidebar.radio("Dashboard", ["Scan","History","Admin"])

    st.title("🛡️ POLAVIC")

    # ===== SCAN =====
    if page=="Scan":
        domain = st.text_input("Enter domain")

        if st.button("Scan"):
            data = scan(domain)

            st.json(data)

            ai = ai_analysis(str(data))
            st.subheader("🤖 AI Analysis")
            st.write(ai)

            c.execute("INSERT INTO scans VALUES (?,?,?,?)",
                      (st.session_state.user,domain,str(data),str(datetime.now())))
            conn.commit()

            # PDF
            pdf_file = make_pdf(str(data) + "\n\nAI:\n" + ai)
            with open(pdf_file, "rb") as f:
                st.download_button("Download PDF", f, file_name="report.pdf")

    # ===== HISTORY =====
    elif page=="History":
        c.execute("SELECT * FROM scans WHERE username=?", (st.session_state.user,))
        rows = c.fetchall()

        for r in rows:
            st.write(r)

    # ===== ADMIN PANEL =====
    elif page=="Admin":
        if st.session_state.user != "admin":
            st.error("Access denied")
        else:
            st.subheader("👑 Admin Panel")

            st.write("All Users:")
            c.execute("SELECT username FROM users")
            st.write(c.fetchall())

            st.write("All Scans:")
            c.execute("SELECT * FROM scans")
            st.write(c.fetchall())
