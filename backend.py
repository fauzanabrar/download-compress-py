from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Enable Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_DIR = "downloaded-files"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Endpoint to download files
@app.get("/download/{file_name}")
async def download_file(file_name: str):
    safe_filename = os.path.basename(file_name)
    file_path = os.path.join(DOWNLOAD_DIR, safe_filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=safe_filename, media_type='application/octet-stream')

# Run the server with host="0.0.0.0" for Codespaces
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)