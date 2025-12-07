import re

def clean_text_for_audio(text):
    """
    Master cleaning function.
    """
    # 1. EXPAND ABBREVIATIONS
    text = re.sub(r'\bU\.S\.', 'United States', text)
    text = re.sub(r'\bU\.S\b', 'United States', text)
    text = re.sub(r'\bUS\b', 'United States', text)

    # 2. FIX "World War I / II"
    text = re.sub(r'\bWorld War I\b', 'World War One', text, flags=re.IGNORECASE)
    text = re.sub(r'\bWorld War II\b', 'World War Two', text, flags=re.IGNORECASE)
    
    # 3. FIX CITATION NUMBERS
    text = re.sub(r'(?<=[a-zA-Z”"’])(\d+)(?!\d)', '', text)

    # 4. PRONUNCIATION & EMPHASIS
    corrections = {
        "The Pentagon": "The Pen-tuh-gon",
        "Pentagon": "Pen-tuh-gon",
        "Nvidia": "En-vid-ea",
        " TSMC ": " T-S-M-C ", 
        "ASML": "A-S-M-L",
        "Fuzhou": "Foo-joe",
        "Xiamen": "Sha-men",
        "Huawei": "Hwa-way",
        "Shenzhen": "Shen-zhen",
        # Fix the "On deck" pause by adding a comma
        "On deck ninety-six": "On deck, ninety-six", 
    }
    for word, replacement in corrections.items():
        text = text.replace(word, replacement)

    # 5. CURRENCY
    def currency_replacer(match):
        return f"{match.group(1)} {match.group(2) or ''} dollars"
    text = re.sub(r'\$(\d+(?:\.\d+)?)\s*(billion|million|trillion|thousand)?', currency_replacer, text)

    # 6. HEADER PROTECTION (The "Intro" Rush Fix)
    # If we see a line that looks like a header (all caps, short), force a break
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped: 
            continue
            
        # If it's a Header (e.g. "INTRODUCTION"), add a period to force a stop
        # and ensure it stands alone.
        if stripped.isupper() and len(stripped) < 50:
            stripped += "."
            
        processed_lines.append(stripped)

    # Rejoin with a SPECIAL DELIMITER that main.py will look for
    # We use |PARAGRAPH| so we don't get confused by normal newlines
    return "|PARAGRAPH|".join(processed_lines)