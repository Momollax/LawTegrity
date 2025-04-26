import os
import json

def save_law_as_json(save_path, filename, content):
    os.makedirs(save_path, exist_ok=True)
    filepath = os.path.join(save_path, f"{filename}.json")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
