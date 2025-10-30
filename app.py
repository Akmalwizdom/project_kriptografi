import os
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory
)
from werkzeug.utils import secure_filename
from crypto_logic import proses_kripto, dapatkan_kunci_iv, hitung_sha256, safe_remove
from Crypto.Random import get_random_bytes

app = Flask(__name__)

# --- KONFIGURASI ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'user_uploads')
TEMP_DIR = os.path.join(BASE_DIR, 'output_temp')

# BATAS FILE: 500 MB
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.config['TEMP_FOLDER'] = TEMP_DIR

# Kunci rahasia untuk session
app.config['SECRET_KEY'] = 'inirAhas1aB4n9etK3y'

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'wmv'}

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- ALUR APLIKASI ---

@app.route('/')
def index():
    # serve index.html
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(413)
def request_entity_too_large(error):
    flash(f'File terlalu besar. Batas maksimum adalah 500 MB.', 'error')
    return redirect(url_for('index'))

@app.route('/encrypt', methods=['POST'])
def encrypt_file():
    """Langkah 2: Unggah, Validasi, dan Enkripsi."""

    if 'video_file' not in request.files:
        flash('Tidak ada file yang dipilih.', 'error')
        return redirect(url_for('index'))

    file = request.files['video_file']
    password = request.form.get('password')
    algorithm = request.form.get('algorithm')

    if file.filename == '' or not password or not algorithm:
        flash('Semua field (file, password, algoritma) harus diisi.', 'error')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('Tipe file tidak diizinkan.', 'error')
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    original_filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(original_filepath)

    iv = get_random_bytes(16)
    key = dapatkan_kunci_iv(password, iv)

    encrypted_filename = f"{filename}.enc"
    encrypted_filepath = os.path.join(app.config['TEMP_FOLDER'], encrypted_filename)

    try:
        proses_kripto('enkripsi', algorithm, key, iv, original_filepath, encrypted_filepath)
    except Exception as e:
        flash(f'Terjadi error saat enkripsi: {e}', 'error')
        safe_remove(original_filepath)
        return redirect(url_for('index'))

    session['file_info'] = {
        'original_filename': filename,
        'original_path': original_filepath,
        'original_hash': hitung_sha256(original_filepath),
        'encrypted_filename': encrypted_filename,
        'encrypted_path': encrypted_filepath,
        'algorithm': algorithm,
        'iv': iv.hex()  # Password tidak disimpan
    }

    flash('File berhasil dienkripsi!', 'success')
    return redirect(url_for('encryption_result'))

@app.route('/result')
def encryption_result():
    """Langkah 3: Tampilkan hasil enkripsi."""
    if 'file_info' not in session:
        flash('Session tidak ditemukan. Silakan ulangi proses.', 'error')
        return redirect(url_for('index'))

    file_info = session['file_info']
    return render_template('result.html', file_info=file_info)

@app.route('/decrypt', methods=['POST'])
def decrypt_file():
    """Langkah 4: Proses Dekripsi (sekarang user input password ulang)."""
    if 'file_info' not in session:
        flash('Session tidak ditemukan. Silakan ulangi proses.', 'error')
        return redirect(url_for('index'))

    file_info = session['file_info']

    # 🔹 PASSWORD SEKARANG DIMINTA DARI INPUT FORM
    input_password = request.form.get('password')
    if not input_password:
        flash('Silakan masukkan password untuk dekripsi.', 'error')
        return redirect(url_for('encryption_result'))

    iv = bytes.fromhex(file_info['iv'])
    key = dapatkan_kunci_iv(input_password, iv)
    algorithm = file_info['algorithm']
    encrypted_filepath = file_info['encrypted_path']

    decrypted_filename = f"decrypted_{file_info['original_filename']}"
    decrypted_filepath = os.path.join(app.config['TEMP_FOLDER'], decrypted_filename)

    try:
        proses_kripto('dekripsi', algorithm, key, iv, encrypted_filepath, decrypted_filepath)
    except Exception as e:
        flash(f'Error saat dekripsi: {e}. Kemungkinan password salah.', 'error')
        return redirect(url_for('encryption_result'))

    decrypted_hash = hitung_sha256(decrypted_filepath)
    original_hash = file_info['original_hash']

    is_valid = (decrypted_hash == original_hash)

    session['decrypted_info'] = {
        'filename': decrypted_filename,
        'path': decrypted_filepath,
        'is_valid': is_valid
    }

    session.modified = True

    return redirect(url_for('decryption_final'))

@app.route('/final')
def decryption_final():
    """Langkah 5: Tampilkan hasil akhir dekripsi."""
    if 'decrypted_info' not in session:
        flash('Belum ada hasil dekripsi.', 'error')
        return redirect(url_for('index'))

    return render_template('final.html',
                           decrypted_info=session['decrypted_info'],
                           original_filename=session['file_info']['original_filename'])

@app.route('/download/<type>/<filename>')
def download_file(type, filename):
    """Mengizinkan pengguna mengunduh file .enc atau hasil dekripsi."""
    directory = app.config['TEMP_FOLDER']
    if type == 'original':
        directory = app.config['UPLOAD_FOLDER']

    return send_from_directory(directory, filename, as_attachment=True)

@app.route('/clear')
def clear_session_files():
    """Membersihkan file fisik dari session."""
    if 'file_info' in session:
        safe_remove(session['file_info'].get('original_path'))
        safe_remove(session['file_info'].get('encrypted_path'))
    if 'decrypted_info' in session:
        safe_remove(session['decrypted_info'].get('path'))

    session.clear()
    flash('Session dan file sementara telah dibersihkan.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)