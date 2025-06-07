from flask import Flask, request, send_file, abort
import os, uuid

app = Flask(__name__)

# Cesta pro uploady
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loskybox</title>
        <style>
            body {
                background: #121212;
                color: #eee;
                font-family: monospace;
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 100px;
            }
            #drop-area {
                border: 3px dashed #666;
                padding: 40px;
                border-radius: 10px;
                text-align: center;
                width: 400px;
            }
            #fileElem {
                display: none;
            }
            a {
                color: #00f7ff;
            }
        </style>
    </head>
    <body>
        <h1>Loskybox™</h1>
        <div id="drop-area">
            <p>Drop file here or click to select</p>
            <input type="file" id="fileElem">
            <button onclick="document.getElementById('fileElem').click()">Choose File</button>
        </div>
        <p id="link"></p>

        <script>
            const dropArea = document.getElementById('drop-area');
            const fileElem = document.getElementById('fileElem');
            const link = document.getElementById('link');

            function uploadFile(file) {
                const formData = new FormData();
                formData.append("file", file);

                fetch("/upload", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.text())
                .then(text => {
                    link.innerHTML = '<a href="' + text + '" target="_blank">' + text + '</a>';
                })
                .catch(() => {
                    link.innerText = "⚠️ Upload failed";
                });
            }

            dropArea.addEventListener("dragover", (e) => {
                e.preventDefault();
                dropArea.style.borderColor = "#0ff";
            });

            dropArea.addEventListener("dragleave", () => {
                dropArea.style.borderColor = "#666";
            });

            dropArea.addEventListener("drop", (e) => {
                e.preventDefault();
                dropArea.style.borderColor = "#666";
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    uploadFile(files[0]);
                }
            });

            fileElem.addEventListener("change", () => {
                if (fileElem.files.length > 0) {
                    uploadFile(fileElem.files[0]);
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return "No file uploaded", 400

    ext = file.filename.rsplit('.', 1)[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)

    print(f"[UPLOAD] Saved: {path}")
    return f"http://127.0.0.1:5000/file/{filename}", 200, {'Content-Type': 'text/plain'}

@app.route('/file/<filename>')
def serve_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path)
    return abort(404, description="Soubor nenalezen")

if __name__ == '__main__':
    app.run(debug=True)
