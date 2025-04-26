def extract_plain_text_generic(response_json):
    if not response_json:
        return ""
    text = response_json.get("jorfText") or response_json.get("content") or ""
    return text