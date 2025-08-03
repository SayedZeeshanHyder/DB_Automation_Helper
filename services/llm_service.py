# services/llm_service.py

import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from utils.models import InitialAnalysisResponse

load_dotenv()


class LLMService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.api_key,
            temperature=0.1,
            convert_system_message_to_human=True
        )

    def _invoke_model(self, prompt: str) -> str:
        try:
            response = self.model([HumanMessage(content=prompt)])
            return response.content.strip()
        except Exception as e:
            raise RuntimeError(f"Error invoking Gemini API: {e}")

    def get_initial_analysis(self, prompt_template: str, user_prompt: str, db_url: str) -> InitialAnalysisResponse:
        formatted_prompt = prompt_template.format(prompt=user_prompt, database_url=db_url)
        response_str = self._invoke_model(formatted_prompt)
        try:
            cleaned_response = response_str.strip().replace("```json", "").replace("```", "")
            response_json = json.loads(cleaned_response)
            return InitialAnalysisResponse(**response_json)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Failed to parse initial analysis from LLM: {e}. Response: {response_str}")

    def generate_json_response(self, prompt_template: str, **kwargs) -> dict:
        formatted_prompt = prompt_template.format(**kwargs)
        response_str = self._invoke_model(formatted_prompt)
        try:
            cleaned_response = response_str.strip().replace("```json", "").replace("```", "")
            return json.loads(cleaned_response)
        except (json.JSONDecodeError, TypeError) as e:
            raise ValueError(f"Failed to parse JSON from LLM: {e}. Response: {response_str}")

    def generate_text_response(self, prompt_template: str, **kwargs) -> str:
        formatted_prompt = prompt_template.format(**kwargs)
        response_str = self._invoke_model(formatted_prompt)
        # Clean potential markdown code blocks for SQL and reports
        cleaned_response = response_str.strip().replace("```sql", "").replace("```markdown", "").replace("```", "")
        return cleaned_response


llm_service = LLMService()