"""
SQLCoder Text-to-SQL Frontend
Streamlit application for natural language to SQL conversion
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="SQLCoder Text-to-SQL",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .query-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .result-box {
        background-color: #e8f4fd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffe6e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        color: #d32f2f;
    }
    .sql-code {
        background-color: #2d2d2d;
        color: #ffffff;
        padding: 1rem;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_connection():
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def generate_sql_query(question: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-sql",
            json={"question": question},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def execute_query(question: str):
    try:
        response = requests.post(
            f"{API_BASE_URL}/execute-query",
            json={"question": question},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def get_database_schema():
    try:
        response = requests.get(f"{API_BASE_URL}/schema", timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def main():
    # Header
    st.markdown('<h1 class="main-header">🗃️ SQLCoder Text-to-SQL</h1>', unsafe_allow_html=True)
    st.markdown("### Convert your questions into SQL queries using AI")

    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")

        api_connected = check_api_connection()
        if api_connected:
            st.success("✅ Backend API Connected")
        else:
            st.error("❌ Backend API Disconnected")
            st.warning("Make sure the backend is running on http://localhost:8000")

        st.divider()

        st.header("💡 Example Questions")
        example_questions = [
    "Show all employees in the Engineering department.",
    "List all projects handled by the HR department.",
    "Find employees with salary above ₹60,000.",
    "How many employees were present on 2025-11-08?",
    "Which employee has the highest salary in TechCorp?",
    "List all projects and their respective departments.",
    "Show total number of employees in each department.",
    "Find employees who joined after 2022.",
    "Display attendance records for November 2025.",
    "Show all projects managed by the Finance department."
]


        selected_example = st.selectbox(
            "Choose an example:",
            [""] + example_questions,
            index=0
        )

        if selected_example:
            st.session_state.selected_question = selected_example

        st.divider()

        st.header("📋 Database Schema")
        if st.button("🔄 Load Schema"):
            with st.spinner("Loading schema..."):
                schema_data = get_database_schema()
                if "error" not in schema_data:
                    st.session_state.schema = schema_data.get("schema", {})
                else:
                    st.error(f"Error loading schema: {schema_data['error']}")

        if "schema" in st.session_state:
            for table_name, columns in st.session_state.schema.items():
                with st.expander(f"📊 {table_name}"):
                    for col in columns:
                        col_type = col["type"]
                        is_pk = "🔑" if col.get("primary_key", False) else ""
                        st.text(f"{is_pk} {col['name']} ({col_type})")

    # Main content area
    col1, col2 = st.columns([3, 1])

    with col1:
        st.header("❓ Ask Your Question")

        default_question = st.session_state.get("selected_question", "")

        user_question = st.text_area(
            "Enter your question in plain English:",
            value=default_question,
            height=100,
            placeholder="e.g., Show me all customers from Mumbai with purchases over ₹5000"
        )

        if "selected_question" in st.session_state:
            del st.session_state.selected_question

    with col2:
        st.header("🎛️ Actions")

        generate_only = st.button(
            "🔧 Generate SQL Only",
            use_container_width=True,
            disabled=not api_connected or not user_question.strip()
        )

        execute_query_btn = st.button(
            "▶️ Generate & Execute",
            use_container_width=True,
            disabled=not api_connected or not user_question.strip(),
            type="primary"
        )

        if st.button("🗑️ Clear Results", use_container_width=True):
            keys_to_clear = ["sql_result", "execution_result", "last_question"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    # Process user actions
    if generate_only and user_question.strip():
        with st.spinner("🔄 Generating SQL query..."):
            result = generate_sql_query(user_question)
            st.session_state.sql_result = result
            st.session_state.last_question = user_question

    if execute_query_btn and user_question.strip():
        with st.spinner("🔄 Generating and executing SQL query..."):
            result = execute_query(user_question)
            st.session_state.execution_result = result
            st.session_state.last_question = user_question

    st.divider()

    # Show SQL generation result
    if "sql_result" in st.session_state:
        st.header("🔧 Generated SQL Query")
        result = st.session_state.sql_result

        if "error" in result and result["error"]:
            st.markdown(f'<div class="error-box">❌ Error: {result["error"]}</div>', unsafe_allow_html=True)
        else:
            if "execution_time" in result:
                st.caption(f"⏱️ Generated in {result['execution_time']:.3f} seconds")

            sql_query = result.get("sql_query", "")
            st.markdown(f'<div class="sql-code">{sql_query}</div>', unsafe_allow_html=True)
            st.code(sql_query, language="sql")

    # Show execution result
    if "execution_result" in st.session_state:
        st.header("📊 Query Results")
        result = st.session_state.execution_result

        if "error" in result and result["error"]:
            st.markdown(f'<div class="error-box">❌ Error: {result["error"]}</div>', unsafe_allow_html=True)
        else:
            if "execution_time" in result:
                st.caption(f"⏱️ Executed in {result['execution_time']:.3f} seconds")

            sql_query = result.get("sql_query", "")
            with st.expander("🔍 View SQL Query", expanded=False):
                st.code(sql_query, language="sql")

            results = result.get("results", [])
            if results:
                if isinstance(results[0], dict) and "message" in results[0]:
                    st.success(results[0]["message"])
                    if "rows_affected" in results[0]:
                        st.info(f"Rows affected: {results[0]['rows_affected']}")
                else:
                    df = pd.DataFrame(results)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📝 Rows Returned", len(df))
                    with col2:
                        st.metric("🏗️ Columns", len(df.columns) if not df.empty else 0)
                    with col3:
                        st.metric("💾 Size", f"{df.memory_usage(deep=True).sum()} bytes")

                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True
                    )

                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No results returned from the query.")

    st.divider()
    st.markdown("### 🚀 Powered by SQLCoder & Streamlit")
    st.markdown("""
    **Instructions:**
    1. Make sure the backend API is running (`python backend/main.py`)
    2. Type your question in natural language
    3. Click "Generate & Execute" to get results
    4. Use the sidebar to explore example questions and database schema
    """)


if __name__ == "__main__":
    main()
