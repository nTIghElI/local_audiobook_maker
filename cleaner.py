import re

def clean_text_for_audio(text):
    # 1. Standard cleanup (whitespace, weird artifacts)
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces
    
    # 2. Define the Dictionary of Replacements
    # Key = Original Word (Case sensitive usually, but flags handle that)
    # Value = How it should be pronounced
    replacements = {
        # --- The User Request ---
        "Huawei": "Wah-way",
        
        # --- Chinese Tech Giants ---
        "Xiaomi": "Sh-ow-me",
        "Tencent": "Ten-cent",
        "ByteDance": "Bite-dance",
        "Alibaba": "Ah-lee-bah-bah",
        
        # --- Geopolitics / Cities ---
        "Beijing": "Bay-jing",
        "Taipei": "Tie-pay",
        "Shenzhen": "Shen-jen",
        "Xinjiang": "Shin-jiang",
        "Kyiv": "Keev", 
        "Qatar": "Kuh-tar", 
        
        # --- Military / Gov ---
        "Pentagon": "Pent-agon", 
        "Kremlin": "Krem-lin",
        
        # --- Acronyms ---
        # "United States" flows better than "U.S." (which causes pauses)
        "US": "U-Es",      
        "USA": "United States of America",
        "U.S.": "U-Es",
        
        # For these, we want letter-by-letter. 
        # If "A.I." sounds choppy, we can change it to "Ay Eye" later.
        "TSMC": "Tee Ess Mee See",
        "CCP": "See See Pee",
        "PLA": "Pee El Ah",   
        "NATO": "Nay-toe", 
        "AI": "A Eye",      
        "LLM": "Ell Ell Em"
    }

    # 3. Apply Replacements using Regex for safety
    for word, phonetic in replacements.items():
        # \b matches word boundaries. flags=re.IGNORECASE makes it catch "huawei" and "Huawei"
        pattern = r'\b' + re.escape(word) + r'\b'
        text = re.sub(pattern, phonetic, text, flags=re.IGNORECASE)

    return text

# Test block
if __name__ == "__main__":
    test_sentence = "The US and the CCP are discussing AI regulations."
    print(f"Original: {test_sentence}")
    print(f"Cleaned:  {clean_text_for_audio(test_sentence)}")