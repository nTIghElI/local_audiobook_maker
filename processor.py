import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import re

def get_book_structure(epub_path):
    print(f"📖 Parsing EPUB structure: {epub_path}")
    book = epub.read_epub(epub_path)
    
    chapters = {}
    
    # These words usually indicate a file we want to READ aloud
    keep_signals = ["chapter", "introduction", "prologue", "epilogue", "conclusion", "part"]
    # These words indicate junk files we should SKIP
    skip_signals = ["copyright", "dedication", "glossary", "cast of characters", "notes", "bibliography", "index", "praise"]

    spine_ids = [x[0] for x in book.spine]
    
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT and item.id in spine_ids:
            
            # 1. Get the text
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text().strip()
            
            # 2. Get the first few lines to check what this file is
            preview = text[:100].lower()
            
            # 3. Decision Logic: Keep or Skip?
            is_chapter = False
            
            # If it explicitly says "Chapter" or "Introduction", keep it
            if any(signal in preview for signal in keep_signals):
                is_chapter = True
            
            # If it explicitly says "Glossary" or "Index", kill it
            if any(signal in preview for signal in skip_signals):
                is_chapter = False
                
            # Fallback: If it's really long (>2000 chars), it's probably a narrative chapter
            # even if it doesn't say "Chapter 1" at the very top.
            if len(text) > 2000 and not any(signal in preview for signal in skip_signals):
                is_chapter = True

            if is_chapter:
                # Use the file ID as a name (e.g., index_split_008)
                # We will clean the filename later
                filename = item.get_name().replace('.html', '').replace('.xhtml', '').replace('/', '_')
                chapters[filename] = text
                
    return chapters

def load_book_chapters(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not find: {file_path}")
    
    # Currently optimized for EPUBs like Chip War
    return get_book_structure(file_path)