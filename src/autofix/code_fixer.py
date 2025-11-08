def generate_fix(self, code: str, issue: str, lang: str) -> str:
messages = [
{"role": "system", "content": f"You are an expert {lang} developer."},
{"role": "user", "content": f"Fix this code issue ({issue}):\n{lang}\n{code}\n
]
try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.2,
        max_tokens=200
    )
    return response.choices.message.content
except Exception as e:
    logger.error(f"Failed to generate fix: {str(e)}")
    raise
