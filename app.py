from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Hàm tải video dùng yt_dlp
def download_video(url, quality):
    format_map = {
        'mp4_720': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'mp4_480': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        'mp3': 'bestaudio/best'
    }
    selected_format = format_map.get(quality, 'bestvideo+bestaudio/best')

    ext = 'mp3' if quality == 'mp3' else 'mp4'
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'format': selected_format,
        'merge_output_format': ext,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }] if quality == 'mp3' else []
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# Trang chủ - nhập link và tải video
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        quality = request.form.get('quality')
        if not url:
            flash('⚠️ Vui lòng nhập link video.', 'error')
            return redirect(url_for('index'))
        try:
            filename = download_video(url, quality)
            short_name = os.path.basename(filename)
            flash(f'✅ Video đã tải: {short_name}', 'success')
            return redirect(url_for('download_file', filename=short_name))
        except Exception as e:
            flash(f'❌ Lỗi: {str(e)}', 'error')
            return redirect(url_for('index'))
    return render_template('index.html')

# Endpoint tải file sau khi đã tải xong
@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)