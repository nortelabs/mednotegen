import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class LLMGenerator:
    def __init__(self, model="gpt-3.5-turbo"):
        try:
            import openai
        except ImportError:
            raise ImportError("openai package is required for LLM features. Install with 'uv pip install openai'.")
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = OPENAI_API_KEY
        self.model = model
        self.openai = openai

    def generate_note(self, note_type, patient_info=None):
        prompt = self._build_prompt(note_type, patient_info)
        response = self.openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        return response.choices[0].message["content"].strip()

    def _build_prompt(self, note_type, patient_info=None):
        if note_type == "patient_report":
            return (
                "Generate a realistic, synthetic patient report for a random adult. "
                "Include: Name, Date of Birth, Visit Date, and a summary of the visit. "
                "Format as a short, readable report."
            )
        else:
            return "Generate a synthetic medical note."
