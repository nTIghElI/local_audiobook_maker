import requests
import os

def download_file(url, filename):
    print(f"⬇️ Downloading {filename}...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Saved {filename}")

if __name__ == "__main__":
    # URLs for the binary model and voice file
    model_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx"
    # CHANGED: Now downloading voices.bin instead of voices.json
    voices_url = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin"
    
    if not os.path.exists("kokoro-v0_19.onnx"):
        download_file(model_url, "kokoro-v0_19.onnx")

    if not os.path.exists("voices.bin"):
        download_file(voices_url, "voices.bin")
    else:
        print("⚡ voices.bin already exists.")