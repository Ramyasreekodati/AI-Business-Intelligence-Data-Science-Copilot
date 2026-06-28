import streamlit as st
import os
import uuid
import sys
import pandas as pd

# Add the parent directory to sys.path so we can import from agents and src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------- Configuration ----------
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

# ---------- UI & Theming ----------
st.set_page_config(page_title="AI BI Demo", layout="wide", page_icon="📊")

# Custom CSS for a premium look
st.markdown("""
<style>
    /* Main container styling */
    .report-card {
        background: linear-gradient(145deg, #1e1e24, #2a2a35);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        color: white;
        border: 1px solid #3d3d4d;
    }
    
    /* Headers inside cards */
    .report-card h3 {
        color: #4facfe;
        margin-top: 0;
        margin-bottom: 16px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Highlighted text */
    .highlight-text {
        color: #00f2fe;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ AI Business Intelligence & Data Science Copilot")
st.markdown("*Upload a dataset to run AI-powered Exploratory Data Analysis (EDA) and Business Insights seamlessly.*")
st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Upload Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        if st.button("🚀 Run AI Analysis", use_container_width=True, type="primary"):
            with st.spinner("Initializing Agents..."):
                # Save file locally
                dataset_id = str(uuid.uuid4())
                dest_path = os.path.join(DATA_DIR, f"{dataset_id}.csv")
                with open(dest_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state["dataset_id"] = dataset_id
                st.session_state["analysis_done"] = False

with col2:
    if "dataset_id" in st.session_state and not st.session_state.get("analysis_done", False):
        dataset_id = st.session_state["dataset_id"]
        
        with st.status("🧠 Processing Dataset with Multi-Agent System...", expanded=True) as status:
            try:
                st.write("✓ Data ingestion agent active...")
                
                # Import agents directly from the codebase
                from agents.supervisor_agent import SupervisorAgent
                from agents.data_agent import DataAgent
                from agents.eda_agent import EDAGent
                from agents.business_agent import BusinessAgent
                
                st.write("✓ EDA agent active...")
                # Setup agents and execute
                agents_registry = {
                    "cleaning": DataAgent(),
                    "eda": EDAGent(),
                    "insight": BusinessAgent(),
                    "report": BusinessAgent(),
                }
                supervisor = SupervisorAgent(agents_registry)
                
                st.write("✓ Business insights agent active...")
                # Run the analysis
                result = supervisor.execute(dataset_id, context={})
                
                st.session_state["result"] = result
                st.session_state["analysis_done"] = True
                status.update(label="Analysis complete!", state="complete", expanded=False)
                
            except Exception as e:
                status.update(label="An error occurred", state="error", expanded=False)
                st.error(f"Analysis Failed: {e}")

# ---------- Beautiful Results Display ----------
if st.session_state.get("analysis_done", False) and "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()
    st.header("📊 AI Analysis Report")
    
    if isinstance(result, dict) and "eda" in result:
        eda = result["eda"]
        
        # Display dataset overview metrics
        st.markdown('<div class="report-card"><h3>Dataset Overview</h3>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric(label="Total Rows", value=f"{eda.get('rows', 0):,}")
        m2.metric(label="Total Columns", value=f"{eda.get('columns', 0):,}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Parse and display Column Stats beautifully using a dataframe
        col_stats = eda.get("column_stats", {})
        if col_stats:
            st.markdown('<div class="report-card"><h3>Column Statistics</h3>', unsafe_allow_html=True)
            
            # Convert dictionary of dicts to a list of dicts for pandas
            data = []
            for col_name, stats in col_stats.items():
                data.append({
                    "Feature Name": col_name,
                    "Unique Values": stats.get("unique", 0),
                    "Missing Values": stats.get("missing", 0)
                })
            
            df = pd.DataFrame(data)
            
            # Style the dataframe (gradient background on unique values)
            st.dataframe(
                df.style.background_gradient(subset=['Unique Values'], cmap="Blues"),
                use_container_width=True,
                hide_index=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Display any other insights text if they exist (business_agent might populate this)
        if "insights" in result or "report" in result:
            st.markdown('<div class="report-card"><h3>Business Insights</h3>', unsafe_allow_html=True)
            st.write(result.get("insights", result.get("report", "No specific text insights returned.")))
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        # Fallback for unexpected formats
        st.json(result)
