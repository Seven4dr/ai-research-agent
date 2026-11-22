import os
import json
import re
import time
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from app.core.config import settings

class LLMService:
    """Service d'interaction avec l'API Google Gemini avec tolérance aux pannes."""

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.project_id = settings.GOOGLE_CLOUD_PROJECT
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialise le client Google GenAI selon les paramètres fournis."""
        try:
            from google import genai
            
            # Essai 1 : Client standard via API Key
            if self.api_key:
                try:
                    self._client = genai.Client(api_key=self.api_key)
                    return
                except Exception:
                    pass
            
            # Essai 2 : Mode Vertex AI si ID de projet disponible
            if self.project_id:
                try:
                    self._client = genai.Client(
                        vertexai=True,
                        project=self.project_id,
                        location=self.location
                    )
                    return
                except Exception:
                    pass
                    
            # Fallback direct par défaut
            self._client = genai.Client()
        except Exception as e:
            # Ne bloque pas le chargement initial mais signale l'erreur
            self._client = None

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
        max_retries: int = 3
    ) -> str:
        """Génère du texte brut avec reprise sur erreur."""
        if not self._client:
            self._init_client()
        if not self._client:
            raise RuntimeError("Impossible d'initialiser le client Google Gemini. Vérifiez vos clés.")

        from google.genai import types

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction
        )

        last_error = None
        models_to_try = [self.model_name]
        for fallback in ["gemini-3.5-flash", "gemini-3.1-flash-lite"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        for current_model in models_to_try:
            for attempt in range(max_retries):
                try:
                    response = self._client.models.generate_content(
                        model=current_model,
                        contents=prompt,
                        config=config
                    )
                    if response and response.text:
                        return response.text
                except Exception as e:
                    last_error = e
                    time.sleep(1.0 * (attempt + 1))

        raise RuntimeError(f"Échec de la génération LLM après essais sur {models_to_try} : {str(last_error)}")

    def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Génère une réponse sous forme de dictionnaire JSON garanti."""
        full_prompt = (
            f"{prompt}\n\n"
            "IMPORTANT : Votre réponse doit être STRICTEMENT un objet JSON valide, sans texte additionnel, "
            "sans introduction, sans balises superflues en dehors du bloc JSON standard."
        )
        raw_text = self.generate_text(
            prompt=full_prompt,
            system_instruction=system_instruction,
            temperature=temperature
        )
        return self._extract_json(raw_text)

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extrait et nettoie un bloc JSON à partir d'une réponse textuelle."""
        cleaned = text.strip()
        # Supprime les balises ```json ... ``` si présentes
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
        if match:
            cleaned = match.group(1).strip()
            
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Tentative de recherche du premier { et du dernier }
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                return json.loads(cleaned[start:end+1])
            raise ValueError(f"Impossible de convertir la réponse en JSON : {text[:200]}...")

llm_service = LLMService()
