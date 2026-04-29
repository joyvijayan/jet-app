
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

# Force HTTPS in production
if Talisman:
    Talisman(app, content_security_policy=None)

# Configuration
DOWNLOAD_FOLDER = "downloads"
LOG_FILE = "download_history.log"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Context processor for secure links
@app.context_processor
def override_url_for():
    return dict(url_for=lambda endpoint, **values: url_for(endpoint, _external=True, _scheme='https', **values) if not app.debug else url_for(endpoint, **values))

# SEO & AdSense Routes
@app.route('/robots.txt')
def robots_txt():
    content = "User-agent: *\nAllow: /"
    return Response(content, mimetype='text/plain')

@app.route('/ads.txt')
def ads_txt():
    return send_from_directory(os.getcwd(), 'ads.txt')

@app.route('/sitemap.xml')
def sitemap():
    return render_template('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

# --- MAIN PAGES ---
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

# --- INDIVIDUAL HTML ROUTES (Soft 404 പരിഹരിക്കാൻ) ---
# ഈ റൂട്ടുകൾ ഉണ്ടെങ്കിൽ മാത്രമേ instajet.online/link-issues.html പോലുള്ള ലിങ്കുകൾ നേരിട്ട് പ്രവർത്തിക്കൂ

@app.route("/link-issues.html")
def link_issues():
    return render_template("link-issues.html")

@app.route("/high-quality.html")
def high_quality():
    return render_template("high-quality.html")

@app.route("/reuse-content.html")
def reuse_content():
    return render_template("reuse-content.html")

@app.route("/reels-guide.html")
def reels_guide():
    return render_template("reels-guide.html")

@app.route("/viral-tips.html")
def viral_tips():
    return render_template("viral-tips.html")

@app.route("/privacy-guide.html")
def privacy_guide():
    return render_template("privacy-guide.html")

@app.route("/posting-time.html")
def posting_time():
    return render_template("posting-time.html")

@app.route("/font-world-guide.html")
def font_world_guide():
    return render_template("font-world-guide.html")

@app.route("/video-king.html")
def video_king():
    return render_template("video-king.html")

@app.route("/unique-fonts.html")
def unique_fonts():
    return render_template("unique-fonts.html")

@app.route("/engagement-guide.html")
def engagement_guide():
    return render_template("engagement-guide.html")

@app.route("/digital-privacy.html")
def digital_privacy():
    return render_template("digital-privacy.html")

@app.route("/viral-captions.html")
def viral_captions():
    return render_template("viral-captions.html")

@app.route("/social-history.html")
def social_history():
    return render_template("social-history.html")

@app.route("/growth-strategies.html")
def growth_strategies():
    return render_template("growth-strategies.html")

# --- BLOG DIRECTORY ACCESS ---
@app.route("/blog")
def blog_home():
    return render_template("blog.html")

@app.route("/blog/<page_name>")
def blog_page(page_name):
    # പഴയ ലിങ്കുകൾ ബ്രേക്ക് ആകാതിരിക്കാൻ ഇത് നിലനിർത്തുന്നു
    valid_pages = [
        "reels-guide", "viral-tips", "privacy-guide", "posting-time", 
        "font-world-guide", "high-quality", "reuse-content", "link-issues", 
        "video-king", "unique-fonts", "engagement-guide", "digital-privacy", 
        "viral-captions", "social-history", "growth-strategies"
    ]
    if page_name in valid_pages:
        return render_template(f"{page_name}.html")
    return "Page not found", 404

# --- DOWNLOAD LOGIC ---
@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url or "instagram.com" not in url:
        return render_template("index.html", error="Please paste a valid Instagram link", video_url=None)

    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"Requested URL: {url}\n")
    except:
        pass

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
        old_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        for f in old_files:
            try: os.remove(f)
            except: continue

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        new_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        if not new_files:
            return render_template("index.html", error="Could not save video.", video_url=None)
            
        latest_file = max(new_files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        video_path = url_for('serve_video', filename=filename, _external=True, _scheme='https')
        return render_template("index.html", video_url=video_path)

    except Exception as e:
        print(f"Error: {e}")
        return render_template("index.html", error="Failed to fetch video.", video_url=None)

@app.route("/downloads/<filename>")
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        return "<h1>Thank You!</h1><p>Your message has been sent successfully.</p><a href='/'>Go Back</a>"
    return render_template("index.html")

@app.route("/stats")
def show_stats():
    count = 0
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            count = len(f.readlines())
    return f"<h1>Total Downloads Requested: {count}</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
