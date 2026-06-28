import streamlit as st
import requests
import os

# ---------- Configuration ----------
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"
TOKEN = os.getenv("STREAMLIT_TOKEN", "")

# Helper functions
def post_endpoint(endpoint: str, json_body=None, files=None):
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    url = f"{BACKEND_URL}{API_PREFIX}{endpoint}"
    try:
        if files:
            resp = requests.post(url, files=files, headers=headers)
        else:
            resp = requests.post(url, json=json_body, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        st.error(f"Request to {endpoint} failed: {exc}")
        return None

def get_endpoint(endpoint: str):
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}
    url = f"{BACKEND_URL}{API_PREFIX}{endpoint}"
    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        st.error(f"GET {endpoint} failed: {exc}")
        return None

# ---------- UI ----------
st.set_page_config(page_title="AI BI Demo", layout="centered")
st.title("AI Business Intelligence & Data Science Copilot Demo")
st.write("Upload a CSV/Excel file, run analysis, and view the generated report.")

uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
if uploaded_file is not None:
    st.success(f"File `{uploaded_file.name}` ready.")
    if st.button("Send to backend"):
        with st.spinner("Uploading…"):
            files = {"file": (uploaded_file.name, uploaded_file.read(), uploaded_file.type)}
            resp = post_endpoint("/upload", files=files)
        if resp:
            file_id = resp.get("file_id") or resp.get("id")
            st.session_state["file_id"] = file_id
            st.success(f"Uploaded – file_id: `{file_id}`")

if "file_id" in st.session_state:
    if st.button("Run Analysis"):
        with st.spinner("Analyzing…"):
            resp = post_endpoint("/analyze", json_body={"file_id": st.session_state["file_id"]})
        if resp:
            run_id = resp.get("run_id")
            st.session_state["run_id"] = run_id
            st.success(f"Analysis started – run_id: `{run_id}`")

if "run_id" in st.session_state:
    if st.button("Fetch Report"):
        with st.spinner("Fetching report…"):
            report = get_endpoint(f"/report/{st.session_state['run_id']}")
        if report:
            st.subheader("Report")
            insights = report.get("insights")
            charts = report.get("charts")
            if insights:
                st.write(insights)
            if charts:
                for i, url in enumerate(charts):
                    st.image(url, caption=f"Chart {i+1}")
            st.success("Report displayed.")
