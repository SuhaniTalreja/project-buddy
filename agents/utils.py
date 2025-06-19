def extract_text(response):
    try:
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        return f"[ERROR extracting text] {e}"
