from flask import Flask, request, jsonify, send_file
from PIL import Image
import os, json
from datetime import datetime
import torch
import numpy as np
import faiss
from transformers import CLIPProcessor, CLIPModel
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
device = "cuda" if torch.cuda.is_available() else "cpu"

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

METADATA_FILE = "backend/index_metadata.json"
INDEX_FILE = "backend/image_index.faiss"

if os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, "r") as f:
        metadata = json.load(f)
else:
    metadata = {}

def windows_to_wsl_path(win_path):
    win_path = win_path.strip().replace("\\", "/")
    if ":" in win_path:
        drive, rest = win_path.split(":", 1)
        wsl_path = f"/mnt/{drive.lower()}{rest}"
        return wsl_path
    return win_path

@app.route("/index", methods=["POST"])
def index_folder():
    data = request.json
    folder_path = data.get("folder_path")
    
    if not folder_path:
        return jsonify({"status": "error", "message": "No folder path provided"}), 400
    
    folder = windows_to_wsl_path(folder_path)
    
    if not os.path.exists(folder):
        return jsonify({"status": "error", "message": f"Folder not found: {folder}"}), 400

    indexed_files = metadata.get(folder, {})
    new_images = []

    for fname in os.listdir(folder):
        if not fname.lower().endswith((".jpg", ".png", ".jpeg")):
            continue
        fpath = os.path.join(folder, fname)
        mtime = os.path.getmtime(fpath)
        timestamp = datetime.fromtimestamp(mtime).isoformat()

        if fname not in indexed_files or (isinstance(indexed_files[fname], dict) and 
                                         indexed_files[fname].get("timestamp") != timestamp) or \
           (not isinstance(indexed_files[fname], dict) and indexed_files[fname] != timestamp):
            new_images.append((fpath, timestamp))

    vectors, paths = [], []
    for path, ts in new_images:
        try:
            image = Image.open(path).convert("RGB")
            inputs = processor(images=image, return_tensors="pt").to(device)
            with torch.no_grad():
                emb = model.get_image_features(**inputs)
                emb = emb / emb.norm(dim=-1, keepdim=True)
                vectors.append(emb.cpu().numpy())
                paths.append(path)

            filename = os.path.basename(path)
            if folder not in metadata:
                metadata[folder] = {}
            metadata[folder][filename] = timestamp
        except Exception as e:
            print(f"Skipping {path}: {e}")

    if vectors:
        vectors = np.vstack(vectors).astype("float32")
        if os.path.exists(INDEX_FILE):
            index = faiss.read_index(INDEX_FILE)
        else:
            index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, INDEX_FILE)

        with open(METADATA_FILE, "w") as f:
            json.dump(metadata, f, indent=2)

        return jsonify({"status": "success", "indexed": len(vectors)})

    return jsonify({"status": "no_new_images", "message": "No new images to index."})

@app.route("/search", methods=["POST"])
def search():
    data = request.form
    query_text = data.get("text", "").strip()
    query_file = request.files.get("image", None)

    if not query_text and not query_file:
        return jsonify({"status": "error", "message": "Provide either text or image query"}), 400

    if not os.path.exists(INDEX_FILE):
        return jsonify({"status": "error", "message": "No index found"}), 404
    index = faiss.read_index(INDEX_FILE)

    all_paths = []
    for folder, files in metadata.items():
        for filename in files:
            all_paths.append(os.path.join(folder, filename))

    with torch.no_grad():
        if query_text:
            inputs = processor(text=[query_text], return_tensors="pt", padding=True).to(device)
            query_emb = model.get_text_features(**inputs)
        else:
            image = Image.open(query_file).convert("RGB")
            inputs = processor(images=image, return_tensors="pt").to(device)
            query_emb = model.get_image_features(**inputs)

        query_emb = query_emb / query_emb.norm(dim=-1, keepdim=True)
        query_np = query_emb.cpu().numpy().astype("float32")

    top_k = 2
    
    D, I = index.search(query_np, top_k)
    matched_paths = [all_paths[i] for i in I[0] if i < len(all_paths)]
    print(matched_paths)
    return jsonify({"status": "success", "results": matched_paths})

@app.route("/image", methods=["GET"])
def serve_image():
    image_path = request.args.get("path")
    if not image_path:
        return jsonify({"error": "No image path provided"}), 400
    
    try:
        if not os.path.isfile(image_path):
            return jsonify({"error": f"Invalid image path: {image_path}"}), 404
        
        return send_file(image_path, mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": f"Failed to serve image: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5001, debug=True)
