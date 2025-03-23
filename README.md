# Natural Language to SQL Query Streamlit App

This Streamlit application allows users to query a PostgreSQL database using natural language. It leverages the Google Gemini API to translate natural language questions into valid SQL queries, executes them against your database, and displays the results.

## Features

- **Natural Language Interface**: Ask questions about your data in plain English
- **SQL Translation**: Converts natural language to SQL using Google's Gemini API
- **Interactive Results**: View query results in an interactive table
- **SQL Preview**: Option to review the generated SQL before execution
- **Error Handling**: Comprehensive error handling for API and database operations
- **Security**: Secure handling of credentials via environment variables
- **Export Functionality**: Download query results as CSV

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Google Gemini API key

### Installation Steps

1. Clone this repository:
   ```
   git clone <repository-url>
   cd natural-language-sql-app
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory with your credentials:
   ```
   # Gemini API credentials
   GEMINI_API_KEY=your_gemini_api_key_here

   # Database connection parameters
   DB_NAME=your_database_name
   DB_USER=your_database_username
   DB_PASSWORD=your_database_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Usage

1. Enter your question in natural language in the text area.
2. Check "Show generated SQL query" if you want to review the SQL before execution.
3. Click "Generate & Execute Query" to process your request.
4. View the results in the interactive table.
5. Download the results as CSV if needed.

## Example Questions

- "Show me the top 5 customers by total purchase amount"
- "What were the sales figures for last month?"
- "Which products have the highest inventory levels?"
- "How many orders were placed in each region last quarter?"

## Architecture

The application is structured around three main components:

1. **Streamlit UI**: Handles user interaction and result visualization.
2. **Gemini API Integration**: Translates natural language to SQL.
3. **PostgreSQL Connection**: Executes queries and retrieves results.

## Security Considerations

- All sensitive information is stored in environment variables.
- Database queries use parameterized statements where applicable.
- API keys and database credentials are never exposed in the UI.

## Customization

You can customize the app by:

- Modifying the prompt template in `get_generated_sql()` to better fit your database schema
- Adjusting the UI layout in the `main()` function
- Adding additional data visualization options for specific query types

## License

[MIT License](LICENSE)