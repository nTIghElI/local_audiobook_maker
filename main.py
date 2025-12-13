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

# SILENCE SETTINGS
PARAGRAPH_PAUSE = 0.8  # Seconds between paragraphs
SENTENCE_PAUSE = 0.2   # Seconds between merged sentences

def split_long_paragraph(text, max_chars=450):
    """
    Splits massive paragraphs into smaller chunks to fit model context.
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

def generate_audio_from_text(kokoro, raw_text, output_path):
    # 1. Clean and get the paragraph list
    cleaned_text = clean_text_for_audio(raw_text)
    paragraphs = cleaned_text.split('|PARAGRAPH|')
    
    full_audio_segments = []
    sample_rate = 24000
    
    # Pre-calculate silence buffers
    para_silence = np.zeros(int(24000 * PARAGRAPH_PAUSE))
    
    print(f"   > Processing {len(paragraphs)} paragraphs...", end="", flush=True)
    
    start_time = time.time()
    
    for i, para in enumerate(paragraphs):
        if len(para.strip()) < 2: continue
        
        # Split only if absolutely necessary
        sub_chunks = split_long_paragraph(para)
        
        for chunk in sub_chunks:
            # Generate audio
            samples, sr = kokoro.create(chunk, voice='am_michael', speed=1.0, lang='en-us')
            if samples is not None:
                full_audio_segments.append(samples)
                sample_rate = sr
        
        # Add the "Breath" after every paragraph
        full_audio_segments.append(para_silence)
        
        if i % 10 == 0: print(".", end="", flush=True)
        
    elapsed = time.time() - start_time
    print(f" Done ({elapsed:.1f}s).")
    
    if full_audio_segments:
        final_audio = np.concatenate(full_audio_segments)
        sf.write(output_path, final_audio, sample_rate)
        return True
    return False

def interface():
    # 1. Select Book
    if not os.path.exists(INPUT_FOLDER): os.makedirs(INPUT_FOLDER)
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
    print(f"✅ Found {len(chapters)} viable chapters.")
    
    # 3. Generate Test
    test_key = next((k for k in chapters.keys() if 'intro' in k.lower()), list(chapters.keys())[0])
    test_text = chapters[test_key][:1500] 
    
    print(f"\n🧪 GENERATING TEST: {test_key}...")
    
    # Init Model - Now it should pick up the GPU automatically
    kokoro = Kokoro("kokoro-v0_19.onnx", "voices.bin")
    
    os.makedirs(STAGING_FOLDER, exist_ok=True)
    test_path = os.path.join(STAGING_FOLDER, "test_preview.wav")
    
    generate_audio_from_text(kokoro, test_text, test_path)
    
    print(f"\n🎧 Test file created: {test_path}")
    
    confirm = input("\nDid it sound good? Press 'Y' to generate the whole book, or 'N' to abort: ")
    if confirm.lower() != 'y':
        print("🚫 Aborting.")
        return

    # 4. Full Batch Generation
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