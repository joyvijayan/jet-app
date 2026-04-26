from flask import Flask, render_template, request, send_from_directory, Response
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

# Route for robots.txt (Helps with Google AdSense/SEO)
@app.route('/robots.txt')
def robots_txt():
    content = "User-agent: *\nAllow: /"
    return Response(content, mimetype='text/plain')

# Route for ads.txt (Added for AdSense Verification)
@app.route('/ads.txt')
def ads_txt():
    return send_from_directory(os.getcwd(), 'ads.txt')

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

# --- BLOG ROUTES START ---
@app.route("/blog")
def blog_home():
    return render_template("blog.html")

@app.route("/blog/reels-guide")
def reels_guide():
    return render_template("reels-guide.html")

@app.route("/blog/viral-tips")
def viral_tips():
    return render_template("viral-tips.html")

@app.route("/blog/privacy-guide")
def privacy_guide():
    return render_template("privacy-guide.html")

@app.route("/blog/posting-time")
def posting_time():
    return render_template("posting-time.html")

@app.route("/blog/font-world-guide")
def font_world_guide():
    return render_template("font-world-guide.html")

@app.route("/blog/high-quality")
def high_quality():
    return render_template("high-quality.html")

@app.route("/blog/reuse-content")
def reuse_content():
    return render_template("reuse-content.html")

@app.route("/blog/link-issues")
def link_issues():
    return render_template("link-issues.html")

@app.route("/blog/video-king")
def video_king():
    return render_template("video-king.html")
# --- BLOG ROUTES END ---

# Contact route to handle form submissions
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        
        # Log the received message to server console
        print(f"New Message Received: {name} - {email} - {subject} - {message}")
        
        return "<h1>Thank You!</h1><p>Your message has been sent successfully.</p><a href='/'>Go Back</a>"
    
    return render_template("index.html") 

@app.route('/sitemap.xml')
def sitemap():
    return render_template('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

# Simple statistics page to see total download requests
@app.route("/stats")
def show_stats():
    count = 0
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            count = len(f.readlines())
    return f"<h1>Total Downloads Requested: {count}</h1>"

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")

    # Basic URL validation
    if not url or "instagram.com" not in url:
        return render_template("index.html", error="Please paste a valid Instagram link", video_url=None)

    # Log the URL to the history file
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"Requested URL: {url}\n")
    except Exception as log_error:
        print(f"Logging Error: {log_error}")

    # yt-dlp options with Cookies to prevent being blocked
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.instagram.com/',
        }
    }

    try:
        # Clear old files before starting a new download to save space
        old_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        for f in old_files:
            try:
                os.remove(f)
            except:
                continue

        # Execute the download using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # Check if the file was actually created
        new_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        if not new_files:
            return render_template("index.html", error="Could not save video. Instagram might be blocking the request.", video_url=None)
            
        latest_file = max(new_files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        video_path = f"/downloads/{filename}"

        return render_template("index.html", video_url=video_path)

    except Exception as e:
        print(f"Detailed Download Error: {e}")
        return render_template("index.html", error="Failed to fetch video. Try another link or check server logs.", video_url=None)

# Route to serve the actual video file
@app.route("/downloads/<filename>")
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    # Ensure port is dynamic for Render deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
