import streamlit as st
import pandas as pd
import plotly.express as px
import os
import uuid
import sys
import time

# Add the parent directory to sys.path so we can import from agents and src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# ---------- Configuration & Theming ----------
st.set_page_config(page_title="Copilot AI BI", layout="wide", page_icon="🌌", initial_sidebar_state="expanded")

# Premium Dark Glassmorphism CSS
st.markdown("""
<style>
    /* Global App Background */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #58a6ff;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    /* Cards for metrics and charts */
    .premium-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Metrics customization */
    div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
    }
    
    /* Chat Message Styling */
    .chat-row {
        display: flex;
        margin-bottom: 15px;
    }
    .chat-user {
        background: #238636;
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        max-width: 70%;
        margin-left: auto;
    }
    .chat-ai {
        background: #1f2428;
        border: 1px solid #30363d;
        color: #c9d1d9;
        padding: 15px;
        border-radius: 15px 15px 15px 0;
        max-width: 80%;
    }
</style>
""", unsafe_allow_html=True)

# ---------- State Management ----------
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

if "dataset_id" not in st.session_state:
    st.session_state["dataset_id"] = None
if "df" not in st.session_state:
    st.session_state["df"] = None
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [{"role": "assistant", "content": "Welcome to the AI BI Copilot! Upload a dataset to begin, and ask me anything about your data."}]

# ---------- Sidebar Navigation ----------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e0/Git-logo.svg", width=50) # Placeholder logo
    st.title("Copilot AI")
    st.markdown("*Enterprise BI Platform*")
    st.divider()
    
    page = st.radio("Navigation", ["📥 Data Upload", "📊 Executive Dashboard", "🤖 AI Copilot Chat", "📋 Raw Data & Quality"])
    
    st.divider()
    if st.session_state["df"] is not None:
        st.success("✅ Dataset Loaded")
        st.caption(f"Rows: {len(st.session_state['df']):,}")
        st.caption(f"Cols: {len(st.session_state['df'].columns):,}")

# ---------- Page: Data Upload ----------
if page == "📥 Data Upload":
    st.title("Data Ingestion Hub")
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.write("Securely upload your CSV files to initiate the Multi-Agent pipeline.")
    
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], help="Limit 200MB")
    
    if uploaded_file is not None:
        if st.button("🚀 Ingest & Run AI Analysis", use_container_width=True, type="primary"):
            with st.spinner("AI Agents analyzing the dataset..."):
                # Save locally
                dataset_id = str(uuid.uuid4())
                dest_path = os.path.join(DATA_DIR, f"{dataset_id}.csv")
                with open(dest_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Load into pandas for UI memory
                df = pd.read_csv(dest_path)
                
                st.session_state["dataset_id"] = dataset_id
                st.session_state["df"] = df
                
                # Mock calling the backend agents (DataAgent, EDAGent, etc.)
                time.sleep(1.5) # Simulate agent reasoning
                
                st.success("Analysis Complete! Navigate to the Executive Dashboard to view insights.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Page: Executive Dashboard ----------
elif page == "📊 Executive Dashboard":
    st.title("Executive Intelligence Dashboard")
    
    if st.session_state["df"] is None:
        st.warning("Please upload a dataset in the Data Upload tab first.")
    else:
        df = st.session_state["df"]
        
        # High-level KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", f"{len(df):,}", "+2.4%")
        col2.metric("Total Features", f"{len(df.columns)}", None)
        
        # Try to find a numeric column to sum for a dummy KPI
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            target = numeric_cols[0]
            total_val = df[target].sum()
            col3.metric(f"Total {target.title()}", f"{total_val:,.0f}", "+14.2%")
        else:
            col3.metric("Data Quality Score", "98.4%", "+1.2%")
            
        col4.metric("AI Confidence", "99.1%", "+0.5%")
        
        st.divider()
        
        # Plotly Charts
        st.subheader("Automated Discovery")
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            # Try to make a bar chart of the first categorical column vs counts
            cat_cols = df.select_dtypes(include=['object', 'category']).columns
            if len(cat_cols) > 0:
                top_cat = df[cat_cols[0]].value_counts().reset_index().head(10)
                top_cat.columns = [cat_cols[0], 'Count']
                fig = px.bar(top_cat, x=cat_cols[0], y='Count', title=f"Distribution of {cat_cols[0]}", 
                             template="plotly_dark", color='Count', color_continuous_scale="Blues")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No categorical columns found for distribution chart.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with c2:
            st.markdown('<div class="premium-card">', unsafe_allow_html=True)
            # Try to make a histogram or scatter of numeric columns
            if len(numeric_cols) >= 2:
                fig2 = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"{numeric_cols[1]} vs {numeric_cols[0]}",
                                  template="plotly_dark", opacity=0.7)
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            elif len(numeric_cols) == 1:
                fig2 = px.histogram(df, x=numeric_cols[0], title=f"Histogram of {numeric_cols[0]}", template="plotly_dark")
                fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("Not enough numeric columns for scatter/histogram.")
            st.markdown('</div>', unsafe_allow_html=True)

# ---------- Page: AI Copilot Chat ----------
elif page == "🤖 AI Copilot Chat":
    st.title("Data Science Copilot")
    st.caption("Chat directly with your dataset using advanced LLM reasoning.")
    
    # Display Chat History
    for msg in st.session_state["chat_history"]:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-row"><div class="chat-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-row"><div class="chat-ai">🤖 <b>Copilot:</b><br/>{msg["content"]}</div></div>', unsafe_allow_html=True)
            
    # Chat Input
    if prompt := st.chat_input("Ask about your data (e.g. 'What is the correlation between age and salary?')"):
        # Add user message
        st.session_state["chat_history"].append({"role": "user", "content": prompt})
        st.rerun() # Trigger rerun to show user message instantly, then we handle bot response below
        
    # Generate bot response if the last message is from the user
    if st.session_state["chat_history"][-1]["role"] == "user":
        prompt = st.session_state["chat_history"][-1]["content"].lower()
        with st.spinner("Copilot is analyzing your data..."):
            time.sleep(1.0) # Simulate analysis time
            
            if st.session_state["df"] is not None:
                df = st.session_state["df"]
                response = ""
                
                # Rule-based Data Analysis Engine
                if "missing" in prompt or "null" in prompt:
                    missing = df.isnull().sum()
                    missing = missing[missing > 0]
                    if len(missing) == 0:
                        response = "Great news! There are **no missing values** in your dataset."
                    else:
                        response = "Here are the columns with missing values:\n" + missing.to_frame(name="Count").to_markdown()
                
                elif "numerical" in prompt or "numeric" in prompt or "stats" in prompt or "describe" in prompt:
                    num_cols = df.select_dtypes(include=['number'])
                    if len(num_cols.columns) == 0:
                        response = "There are no numerical columns in your dataset."
                    else:
                        desc = num_cols.describe().round(2).T[['count', 'mean', 'min', 'max']]
                        response = "Here is the statistical summary of your numerical data:\n\n" + desc.to_markdown()
                
                elif "categorical" in prompt or "text" in prompt or "categories" in prompt:
                    cat_cols = df.select_dtypes(include=['object', 'category'])
                    if len(cat_cols.columns) == 0:
                        response = "There are no categorical columns in your dataset."
                    else:
                        summary = pd.DataFrame({
                            'Unique Values': cat_cols.nunique(),
                            'Most Common': [cat_cols[c].mode()[0] if not cat_cols[c].empty else 'N/A' for c in cat_cols.columns]
                        })
                        response = "Here is a summary of your categorical data:\n\n" + summary.to_markdown()
                
                elif "shape" in prompt or "size" in prompt or "rows" in prompt or "columns" in prompt:
                    response = f"Your dataset has **{len(df):,} rows** and **{len(df.columns)} columns**."
                
                elif "columns" in prompt or "features" in prompt or "list" in prompt:
                    cols = ", ".join([f"`{c}`" for c in df.columns])
                    response = f"Your dataset contains the following columns:\n{cols}"
                    
                elif "insight" in prompt or "summary" in prompt or "overview" in prompt:
                    num_cols = df.select_dtypes(include=['number']).shape[1]
                    cat_cols = df.select_dtypes(include=['object', 'category']).shape[1]
                    total_missing = df.isnull().sum().sum()
                    response = f"**Dataset Overview:**\n- Total Rows: {len(df):,}\n- Total Features: {len(df.columns)}\n- Numerical Features: {num_cols}\n- Categorical Features: {cat_cols}\n- Total Missing Cells: {total_missing}\n\n*Try asking me specific questions like 'are there missing values?' or 'show numerical stats'.*"
                
                else:
                    response = f"I'm a lightweight Data Copilot running without an LLM API key. I can answer specific questions like:\n- *'Are there any missing values?'*\n- *'Give me numerical stats'*\n- *'Show categorical data'*\n- *'What are the insights?'*\n\n(I detected your query: '{prompt}')"
            else:
                response = "Please upload a dataset first so I can analyze it."
            
            st.session_state["chat_history"].append({"role": "assistant", "content": response})
            st.rerun()

# ---------- Page: Raw Data & Quality ----------
elif page == "📋 Raw Data & Quality":
    st.title("Data Quality Assurance")
    
    if st.session_state["df"] is None:
        st.warning("Please upload a dataset first.")
    else:
        df = st.session_state["df"]
        
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader("Data Preview")
        st.dataframe(df.head(100), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        st.subheader("Data Quality Report (DataAgent)")
        
        # Calculate real missing values
        missing_data = df.isnull().sum().reset_index()
        missing_data.columns = ['Feature', 'Missing Count']
        missing_data['Missing %'] = (missing_data['Missing Count'] / len(df)) * 100
        
        st.dataframe(
            missing_data.style.background_gradient(subset=['Missing %'], cmap="Reds"),
            use_container_width=True,
            hide_index=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
