# AI-Powered Database Querying System 🤖

A robust, AI-driven system that allows users to interact with SQL and NoSQL databases using natural language. This application translates plain English prompts into executable database queries, generates reports, creates visualizations, and sends emails automatically.

---

## 🚀 Key Features

* **Natural Language Querying:** Ask complex questions in English to query your SQL (PostgreSQL, MySQL) or NoSQL (MongoDB) databases.
* **Automated Analysis:** The system automatically determines the user's intent—whether they need a simple query, a report, a visualization, or to send emails.
* **Dynamic Query Generation:** Leverages Google's Gemini LLM via LangChain to generate efficient and syntactically correct SQL queries or PyMongo query objects.
* **Built-in Tools:**
    * **Report Generation:** Creates detailed, professional reports in Markdown based on the query results.
    * **Data Visualization:** Generates Chart.js configurations for frontend data visualization.
    * **Email Service:** Sends personalized bulk emails to users identified in a query.
* **Minimalist Frontend:** A clean, single-page interface for interacting with the API.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI
* **AI Model:** Google Gemini 1.5 Flash
* **Orchestration:** LangChain
* **Databases:**
    * **SQL:** SQLAlchemy (for schema reflection), Psycopg2 (PostgreSQL), PyMySQL (MySQL)
    * **NoSQL:** PyMongo (MongoDB)
* **Environment:** Python-Dotenv
* **Web Server:** Uvicorn

---

## 📂 Project Structure

```
.
├── .env
├── requirements.txt
├── main.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── routes/
│   └── query_router.py
├── services/
│   ├── db_service.py
│   ├── email_service.py
│   └── llm_service.py
├── prompts/
│   └── prompt_templates.py
└── utils/
    ├── error_handlers.py
    └── models.py
```

---

## ⚙️ Setup and Installation

Follow these steps to get the project running locally.

### 1. Clone the Repository

```bash
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name
```

### 2. Create and Activate a Virtual Environment (Recommended)

```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory. You can copy the example:

```bash
# For Windows
copy .env.example .env

# For macOS/Linux
cp .env.example .env
```

Now, open the `.env` file and fill in your credentials.

---

## 🔑 Configuration

Your `.env` file must contain the following keys:

* **`GEMINI_API_KEY`**: Your API key from Google AI Studio.
* **`EMAIL_HOST`**: The SMTP host for your email provider (e.g., `smtp.gmail.com`).
* **`EMAIL_PORT`**: The SMTP port (e.g., `587` for Gmail).
* **`EMAIL_HOST_USER`**: Your email address.
* **`EMAIL_HOST_PASSWORD`**: Your email app password (for Gmail, this is required if you have 2FA enabled).
* **`EMAIL_SENDER_NAME`**: The name you want to appear as the sender.

---

## ▶️ Running the Application

1.  **Start the Backend Server:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.

2.  **Launch the Frontend:**
    Open the `frontend/index.html` file in your web browser.

---

## 📖 API Usage

The system exposes a single primary endpoint for all operations.

### POST `/api/query`

This endpoint accepts a JSON body with the database connection URL and a natural language prompt.

**Request Body:**
```json
{
  "database_url": "your_database_connection_string",
  "prompt": "your_natural_language_question"
}
```

**Example `curl` Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/api/query' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "database_url": "postgresql://user:pass@localhost/mydatabase",
    "prompt": "Generate a report of all users from New York who signed up in 2025"
  }'
```

**Successful Response:**
The API will return a JSON object containing the results of the requested actions, which may include `query_result`, `report`, `visual`, and `email_status`.

---

## 🧠 How It Works

The application follows a sequential, multi-step process for each request:

1.  **Initial Analysis:** The user's prompt and database URL are sent to the Gemini LLM to determine the core tasks required (querying, reporting, emailing, etc.) and the database type.
2.  **Schema Fetching:** The system connects to the specified database and programmatically extracts its schema (table structures for SQL, sample documents for NoSQL). This provides context for the AI.
3.  **Query Generation:** The schema, user prompt, and specific instructions are sent back to the LLM in a detailed prompt, asking it to generate an efficient and correct SQL or NoSQL query.
4.  **Database Execution:** The generated query is executed against the database, and the results are sanitized to handle non-serializable data types like `datetime` and `bytes`.
5.  **Post-Processing Tools:** If requested in the initial analysis, the query results are passed to other LLM-powered tools to generate reports, email content, or visualization data.
6.  **Final Response:** A consolidated JSON object containing all the generated artifacts is returned to the user.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
