# services/assistant_ai.py

import base64
from openai import OpenAI


class GPTAssistant:
    """
    Assistant IA générique pour l'analyse avec vision.
    Compatible avec le SDK OpenAI 2025 (client.responses).
    """

    def __init__(self, model="gpt-5-mini"):
        self.client = OpenAI()
        self.model = model
    
    def encode_image(self, image_path):
        """Encode une image en base64 pour inclusion dans le prompt."""
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    def ask_with_image(self, prompt, image_path):
        """
        Envoie un prompt avec une image au modèle.
        
        Args:
            prompt: Le prompt textuel
            image_path: Chemin vers l'image à analyser
            
        Returns:
            La réponse du modèle
        """
        base64_image = self.encode_image(image_path)
        
        response = self.client.responses.create(
            model=self.model,
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}"
                    }
                ]
            }]
        )
        return response.output_text
    
    def ask(self, prompt):
        """
        Envoie un prompt textuel simple au modèle (sans image).
        
        Args:
            prompt: Le prompt textuel
            
        Returns:
            La réponse du modèle
        """
        response = self.client.responses.create(
            model=self.model,
            input=[{
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}]
            }]
        )
        return response.output_text
