import soundfile as sf
from kokoro_onnx import Kokoro
from processor import load_book
from cleaner import split_book_into_chapters
import numpy as np
import time
import os

def split_into_chunks(text, max_chars=400):
    # Splits text by punctuation to avoid context-window truncation
    sentences = text.replace('!', '.').replace('?', '.').replace('\n', ' ').split('.')
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_chars:
            current_chunk += sentence + "."
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + "."
    if current_chunk: chunks.append(current_chunk)
    return chunks

def main():
    # 1. SETUP
    print("🔌 Initializing GPU Voice Engine...")
    kokoro = Kokoro("kokoro-v0_19.onnx", "voices.bin")
    
    # 2. LOAD
    print("📖 Loading Book...")
    raw_text = load_book("The Kill Chain.epub")
    
    # 3. SPLIT
    # This gets us a dictionary: {'01_Chapter_1': "Text...", '02_Chapter_2': "Text..."}
    chapters = split_book_into_chapters(raw_text)
    
    # Create output folder
    os.makedirs("audio_output", exist_ok=True)
    
    # 4. BATCH GENERATION
    total_chapters = len(chapters)
    print(f"\n🎙️  Starting Batch Job: {total_chapters} Chapters")
    print("------------------------------------------------")

    for index, (filename, text_content) in enumerate(chapters.items()):
        print(f"Processing [{index+1}/{total_chapters}]: {filename}...")
        
        # Chunking
        chunks = split_into_chunks(text_content)
        audio_segments = []
        
        start_time = time.time()
        
        # Loop through sentences in this chapter
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) < 2: continue
            
            # Generate Audio
            samples, sample_rate = kokoro.create(
                chunk, 
                voice='am_michael', 
                speed=1.0, 
                lang='en-us'
            )
            audio_segments.append(samples)
            
            # Simple progress indicator (dots)
            if i % 10 == 0: print(".", end="", flush=True)

        # Stitch and Save
        if audio_segments:
            full_audio = np.concatenate(audio_segments)
            out_path = f"audio_output/{filename}.wav"
            sf.write(out_path, full_audio, sample_rate)
            duration = time.time() - start_time
            print(f"\n✅ Saved {out_path} (Gen Time: {duration:.2f}s)\n")
        else:
            print(f"\n❌ Warning: No audio generated for {filename}\n")

    print("🎉 BOOK COMPLETE! Check the 'audio_output' folder.")

if __name__ == "__main__":
    main()