document.addEventListener('DOMContentLoaded', () => {
    const directoryPath = document.getElementById('directoryPath');
    const indexButton = document.getElementById('indexButton');
    const searchText = document.getElementById('searchText');
    const searchImage = document.getElementById('searchImage');
    const searchButton = document.getElementById('searchButton');
    const statusCard = document.getElementById('statusCard');
    const statusHeader = document.getElementById('statusHeader');
    const statusMessage = document.getElementById('statusMessage');
    const resultsCard = document.getElementById('resultsCard');
    const resultsGallery = document.getElementById('resultsGallery');

    // Enable/disable the index button
    directoryPath.addEventListener('input', () => {
        indexButton.disabled = !directoryPath.value.trim();
    });

    indexButton.addEventListener('click', async () => {
        const folderPath = directoryPath.value.trim();
        if (!folderPath) {
            alert("Please enter a directory path");
            return;
        }

        showStatus("Indexing Images...", "Please wait while we process your images.");

        indexButton.disabled = true;
        try {
            const response = await fetch('http://localhost:5001/index', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder_path: folderPath }),
            });

            const data = await response.json();
            if (response.ok) {
                showStatus("Success!", `Successfully indexed ${data.indexed} images.`, true);
            } else {
                showStatus("Error!", data.message || "Indexing failed.", false);
            }
        } catch (error) {
            showStatus("Error!", "Failed to communicate with server: " + error.message, false);
        } finally {
            indexButton.disabled = false;
        }
    });

    searchButton.addEventListener('click', async () => {
        const text = searchText.value.trim();
        const file = searchImage.files[0];

        if (!text && !file) {
            alert("Please enter text or select an image to search.");
            return;
        }

        showStatus("Searching...", "Searching for similar images...");
        resultsCard.classList.add("hidden");

        const formData = new FormData();
        if (text) formData.append("text", text);
        if (file) formData.append("image", file);

        try {
            const response = await fetch('http://localhost:5001/search', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                showStatus("Success!", "Found similar images!", true);
                displayResults(data.results);
            } else {
                showStatus("Error!", data.message || "Search failed.", false);
            }
        } catch (error) {
            showStatus("Error!", "Failed to search: " + error.message, false);
        }
    });

    function showStatus(title, message, success = null) {
        statusCard.classList.remove("hidden");
        statusHeader.innerHTML = success === null
            ? `<i class="fas fa-spinner fa-spin"></i> ${title}`
            : `<i class="fas fa-${success ? 'check-circle success' : 'times-circle error'}"></i> ${title}`;
        statusMessage.textContent = message;
    }

    function displayResults(paths) {
        resultsGallery.innerHTML = "";
        if (paths.length === 0) {
            resultsGallery.innerHTML = "<p>No similar images found.</p>";
        } else {
            paths.forEach(path => {
                const container = document.createElement("div");
                container.className = "image-result";
                
                // Create image element
                const img = document.createElement("img");
                
                // Use the backend's image serving endpoint
                img.src = `http://localhost:5001/image?path=${encodeURIComponent(path)}`;
                img.alt = "Result Image";
                img.loading = "lazy";
                
                // Add event handlers
                img.onerror = function() {
                    this.onerror = null;
                    this.src = 'https://via.placeholder.com/150?text=Image+Not+Found';
                };
                
                // Styling
                img.style.width = "150px";
                img.style.height = "150px";
                img.style.objectFit = "cover";
                img.style.borderRadius = "8px";
                img.style.boxShadow = "0 2px 6px rgba(0,0,0,0.15)";
                
                // Add to container
                container.appendChild(img);
                
                // Add path as caption
                const caption = document.createElement("div");
                caption.className = "image-caption";
                caption.textContent = path.split('/').pop(); // Show only filename
                container.appendChild(caption);
                
                resultsGallery.appendChild(container);
            });
        }
        resultsCard.classList.remove("hidden");
    }
});
