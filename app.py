from flask import Flask, render_template, request, send_from_directory
import os
import yt_dlp
import glob

app = Flask(__name__)

# Create downloads folder if it doesn't exist
DOWNLOAD_FOLDER = "downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/")
def home():
    return render_template("index.html", video_url=None)

# Privacy Policy Page
@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

# Terms and Conditions Page
@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")

    # Basic check for Instagram links
    if not url or "instagram.com" not in url:
        return render_template("index.html", error="Please paste a valid Instagram link", video_url=None)

    # yt-dlp configuration
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        # Clear old files to save server space
        files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        for f in files:
            try:
                os.remove(f)
            except:
                continue

        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # Find the newly downloaded file
        new_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        if not new_files:
            return render_template("index.html", error="Could not save video", video_url=None)
            
        latest_file = max(new_files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        
        # Path for the video player in the browser
        video_path = f"/downloads/{filename}"

        return render_template("index.html", video_url=video_path)

    except Exception as e:
        print(f"Error: {e}")
        return render_template("index.html", error="Failed to fetch video. Try another link.", video_url=None)

@app.route("/downloads/<filename>")
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    # Configured for hosting services like Render or PythonAnywhere
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
