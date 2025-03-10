# app/utils.py
def clean_text(text):
    """Condense whitespace (including newlines) to a single space."""
    return ' '.join(text.split())
