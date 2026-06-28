import streamlit as st
import os
import uuid
import sys

# Add the parent directory to sys.path so we can import from agents and src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------- Configuration ----------
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

# ---------- UI ----------
st.set_page_config(page_title="AI BI Demo", layout="centered")
st.title("AI Business Intelligence & Data Science Copilot Demo")
st.write("Upload a CSV file to run the AI analysis locally within Streamlit (No Backend Required).")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    st.success(f"File `{uploaded_file.name}` ready.")
    
    if st.button("Run AI Analysis"):
        with st.spinner("Processing file..."):
            # 1. Save file locally
            dataset_id = str(uuid.uuid4())
            dest_path = os.path.join(DATA_DIR, f"{dataset_id}.csv")
            with open(dest_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state["dataset_id"] = dataset_id
            st.success(f"File uploaded successfully! Dataset ID: `{dataset_id}`")
            
        with st.spinner("Agents are analyzing the dataset... This may take a moment."):
            try:
                # 2. Import agents directly from the codebase
                from agents.supervisor_agent import SupervisorAgent
                from agents.data_agent import DataAgent
                from agents.eda_agent import EDAGent
                from agents.business_agent import BusinessAgent
                
                # 3. Setup agents and execute
                agents_registry = {
                    "cleaning": DataAgent(),
                    "eda": EDAGent(),
                    "insight": BusinessAgent(),
                    "report": BusinessAgent(),
                }
                supervisor = SupervisorAgent(agents_registry)
                
                # 4. Run the analysis
                result = supervisor.execute(dataset_id, context={})
                
                # 5. Display Results
                st.subheader("Analysis Report")
                
                # Depending on what `result` is (dict or string), display it gracefully
                if isinstance(result, dict):
                    st.json(result)
                else:
                    st.write(result)
                    
                st.success("Analysis complete!")
                
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
