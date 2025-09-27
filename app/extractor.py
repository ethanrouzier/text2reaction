import os
from typing import Optional
from mistralai import Mistral
from .models import ReactionSet
from .prompts import SYSTEM_PROMPT, USER_INSTRUCTIONS

MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

class LLMExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.client = Mistral(api_key=api_key or os.environ.get("MISTRAL_API_KEY", ""))

    def extract(self, doc_title: str, section_title: str, section_text: str, source_url: Optional[str] = None) -> ReactionSet:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_INSTRUCTIONS + "\n\n" + f"DOCUMENT_TITLE: {doc_title}\nSECTION_TITLE: {section_title}\nSOURCE_URL: {source_url or ''}\n\nEXPERIMENTAL:\n" + section_text},
        ]
        resp = self.client.chat.complete(
            model=MODEL,
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = resp.choices[0].message.content
        return ReactionSet.model_validate_json(content)
