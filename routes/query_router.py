# routes/query_router.py

from fastapi import APIRouter, HTTPException
from utils.models import QueryRequest
from services.llm_service import llm_service
from services import db_service
# --- THE FIX IS HERE ---
# We now explicitly import the email_service INSTANCE from the email_service MODULE.
from services.email_service import email_service
from prompts import prompt_templates
import json

router = APIRouter()


@router.post("/query")
async def handle_query(request: QueryRequest):
    final_response = {}
    schema = None

    try:
        # --- [1] ---
        print("\n--- [1] Query request received. Starting initial analysis... ---")
        analysis = llm_service.get_initial_analysis(
            prompt_templates.INITIAL_ANALYSIS_PROMPT,
            user_prompt=request.prompt,
            db_url=request.database_url
        )
        final_response['analysis'] = analysis.model_dump()
        # --- [2] ---
        print(
            f"--- [2] Initial analysis successful. DB Type from AI: '{analysis.database_type}'. Fetching schema... ---")

        # Attempt to fetch schema and handle connection errors immediately
        try:
            # Normalize the database_type to be lowercase and stripped of whitespace for robust matching.
            if analysis.database_type:
                db_type_normalized = analysis.database_type.lower().strip()
            else:
                db_type_normalized = ""

            if db_type_normalized == 'sql':
                schema = db_service.get_sql_schema(request.database_url)
            elif db_type_normalized == 'nosql':
                schema = db_service.get_nosql_schema(request.database_url)

            # This print will only be reached if one of the above conditions is met and doesn't error
            if schema is not None:
                print("--- [3] Database schema fetched successfully. Generating query... ---")

        except ConnectionError as e:
            # If connection fails, add the specific error to the response and return.
            final_response['database_connection_error'] = str(e)
            print(f"--- [!] DATABASE CONNECTION FAILED: {e} ---")
            return final_response

        # This block now robustly checks the outcome of the schema fetching.
        if schema is None:
            # This happens if the database_type was not 'sql' or 'nosql'.
            error_msg = f"Could not determine schema. The initial analysis identified an unsupported or empty database type: '{analysis.database_type}'"
            final_response['schema_fetching_error'] = error_msg
            print(f"--- [!] SCHEMA FETCHING FAILED: {error_msg} ---")
            return final_response

        print(f"--- [DEBUG] Schema size: {len(schema)} characters. Sending to Gemini for query generation... ---")

        # Handle case where database is empty (no tables/collections)
        if not schema.strip():
            final_response[
                'query_execution_error'] = "Database schema is empty. The database might not have any tables or collections."
            print("--- [!] SCHEMA IS EMPTY. Cannot generate query. ---")
            return final_response

        # Phase 2: Query Generation & Execution (will only run if schema fetch was successful)
        query_result = []
        generated_query_obj = None

        if db_type_normalized == 'sql':
            sql_query = llm_service.generate_text_response(
                prompt_templates.SQL_GENERATION_PROMPT,
                dialect=analysis.database_name,
                schema=schema,
                prompt=request.prompt
            )
            # --- [4] ---
            print("--- [4] Query generation successful. Preparing to execute... ---")
            generated_query_obj = sql_query
            final_response['generated_query'] = sql_query

            # --- [5] ---
            print("=" * 50)
            print(f"--- [5] EXECUTING SQL QUERY:\n{sql_query}")
            print("=" * 50)

            try:
                query_result = db_service.execute_sql_query(request.database_url, sql_query)
                print("--- [6] Query execution complete. ---")
            except Exception as e:
                final_response['query_execution_error'] = f"Failed to execute SQL query: {e}"

        elif db_type_normalized == 'nosql':
            nosql_gen_json = llm_service.generate_json_response(
                prompt_templates.NOSQL_GENERATION_PROMPT,
                schema=schema,
                prompt=request.prompt
            )
            # --- [4] ---
            print("--- [4] Query generation successful. Preparing to execute... ---")
            generated_query_obj = nosql_gen_json
            final_response['generated_query'] = nosql_gen_json

            collection = nosql_gen_json.get('collection')
            query_filter = nosql_gen_json.get('query')

            # --- [5] ---
            print("=" * 50)
            print(f"--- [5] EXECUTING NOSQL QUERY:\n{json.dumps(nosql_gen_json, indent=2)}")
            print("=" * 50)

            if not collection or query_filter is None:
                final_response['query_execution_error'] = "LLM failed to generate a valid collection or query filter."
            else:
                try:
                    query_result = db_service.execute_nosql_query(request.database_url, collection, query_filter)
                    print("--- [6] Query execution complete. ---")
                except Exception as e:
                    final_response['query_execution_error'] = f"Failed to execute NoSQL query: {e}"

        final_response['query_result'] = query_result
        if not query_result and 'query_execution_error' not in final_response:
            final_response[
                'query_result_message'] = "Query executed successfully but returned no results. The generated query might be logically incorrect for the data."

        # Phase 3: Post-Query Tools
        if analysis.isEmailRequired and query_result:
            email_json = llm_service.generate_json_response(
                prompt_templates.EMAIL_GENERATION_PROMPT,
                prompt=request.prompt,
                query_result=json.dumps(query_result[:5], indent=2)
            )
            subject = email_json.get('subject', 'Important Update')
            body_template = email_json.get('body', '<p>Hello!</p>')
            email_status = email_service.send_emails(
                recipients=[],
                subject=subject,
                html_body_template=body_template,
                data=query_result
            )
            final_response['email_status'] = email_status

        if analysis.isReportGenerationRequired and query_result:
            report_markdown = llm_service.generate_text_response(
                prompt_templates.REPORT_GENERATION_PROMPT,
                prompt=request.prompt,
                query_result=json.dumps(query_result, indent=2)
            )
            final_response['report_status'] = "Report generated successfully."
            final_response['report'] = report_markdown

        if analysis.isVisualizationRequired and query_result:
            visual_json = llm_service.generate_json_response(
                prompt_templates.VISUALIZATION_GENERATION_PROMPT,
                prompt=request.prompt,
                query_result=json.dumps(query_result, indent=2)
            )
            final_response['visual_status'] = "Visualization generated successfully."
            final_response['visual'] = visual_json

        return final_response

    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        error_detail = {"error": "An unexpected error occurred in the main router.", "detail": str(e)}
        if 'generated_query_obj' in locals() and generated_query_obj:
            error_detail['generated_query_that_failed'] = generated_query_obj
        raise HTTPException(status_code=500, detail=error_detail)