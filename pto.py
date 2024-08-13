from fastapi import FastAPI, Form, HTTPException, Query
from fastapi.responses import FileResponse
import yt_dlp
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory where downloaded videos will be saved
download_path = os.path.join(os.getcwd(), "downloads")
os.makedirs(download_path, exist_ok=True)

@app.get("/formats")
def get_video_formats(link: str):
    """
    Fetch available video formats and their qualities, filtering to show only MP4 formats.
    """
    try:
        with yt_dlp.YoutubeDL() as ydl:
            info = ydl.extract_info(link, download=False)
            formats = info.get('formats', [])

            # Filter and format the list of MP4 formats
            mp4_formats = [
                {
                    "format_id": f['format_id'],
                    "format": f['format'],
                    "resolution": f.get('resolution'),
                    "ext": f['ext']
                }
                for f in formats if f['ext'] == 'mp4'
            ]
            return {"formats": mp4_formats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch formats: {e}")

@app.post("/download")
def download_video(link: str = Form(...), format_code: str = Form(...)):
    """
    Download the video in the specified format.
    """
    output_file = os.path.join(download_path, f"video-{link[-11:]}.mp4")
    
    youtube_dl_options = {
        "format": format_code,
        "outtmpl": output_file,
    }
    
    try:
        with yt_dlp.YoutubeDL(youtube_dl_options) as ydl:
            ydl.download([link])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {e}")

    return {"status": "Download started", "file_path": output_file}

@app.get("/download/{filename}")
def serve_file(filename: str):
    """
    Serve the downloaded file.
    """
    file_path = os.path.join(download_path, filename)
    
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)
 