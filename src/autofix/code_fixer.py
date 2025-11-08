import openai, os

class CodeFixer:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
    def generate_fix(self, code:str, issue:str, lang:str) -> str:
        prompt = f"Fix this {lang} code ({issue}):\n{code}"
        return openai.Completion.create(model="gpt-4", prompt=prompt, temperature=0.2, max_tokens=200).choices[0].text

