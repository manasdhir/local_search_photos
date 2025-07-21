# Local Search - Photos

A local image search and indexing system using [CLIP](https://github.com/openai/CLIP) and [FAISS](https://github.com/facebookresearch/faiss), with a modern web frontend. Index your local image folders and search for similar images using text or image queries.

---

## Features

- **Index Local Folders:** Index all images in a specified local folder. Supports Windows paths (auto-converted for WSL).
- **Semantic Search:** Search for images using natural language (text) or by uploading an image.
- **CLIP Embeddings:** Uses OpenAI's CLIP model for extracting image and text features.
- **Fast Retrieval:** Uses FAISS for efficient similarity search over indexed images.
- **Modern Web UI:** User-friendly frontend with live status, error handling, and result gallery.
- **Image Preview:** View search results directly in the browser.
- **Cross-platform:** Backend supports both CPU and GPU (CUDA) environments.

---

## Project Structure

```
.
├── backend/
│   ├── app.py                # Flask API for indexing, searching, and serving images
│   ├── image_index.faiss     # FAISS index file (auto-generated)
│   └── index_metadata.json   # Metadata for indexed images (auto-generated)
├── frontend/
│   ├── server.py             # Flask server for serving static frontend files
│   └── static/
│       ├── app.js            # Main frontend logic (index, search, display)
│       ├── index.html        # Main UI
│       └── styles.css        # Styling for the web app
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone <repo-url>
cd local_search_photos
```

### 2. Create and Activate Python Environment

```sh
python3 -m venv myenv
source myenv/bin/activate.fish   # For fish shell
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Download CLIP Model (First Run)

The backend will automatically download the CLIP model on first run.

---

## Running the Application

### 1. Start the Backend API

```sh
cd backend
python app.py
```
- Runs on `http://localhost:5001`
- Handles image indexing, search, and image serving.

### 2. Start the Frontend Server

In a new terminal:

```sh
cd frontend
python server.py
```
- Serves the UI at `http://localhost:5000`

---

## Usage

1. **Open the Web UI:**  
   Go to [http://localhost:5000](http://localhost:5000) in your browser.

2. **Index Images:**
   - Enter the full path to your image folder (Windows paths supported).
   - Click "Start Indexing". The backend will process and index all images in the folder.

3. **Search Images:**
   - Enter a text query (e.g., "cat on a sofa") or upload an image.
   - Click "Search". The most similar images will be displayed in the results gallery.

---

## API Endpoints

- `POST /index`  
  **Body:** `{ "folder_path": "<path>" }`  
  Indexes all images in the given folder.

- `POST /search`  
  **Form:** `text=<query>` or `image=<file>`  
  Searches for similar images using text or image.

- `GET /image?path=<path>`  
  Serves the image file for preview.

---

## Technologies Used

- **Backend:** Python, Flask, Flask-CORS, FAISS, Transformers (CLIP), Pillow
- **Frontend:** HTML, CSS, JavaScript (Vanilla), FontAwesome
- **Other:** Numpy, Torch, WSL path conversion for Windows compatibility

---

## Notes

- Only `.jpg`, `.jpeg`, and `.png` images are indexed.
- The backend stores image features in `image_index.faiss` and metadata in `index_metadata.json`.
- The system is optimized for local use and does not upload your images anywhere.

---

## License

MIT License

---
