import os

def save_law_text(save_path, filename, text_content):
    os.makedirs(save_path, exist_ok=True)
    filepath = os.path.join(save_path, f"{filename}.txt")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text_content)