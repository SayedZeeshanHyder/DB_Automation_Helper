# services/db_service.py

from sqlalchemy import create_engine, inspect, text
from pymongo import MongoClient
from urllib.parse import urlparse
import json
import datetime  # Import the datetime module


def get_db_details(db_url: str):
    parsed_url = urlparse(db_url)
    scheme = parsed_url.scheme.lower()
    if 'postgres' in scheme:
        return 'sql', 'postgresql'
    elif 'mysql' in scheme:
        return 'sql', 'mysql'
    elif 'mongodb' in scheme:
        return 'nosql', 'mongodb'
    raise ValueError(f"Unsupported database scheme: {scheme}")


def get_sql_schema(db_url: str) -> str:
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        schema_info = []
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            column_details = [f"{col['name']} ({col['type']})" for col in columns]
            schema_info.append(f"Table: {table_name}\nColumns: {', '.join(column_details)}")
        return "\n\n".join(schema_info)
    except Exception as e:
        raise ConnectionError(f"Failed to connect to SQL database or inspect schema: {e}")


def get_nosql_schema(db_url: str) -> str:
    try:
        client = MongoClient(db_url)
        db_name = urlparse(db_url).path.lstrip('/')
        db = client[db_name]
        schema_info = []
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            first_doc = collection.find_one()
            if first_doc:
                first_doc.pop('_id', None)
                schema_info.append(
                    f"Collection: {collection_name}\nSample Document: {json.dumps(first_doc, indent=2, default=str)}")
        client.close()
        return "\n\n".join(schema_info)
    except Exception as e:
        raise ConnectionError(f"Failed to connect to NoSQL database or inspect schema: {e}")


def execute_sql_query(db_url: str, query: str) -> list[dict]:
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            result_proxy = connection.execute(text(query))

            results = []
            for row in result_proxy:
                row_dict = dict(row._mapping)
                for key, value in row_dict.items():
                    # Handle datetime objects
                    if isinstance(value, (datetime.datetime, datetime.date)):
                        row_dict[key] = value.isoformat()
                    # --- THE FIX IS HERE ---
                    # Handle bytes objects
                    elif isinstance(value, bytes):
                        try:
                            # Try to decode bytes into a UTF-8 string
                            row_dict[key] = value.decode('utf-8')
                        except UnicodeDecodeError:
                            # If it's not text (e.g., an image), use a safe placeholder
                            row_dict[key] = '<Binary Data>'
                    # --- END OF FIX ---
                results.append(row_dict)

            return results
    except Exception as e:
        raise RuntimeError(f"Error executing SQL query: {e}")


def execute_nosql_query(db_url: str, collection_name: str, query_filter: dict) -> list[dict]:
    try:
        client = MongoClient(db_url)
        db_name = urlparse(db_url).path.lstrip('/')
        db = client[db_name]
        collection = db[collection_name]
        results = [json.loads(json.dumps(doc, default=str)) for doc in collection.find(query_filter)]
        client.close()
        return results
    except Exception as e:
        raise RuntimeError(f"Error executing NoSQL query: {e}")