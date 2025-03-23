import streamlit as st
import os
import psycopg2
import pandas as pd
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(override=True) 

# Configure Gemini API
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash')
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    st.error("Failed to initialize Gemini API. Please check your API key.")

# Database connection parameters
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT", "5432")
}

def get_db_schema():
    """Fetch the database schema to provide context for the Gemini API"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        schema_info = []
        for table in tables:
            table_name = table[0]
            # Get column information for each table
            cursor.execute(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = '{table_name}'
            """)
            columns = cursor.fetchall()
            
            column_info = [f"{col[0]} ({col[1]})" for col in columns]
            schema_info.append(f"Table: {table_name}\nColumns: {', '.join(column_info)}")
        
        conn.close()
        return "\n\n".join(schema_info)
    except Exception as e:
        logger.error(f"Failed to fetch database schema: {e}")
        return "Error fetching schema"

def get_generated_sql(natural_language_query):
    """
    Call the Gemini API to convert natural language query to SQL
    
    Args:
        natural_language_query (str): User's natural language question
        
    Returns:
        str: Generated SQL query or error message
    """
    try:
        # Get database schema for context
        schema = get_db_schema()
        
        # Prompt template for Gemini
        prompt = f"""
        You are a specialized SQL query generator. Convert the following natural language question into a valid PostgreSQL SQL query.
        
        Database Schema:
        {schema}
        
        Natural Language Question:
        {natural_language_query}
        
        Rules:
        1. Generate ONLY the SQL query without any additional text, explanations, or markdown.
        2. Ensure the query is valid PostgreSQL syntax.
        3. Use JOINs where appropriate when querying multiple tables.
        4. Use column names exactly as they appear in the schema.
        5. Keep the query efficient and focused on answering the specific question.
        6. When appropriate, include ORDER BY, GROUP BY, or LIMIT clauses to make the results more useful.
        7. Do not include any SQL comments in the query.
        
        SQL Query:
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Error generating SQL: {str(e)}"

def execute_query(sql_query):
    """
    Execute the SQL query on the PostgreSQL database
    
    Args:
        sql_query (str): SQL query to execute
        
    Returns:
        tuple: (success (bool), results (pd.DataFrame) or error message (str))
    """
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        # Use pandas to execute query and return results as DataFrame
        results = pd.read_sql_query(sql_query, conn)
        conn.close()
        return True, results
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False, f"Error executing query: {str(e)}"

def display_results(success, results):
    """
    Display query results or error message using Streamlit
    
    Args:
        success (bool): Whether the query execution was successful
        results (pd.DataFrame or str): Query results or error message
    """
    if success:
        if len(results) == 0:
            st.info("Query executed successfully, but returned no results.")
        else:
            st.success(f"Query returned {len(results)} results.")
            st.dataframe(results)
            
            # Option to download results as CSV
            csv = results.to_csv(index=False)
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
    else:
        st.error(results)  # Display error message

def main():
    st.set_page_config(
        page_title="Natural Language to SQL Query App",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("Natural Language to SQL Query App")
    
    # Sidebar with app information
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This app converts your natural language questions into SQL queries and executes them against a PostgreSQL database.
        
        **How to use:**
        1. Type your question in the text input
        2. Review the generated SQL (optional)
        3. Execute the query and view results
        
        **Example questions:**
        - Show me the top 5 customers by total purchase amount
        - What were the sales figures for last month?
        - Which products have the highest inventory levels?
        """)
        
        st.header("Database Information")
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            st.success("✅ Connected to database")
            conn.close()
            
            # Display basic schema info
            schema_info = get_db_schema()
            with st.expander("View Database Schema"):
                st.code(schema_info)
                
        except Exception as e:
            st.error(f"❌ Database connection failed: {e}")
    
    # Main app area
    st.header("Ask a question about your data")
    query = st.text_area("Enter your question in plain English:", height=100)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        execute_button = st.button("Generate & Execute Query", type="primary")
    
    with col2:
        show_sql = st.checkbox("Show generated SQL query", value=True)
    
    if execute_button and query:
        with st.spinner("Generating SQL query..."):
            sql_query = get_generated_sql(query)
        
        if not sql_query.startswith("Error"):
            if show_sql:
                with st.expander("Generated SQL Query", expanded=True):
                    st.code(sql_query, language="sql")
            
            with st.spinner("Executing query..."):
                success, results = execute_query(sql_query)
                display_results(success, results)
        else:
            st.error(sql_query)
    
    # Footer
    st.markdown("---")
    st.caption("Powered by Streamlit, PostgreSQL, and Google Gemini")

if __name__ == "__main__":
    main()