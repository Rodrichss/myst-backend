import unicodedata

def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    # remove accents
    text = ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

    return text