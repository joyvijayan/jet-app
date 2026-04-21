from flask import Flask, render_template, request, send_from_directory
import os
import yt_dlp
import glob

app = Flask(__name__)

# Configuration
DOWNLOAD_FOLDER = "downloads"
LOG_FILE = "download_history.log"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/")
def home():
    return render_template("index.html", video_url=None)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route('/sitemap.xml')
def sitemap():
    return render_template('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")

    # Basic validation for Instagram links
    if not url or "instagram.com" not in url:
        return render_template("index.html", error="Please paste a valid Instagram link", video_url=None)

    # --- Start Download Tracking ---
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"Requested URL: {url}\n")
    except Exception as log_error:
        print(f"Logging Error: {log_error}")
    # --- End Download Tracking ---

    # yt-dlp options
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        # Cleanup: Remove old files before starting a new download
        files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        for f in files:
            try:
                os.remove(f)
            except:
                continue

        # Download video using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # Find the newly downloaded file
        new_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        if not new_files:
            return render_template("index.html", error="Could not save video", video_url=None)
            
        # Select the most recently created file
        latest_file = max(new_files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        video_path = f"/downloads/{filename}"

        return render_template("index.html", video_url=video_path)

    except Exception as e:
        print(f"Download Error: {e}")
        return render_template("index.html", error="Failed to fetch video. Try another link.", video_url=None)

@app.route("/downloads/<filename>")
def serve_video(filename):
    """Serves the downloaded file to the user."""
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    # Get port from environment (useful for hosting like Render/Heroku)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
