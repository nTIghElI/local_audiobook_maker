import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def inspect_epub(epub_path):
    print(f"🕵️‍♂️ Inspecting: {epub_path}...")
    try:
        book = epub.read_epub(epub_path)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return

    print(f"📚 Title: {book.get_metadata('DC', 'title')[0][0]}")
    
    # 1. Check the Table of Contents (TOC)
    # This is the "Map" the publisher included.
    print("\n--- TABLE OF CONTENTS (TOC) ---")
    for link in book.toc:
        if isinstance(link, tuple):
            # Normal Chapter link
            title = link[0].title
            src = link[0].href
            print(f"  ✅ Found: '{title}' -> points to {src}")
        elif isinstance(link, list):
            # Nested section (like "Part 1" -> "Chapter 1")
            print(f"  📂 Section: {link[0].title}")
            for sublink in link[1]:
                if isinstance(sublink, ebooklib.epub.Link):
                    print(f"     - '{sublink.title}'")

    # 2. Check the Spine (The actual file order)
    print("\n--- INTERNAL FILE STRUCTURE (Spine) ---")
    spine_ids = [x[0] for x in book.spine]
    count = 0
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT and item.id in spine_ids:
            # Get a snippet of text to see what's inside
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text_preview = soup.get_text()[:50].replace('\n', ' ').strip()
            print(f"  📄 File: {item.get_name()} | Starts with: '{text_preview}...'")
            count += 1
            if count > 10:
                print("  ... (stopping list to save space)")
                break

if __name__ == "__main__":
    # Point this to your new book
    # Make sure to move the epub into the 'inputs' folder!
    target_book = "inputs/Chip War.epub" 
    inspect_epub(target_book)