import streamlit as st
import requests
from bs4 import BeautifulSoup
import time

st.set_page_config(page_title="Terminal Scanner", layout="centered")

# -------- TERMINAL STYLE --------
st.markdown("""
<style>
.stApp {
    background-color: black;
    color: #00ff00;
    font-family: monospace;
}

.terminal {
    background: black;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #00ff00;
    height: 400px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

st.title("💻 HACKER TERMINAL SCANNER")

url = st.text_input("Enter target (example: google.com)")

# -------- FIX URL --------
def fix_url(u):
    if not u.startswith("http"):
        u = "https://" + u
    return u

# -------- TERMINAL OUTPUT --------
terminal = st.empty()

def print_terminal(lines):
    output = ""
    for line in lines:
        output += line + "\n"
        terminal.markdown(f"<div class='terminal'><pre>{output}</pre></div>", unsafe_allow_html=True)
        time.sleep(0.4)

# -------- SCAN --------
if st.button("INITIATE SCAN"):

    if not url:
        st.warning("Enter target first")
    else:
        url = fix_url(url)

        try:
            # fake hacker steps
            steps = [
                "Initializing modules...",
                "Bypassing firewall...",
                "Establishing secure connection...",
                f"Target locked: {url}",
                "Fetching headers...",
                "Analyzing vulnerabilities..."
            ]

            print_terminal(steps)

            response = requests.get(url, timeout=5)

            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.title.string if soup.title else "Unknown"

            result = [
                "------ RESULT ------",
                f"Website: {title}",
                f"Status Code: {response.status_code}",
                "Scan Complete ✔"
            ]

            print_terminal(result)

        except:
            print_terminal(["Connection Failed ❌"])
