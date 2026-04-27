
from flask import Flask, render_template, request, send_from_directory, Response, url_for
import os
import yt_dlp
import glob

# For enhanced security, forces HTTPS and sets secure headers
try:
    from flask_talisman import Talisman
except ImportError:
    Talisman = None

app = Flask(__name__)

# Force HTTPS in production (useful for Render/Heroku)
if Talisman:
    Talisman(app, content_security_policy=None)

# Configuration
DOWNLOAD_FOLDER = "downloads"
LOG_FILE = "download_history.log"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Context processor to force url_for to generate HTTPS links
@app.context_processor
def override_url_for():
    return dict(url_for=lambda endpoint, **values: url_for(endpoint, _external=True, _scheme='https', **values) if not app.debug else url_for(endpoint, **values))

# Route for robots.txt (SEO & AdSense requirement)
@app.route('/robots.txt')
def robots_txt():
    content = "User-agent: *\nAllow: /"
    return Response(content, mimetype='text/plain')

# Route for ads.txt (AdSense Verification)
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

# --- BLOG ROUTES ---
blog_pages = [
    "reels-guide", "viral-tips", "privacy-guide", "posting-time", 
    "font-world-guide", "high-quality", "reuse-content", "link-issues", 
    "video-king", "unique-fonts", "engagement-guide", "digital-privacy", 
    "viral-captions", "social-history", "growth-strategies"
]

@app.route("/blog")
def blog_home():
    return render_template("blog.html")

@app.route("/blog/<page_name>")
def blog_page(page_name):
    if page_name in blog_pages:
        return render_template(f"{page_name}.html")
    return "Page not found", 404

# Contact route for form submissions
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        print(f"New Message: {name} - {email} - {message}")
        return "<h1>Thank You!</h1><p>Your message has been sent successfully.</p><a href='/'>Go Back</a>"
    return render_template("index.html")

@app.route('/sitemap.xml')
def sitemap():
    return render_template('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

# Statistics page for internal tracking
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
    if not url or "instagram.com" not in url:
        return render_template("index.html", error="Please paste a valid Instagram link", video_url=None)

    # Log request to history
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"Requested URL: {url}\n")
    except:
        pass

    # yt-dlp settings
    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }

    try:
        # Cleanup old files
        old_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        for f in old_files:
            try: os.remove(f)
            except: continue

        # Start download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        # Get the downloaded file
        new_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        if not new_files:
            return render_template("index.html", error="Could not save video.", video_url=None)
            
        latest_file = max(new_files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        
        # Generate secure HTTPS link for the video
        video_path = url_for('serve_video', filename=filename, _external=True, _scheme='https')

        return render_template("index.html", video_url=video_path)

    except Exception as e:
        print(f"Error: {e}")
        return render_template("index.html", error="Failed to fetch video.", video_url=None)

# Route to serve the video file securely
@app.route("/downloads/<filename>")
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    # Ensure dynamic port for cloud deployment
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
