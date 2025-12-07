import os
import time
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro
from processor import load_book_chapters
from cleaner import clean_text_for_audio

# CONFIG
INPUT_FOLDER = "inputs"
OUTPUT_FOLDER = "output"
STAGING_FOLDER = "staging"

# SILENCE SETTINGS (The "Breathing" Room)
PARAGRAPH_PAUSE = 0.8  # Seconds between paragraphs
SENTENCE_PAUSE = 0.2   # Seconds between merged sentences

def generate_audio_from_text(kokoro, raw_text, output_path):
    """
    New logic: Splits by |PARAGRAPH| delimiter from cleaner.py.
    Generates audio for each paragraph individually, then stitches with silence.
    """
    # 1. Clean and get the paragraph list
    cleaned_text = clean_text_for_audio(raw_text)
    paragraphs = cleaned_text.split('|PARAGRAPH|')
    
    full_audio_segments = []
    sample_rate = 24000
    
    # Create Silence Buffers
    para_silence = np.zeros(int(24000 * PARAGRAPH_PAUSE))
    
    print(f"   > Processing {len(paragraphs)} paragraphs...", end="", flush=True)
    
    for i, para in enumerate(paragraphs):
        if len(para.strip()) < 2: continue
        
        # Safety: If a paragraph is HUGE (like > 500 chars), we still need to split it
        # so the model doesn't crash (510 token limit).
        sub_chunks = split_long_paragraph(para)
        
        for chunk in sub_chunks:
            samples, sr = kokoro.create(chunk, voice='am_michael', speed=1.0, lang='en-us')
            full_audio_segments.append(samples)
            sample_rate = sr
        
        # Add the "Breath" after every paragraph
        full_audio_segments.append(para_silence)
        
        if i % 5 == 0: print(".", end="", flush=True)
        
    print(" Done.")
    
    if full_audio_segments:
        final_audio = np.concatenate(full_audio_segments)
        sf.write(output_path, final_audio, sample_rate)
        return True
    return False

def split_long_paragraph(text, max_chars=400):
    """
    Fallback for massive paragraphs. Splits by sentences.
    """
    if len(text) < max_chars:
        return [text]
        
    sentences = text.replace('!', '.').replace('?', '.').split('.')
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) < max_chars:
            current += s + "."
        else:
            chunks.append(current)
            current = s + "."
    if current: chunks.append(current)
    return chunks

def interface():
    # 1. Select Book
    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith('.epub')]
    if not files:
        print(f"❌ No EPUBs found in {INPUT_FOLDER}/")
        return

    print("\n📚 Available Books:")
    for i, f in enumerate(files):
        print(f"  [{i+1}] {f}")
    
    choice = input("\nSelect a book number: ")
    try:
        book_filename = files[int(choice) - 1]
    except:
        print("Invalid choice.")
        return

    book_path = os.path.join(INPUT_FOLDER, book_filename)
    book_name = book_filename.replace('.epub', '')
    
    # 2. Inspect & Parse
    print(f"\n🕵️‍♂️ Inspecting {book_filename}...")
    chapters = load_book_chapters(book_path)
    
    chapter_keys = list(chapters.keys())
    print(f"✅ Found {len(chapter_keys)} viable chapters/sections.")
    
    # 3. Generate Test (Introduction usually)
    # We look for a file with 'intro' in the name, otherwise take the first one
    test_key = next((k for k in chapter_keys if 'intro' in k.lower()), chapter_keys[0])
    test_text = chapters[test_key][:3000] # First 3000 chars
    
    print(f"\n🧪 GENERATING TEST: {test_key}...")
    
    # Init Model
    kokoro = Kokoro("kokoro-v0_19.onnx", "voices.bin")
    
    os.makedirs(STAGING_FOLDER, exist_ok=True)
    test_path = os.path.join(STAGING_FOLDER, "test_preview.wav")
    
    generate_audio_from_text(kokoro, test_text, test_path)
    
    print(f"\n🎧 Test file created: {test_path}")
    print("👉 Please go listen to it now.")
    
    # 4. User Feedback Loop
    confirm = input("\nDid it sound good? Press 'Y' to generate the whole book, or 'N' to abort: ")
    
    if confirm.lower() != 'y':
        print("🚫 Aborting.")
        return

    # 5. Full Batch Generation
    print("\n🚀 STARTING FULL BATCH GENERATION")
    book_out_folder = os.path.join(OUTPUT_FOLDER, book_name)
    os.makedirs(book_out_folder, exist_ok=True)
    
    for i, (filename, content) in enumerate(chapters.items()):
        print(f"[{i+1}/{len(chapters)}] Generating {filename}...")
        out_file = os.path.join(book_out_folder, f"{filename}.wav")
        
        if os.path.exists(out_file):
            print("   -> File exists, skipping.")
            continue
            
        generate_audio_from_text(kokoro, content, out_file)

    print(f"\n🎉 COMPLETED! All files are in {book_out_folder}")

if __name__ == "__main__":
    interface()