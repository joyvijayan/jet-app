from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
import yt_dlp
import glob

app = Flask(__name__)

if not os.path.exists("downloads"):
    os.makedirs("downloads")


@app.route("/")
def home():
    video_url = request.args.get("video_url")
    error = request.args.get("error")
    return render_template("index.html", video_url=video_url, error=error)


@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")

    # Allow only Instagram links
    if not url or "instagram.com" not in url:
        return redirect(url_for("home", error="Only Instagram links allowed"))

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        files = glob.glob("downloads/*")
        latest_file = max(files, key=os.path.getctime)

        filename = os.path.basename(latest_file)
        video_path = f"/downloads/{filename}"

        return redirect(url_for("home", video_url=video_path))

    except Exception as e:
        print(e)
        return redirect(url_for("home", error="Failed to download video"))


@app.route("/downloads/<filename>")
def serve_video(filename):
    return send_from_directory("downloads", filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
