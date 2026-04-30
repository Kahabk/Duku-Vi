import requests
import base64
from PIL import Image

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen3.5:4b"
session = requests.Session()

def preprocess_image(path):
    img = Image.open(path).convert("RGB")
    img.thumbnail((336, 336))  # Smallest viable size
    img.save("t.jpg", format="JPEG", quality=50)
    return "t.jpg"

def ask(image_path):
    b64 = base64.b64encode(open(preprocess_image(image_path), "rb").read()).decode()
    payload = {
        "model": MODEL,
        "prompt": "Briefly describe this image.",  
        "images": [b64],
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 80,       # Low token limit = fast
            "num_ctx": 512,          # Tiny context window
            "num_thred":3,                      # Match i3 core count
            "num_gpu": 1,            # CPU only (i3 = no GPU)
            "low_vram": True,
            "f16_kv": False,
        }
    }
    try:
        r = session.post(OLLAMA_URL, json=payload, timeout=60)
        return r.json().get("response", "Empty response")
    except Exception as e:
        return f"ERROR: {e}"

if __name__ == "__main__":
    print(ask("popa.jpeg"))
