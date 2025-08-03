# prompts/prompt_templates.py

INITIAL_ANALYSIS_PROMPT = """
Analyze the user's prompt and the database URL to determine the required actions.
Respond ONLY with a valid JSON object in the following format, with no additional text or explanations.

User Prompt: "{prompt}"
Database URL: "{database_url}"

JSON Format:
{{
  "database_type": "SQL or NoSQL",
  "database_name": "postgresql, mysql, or mongodb",
  "isEmailRequired": boolean,
  "isReportGenerationRequired": boolean,
  "isVisualizationRequired": boolean
}}

Analyze the prompt for keywords like "send email", "email all users", "report", "summarize", "visualize", "graph", "chart", etc. to determine the boolean flags.
Based on the database URL scheme ('postgresql', 'mysql', 'mongodb'), determine the database_type and database_name.
"""

SQL_GENERATION_PROMPT = """
You are an expert SQL engineer. Your task is to generate a single, highly efficient, and 100% syntactically correct SQL query for the user's request.

DO NOT generate any text, explanation, or markdown formatting around the query. Only output the raw SQL query.
IMPORTANT: If the user asks for "everything", "all data", or "all users" from a table, generate a `SELECT * FROM your_table_name;` query.

Database Dialect: {dialect}
Database Schema:
{schema}

User's Request: "{prompt}"

Generated SQL Query:
"""

NOSQL_GENERATION_PROMPT = """
You are an expert NoSQL database engineer specializing in MongoDB. Your task is to generate a Python dictionary that represents a valid PyMongo query based on the user's request. You must also determine the target collection from the schema provided.

DO NOT generate any text, explanation, or markdown formatting around the JSON. Only output a single, raw JSON object in the specified format.

IMPORTANT: Based on the user's prompt (e.g., 'find all users'), you MUST infer the most likely collection name from the provided schema (e.g., 'users', 'customers'). If the user requests "everything", "all documents", or "all users", the "query" filter should be an empty dictionary: {{}}.

Database Collections and Sample Documents (Schema):
{schema}

User's Request: "{prompt}"

JSON Output Format:
{{
  "collection": "target_collection_name",
  "query": {{ "your_pymongo_query_filter": "value" }}
}}
"""

EMAIL_GENERATION_PROMPT = """
You are a marketing and communications expert. Based on the user's request and the provided data, generate professional and aesthetic email content.

The output must be a single, valid JSON object with no surrounding text or explanations.

The JSON must contain two keys: "subject" and "body". The "body" must be a single string of HTML content.
If the request implies sending a unique email to each recipient (e.g., using their name), use placeholders in the format {{column_name}}. The system will replace these placeholders for each recipient.

User's Request: "{prompt}"
Query Result Data:
{query_result}

JSON Output Format:
{{
  "subject": "Your Compelling Email Subject",
  "body": "<html>...Your aesthetic HTML content with placeholders like {{name}} or {{order_count}}...</html>"
}}
"""

REPORT_GENERATION_PROMPT = """
You are a professional data analyst. Your task is to generate a comprehensive and well-structured report based on the user's request and the provided data.

The output should be in Markdown format. The report must be easy to read, professional, and provide clear insights. Include a title, summary, key findings, and detailed sections as appropriate.

User's Request: "{prompt}"
Query Result Data:
{query_result}

Generated Markdown Report:
"""

VISUALIZATION_GENERATION_PROMPT = """
You are a data visualization expert. Your task is to suggest the best way to visualize the given data to answer the user's request.
You must generate a configuration for a chart using the Chart.js library format.

The output must be a single, valid JSON object representing the Chart.js configuration, with no surrounding text or explanations.
Choose the most appropriate chart type (bar, line, pie, doughnut, etc.).
The JSON should have 'type', 'data', and 'options' keys.

User's Request: "{prompt}"
Query Result Data:
{query_result}

Generated Chart.js JSON:
"""