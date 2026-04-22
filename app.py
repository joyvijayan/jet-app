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

# --- New Route for robots.txt (Google AdSense Fix) ---
@app.route('/robots.txt')
def robots_txt():
    content = "User-agent: *\nAllow: /"
    return Response(content, mimetype='text/plain')

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

# --- UPDATED CONTACT ROUTE TO FIX 'METHOD NOT ALLOWED' ---
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Collecting data from your new 4 boxes
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")
        
        # This will print the message in your server logs
        print(f"New Message: {name} - {email} - {subject} - {message}")
        
        # After submission, it shows a success message
        return "<h1>Thank You!</h1><p>Your message has been sent successfully.</p><a href='/'>Go Back</a>"
    
    # If it's a normal visit (GET), it shows the contact page
    return render_template("index.html") 

@app.route('/sitemap.xml')
def sitemap():
    return render_template('sitemap.xml'), 200, {'Content-Type': 'application/xml'}

@app.route("/stats")
def show_stats():
    count = 0
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            count = len(f.readlines())
    return f"<h1>Total Downloads: {count}</h1>"

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")

    if not url or "instagram.com" not in url:
        return render_template("index.html", error="Please paste a valid Instagram link", video_url=None)

    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"Requested URL: {url}\n")
    except Exception as log_error:
        print(f"Logging Error: {log_error}")

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        for f in files:
            try:
                os.remove(f)
            except:
                continue

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)

        new_files = glob.glob(f"{DOWNLOAD_FOLDER}/*")
        if not new_files:
            return render_template("index.html", error="Could not save video", video_url=None)
            
        latest_file = max(new_files, key=os.path.getctime)
        filename = os.path.basename(latest_file)
        
        # --- FIXED LINE BELOW ---
        video_path = f"/downloads/{filename}"

        return render_template("index.html", video_url=video_path)

    except Exception as e:
        print(f"Download Error: {e}")
        return render_template("index.html", error="Failed to fetch video. Try another link.", video_url=None)

@app.route("/downloads/<filename>")
def serve_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
