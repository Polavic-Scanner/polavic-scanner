import streamlit as st
import socket
import requests
import ssl
import time

st.set_page_config(layout="wide")

# ================= UI STYLE =================
st.markdown("""
<style>

/* 🔥 BACKGROUND */
.stApp {
    background: radial-gradient(circle at top, #0f0f0f, #000000);
    color: #00ffcc;
    font-family: monospace;
}

/* 🌟 TITLE */
h1 {
    text-align: center;
    color: #00ffcc;
    text-shadow: 0 0 20px #00ffcc;
}

/* 📦 CARD STYLE */
.card {
    background: rgba(0, 255, 204, 0.05);
    border: 1px solid rgba(0,255,204,0.2);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 20px;
    margin: 15px;
    text-align: center;
    box-shadow: 0 0 15px rgba(0,255,204,0.2);
    transition: 0.3s;
}

/* ✨ HOVER GLOW */
.card:hover {
    transform: translateY(-10px) scale(1.05);
    box-shadow: 0 0 40px #00ffcc;
}

/* 📊 GRID */
.row {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
}

/* 🧠 INPUT */
input {
    background: black !important;
    color: #00ffcc !important;
}

/* 🔘 BUTTON */
.stButton>button {
    background: black;
    color: #00ffcc;
    border: 1px solid #00ffcc;
    border-radius: 10px;
    transition: 0.3s;
}
.stButton>button:hover {
    background: #00ffcc;
    color: black;
    box-shadow: 0 0 20px #00ffcc;
}

</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("🛡️ POLAVIC CYBER SCANNER")

# ================= SCAN FUNCTION =================
def scan(domain):
    ip = socket.gethostbyname(domain)

    api = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
    res = requests.get(f"http://{domain}", timeout=5)

    ssl_status = "Secure"
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(3)
            s.connect((domain,443))
    except:
        ssl_status = "Not Secure"

    return {
        "ip": ip,
        "city": api.get("city"),
        "country": api.get("country"),
        "isp": api.get("isp"),
        "status": res.status_code,
        "ssl": ssl_status
    }

# ================= UI =================
domain = st.text_input("🌐 Enter Target Domain")

if st.button("🚀 Scan Target"):
    if domain:

        with st.spinner("Scanning target..."):
            time.sleep(1)
            try:
                data = scan(domain)

                # ===== CARDS UI =====
                st.markdown(f"""
                <div class="row">

                <div class="card">
                <h3>🌐 IP Address</h3>
                <p>{data['ip']}</p>
                </div>

                <div class="card">
                <h3>🏙️ City</h3>
                <p>{data['city']}</p>
                </div>

                <div class="card">
                <h3>🌍 Country</h3>
                <p>{data['country']}</p>
                </div>

                </div>

                <div class="row">

                <div class="card">
                <h3>📡 ISP</h3>
                <p>{data['isp']}</p>
                </div>

                <div class="card">
                <h3>📶 Status Code</h3>
                <p>{data['status']}</p>
                </div>

                <div class="card">
                <h3>🔐 SSL Security</h3>
                <p>{data['ssl']}</p>
                </div>

                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Error: {e}")

    else:
        st.warning("⚠️ Enter a domain first")
