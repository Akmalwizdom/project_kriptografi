import os
import time
import json
import logging
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory
)
from werkzeug.utils import secure_filename

# --- CUSTOM MODULES ---
from crypto_logic import (
    CryptoService, hitung_sha256, safe_remove, validasi_file_video,
    ALLOWED_EXTENSIONS as VIDEO_EXTENSIONS, MAX_FILE_SIZE_MB
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- KONFIGURASI DASAR ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, 'user_uploads')
TEMP_DIR = os.path.join(BASE_DIR, 'output_temp')
RESULTS_FILE = os.path.join(BASE_DIR, 'test_results.json')

app.config.update(
    SECRET_KEY='inirAhas1aB4n9etK3y',
    UPLOAD_FOLDER=UPLOAD_DIR,
    TEMP_FOLDER=TEMP_DIR,
    MAX_CONTENT_LENGTH=MAX_FILE_SIZE_MB * 1024 * 1024,
    RESULTS_FILE=RESULTS_FILE
)

ALLOWED_EXTENSIONS = VIDEO_EXTENSIONS | {'enc'}
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# --- UTILITAS ---
def get_file_size_mb(filepath):
    return round(os.path.getsize(filepath) / (1024 * 1024), 2) if os.path.exists(filepath) else 0

def load_results():
    if not os.path.exists(RESULTS_FILE): return {'encryption': [], 'decryption': []}
    try:
        with open(RESULTS_FILE, 'r') as f: return json.load(f)
    except Exception as e:
        logger.error(f"Error loading results: {e}")
        return {'encryption': [], 'decryption': []}

def save_result(result_type, data):
    results = load_results()
    results.setdefault(result_type, []).append({**data, 'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")})
    try:
        with open(RESULTS_FILE, 'w') as f: json.dump(results, f, indent=4)
        logger.info(f"Result saved: {result_type}")
    except Exception as e: logger.error(f"Error saving result: {e}")

# --- HALAMAN UTAMA ---
@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(413)
def too_large(e):
    flash(f'File terlalu besar (maks {MAX_FILE_SIZE_MB} MB).', 'error')
    return redirect(url_for('index'))

# --- MODE ENKRIPSI / DEKRIPSI ---
@app.route('/mode/encrypt')
def mode_encrypt():
    session.clear()
    session['mode'] = 'encrypt'
    return render_template('select_algorithm.html', mode='encrypt')

@app.route('/mode/decrypt')
def mode_decrypt():
    session.clear()
    session['mode'] = 'decrypt'
    return render_template('select_algorithm.html', mode='decrypt')

# --- UPLOAD FILE ---
@app.route('/upload/<algorithm>', methods=['GET', 'POST'])
def upload_file(algorithm):
    if algorithm not in ['AES', 'Blowfish']:
        flash('Algoritma tidak valid.', 'error')
        return redirect(url_for('index'))
    mode = session.get('mode', 'encrypt')
    if request.method == 'GET':
        return render_template('upload.html', algorithm=algorithm, mode=mode)
    
    file = request.files.get('video_file')
    password = request.form.get('password')
    
    if not file or file.filename == '' or not password:
        flash('File dan password wajib diisi.', 'error')
        return redirect(url_for('upload_file', algorithm=algorithm))
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    if mode == 'encrypt':
        valid, msg = validasi_file_video(filepath, VIDEO_EXTENSIONS)
    else:
        valid = filename.lower().endswith('.enc')
        msg = "File untuk dekripsi harus berekstensi .enc" if not valid else ""
    
    if not valid:
        safe_remove(filepath)
        flash(f'Validasi gagal: {msg}', 'error')
        return redirect(url_for('upload_file', algorithm=algorithm))
        
    session.update({'algorithm': algorithm, 'uploaded_file': filename, 'uploaded_path': filepath, 'password': password})
    return redirect(url_for('process_encrypt' if mode == 'encrypt' else 'process_decrypt'))

# --- PROSES ENKRIPSI ---
@app.route('/process/encrypt')
def process_encrypt():
    if 'uploaded_path' not in session: return redirect(url_for('index'))
    algorithm, password, src, filename = session['algorithm'], session['password'], session['uploaded_path'], session['uploaded_file']
    encrypted_filename = f"{filename}.enc"
    encrypted_path = os.path.join(app.config['TEMP_FOLDER'], encrypted_filename)
    
    try:
        original_hash = hitung_sha256(src)
        if not original_hash: raise Exception("Gagal menghitung hash file asli")
        start = time.time()
        
        # Gunakan CryptoService
        success, msg = CryptoService.encrypt_file(src, encrypted_path, password, algorithm)
        
        dur = round(time.time() - start, 2)
        if not success: raise Exception(msg)
        logger.info(f"Enkripsi {algorithm} berhasil dalam {dur} detik")
    except Exception as e:
        flash(f'Enkripsi gagal: {e}', 'error')
        safe_remove(encrypted_path)
        return redirect(url_for('index'))
        
    save_result('encryption', {'file_name': filename, 'size_mb': get_file_size_mb(src), 'algorithm': algorithm, 'time': dur})
    session['file_info'] = {
        'original_filename': filename, 'original_path': src,
        'encrypted_filename': encrypted_filename, 'encrypted_path': encrypted_path,
        'algorithm': algorithm, 'password': password, 'original_hash': original_hash, 'encryption_time': dur
    }
    flash(f'Enkripsi berhasil dalam {dur} detik.', 'success')
    return redirect(url_for('encryption_result'))

@app.route('/result/encrypt')
def encryption_result():
    if 'file_info' not in session: return redirect(url_for('index'))
    return render_template('result_encrypt.html', file_info=session['file_info'])

# --- DEKRIPSI SEKARANG ---
@app.route('/decrypt-now', methods=['POST'])
def decrypt_now():
    if 'file_info' not in session: return redirect(url_for('index'))
    file_info = session['file_info']
    session.update({
        'mode': 'decrypt', 'algorithm': file_info['algorithm'], 'uploaded_file': file_info['encrypted_filename'],
        'uploaded_path': file_info['encrypted_path'], 'password': file_info['password'],
        'original_hash_for_decryption': file_info.get('original_hash')
    })
    return redirect(url_for('process_decrypt'))

# --- PROSES DEKRIPSI ---
@app.route('/process/decrypt')
def process_decrypt():
    if 'uploaded_path' not in session: return redirect(url_for('index'))
    algorithm, password, enc_path, enc_filename, orig_hash = session['algorithm'], session['password'], session['uploaded_path'], session['uploaded_file'], session.get('original_hash_for_decryption')
    
    if not os.path.exists(enc_path):
        flash('File terenkripsi tidak ditemukan.', 'error')
        return redirect(url_for('index'))
        
    base_name = enc_filename[:-4] if enc_filename.endswith('.enc') else enc_filename
    original_ext = base_name.rsplit('.', 1)[1] if '.' in base_name else 'mp4'
    dec_filename = f"{base_name.rsplit('.', 1)[0]}_decrypted.{original_ext}" if '.' in base_name else f"{base_name}_decrypted.mp4"
    dec_path = os.path.join(app.config['TEMP_FOLDER'], dec_filename)
    
    try:
        logger.info(f"Memulai dekripsi: {enc_filename} dengan {algorithm}")
        start = time.time()
        
        # Gunakan CryptoService
        success, msg = CryptoService.decrypt_file(enc_path, dec_path, password, algorithm)
            
        dur = round(time.time() - start, 2)
        if not success: raise Exception(msg)
        logger.info(f"Dekripsi berhasil dalam {dur} detik")
        if not os.path.exists(dec_path) or os.path.getsize(dec_path) == 0:
            raise Exception("File hasil dekripsi kosong atau tidak berhasil dibuat.")
    except Exception as e:
        flash(f'{e}', 'error')
        logger.exception(f"Exception during decryption: {e}")
        safe_remove(dec_path)
        return redirect(url_for('index'))

    is_valid, status = None, "File berhasil didekripsi"
    if orig_hash:
        try:
            dec_hash = hitung_sha256(dec_path)
            is_valid = dec_hash == orig_hash
            status = "✓ File berhasil didekripsi dan integritas terverifikasi" if is_valid else "✗ File didekripsi tetapi integritas tidak cocok (kemungkinan password salah)."
        except Exception as e: status = f"File didekripsi tetapi gagal verifikasi hash: {e}"
    else: status = "File berhasil didekripsi (tidak ada verifikasi integritas)"
    
    save_result('decryption', {'file_name': enc_filename, 'size_mb': get_file_size_mb(enc_path), 'algorithm': algorithm, 'time': dur, 'status': status, 'is_valid': is_valid})
    session['decrypted_info'] = {'filename': dec_filename, 'decryption_time': dur, 'is_valid': is_valid, 'integrity_status': status, 'path': dec_path, 'size_mb': get_file_size_mb(dec_path)}
    
    return redirect(url_for('decryption_result'))

# --- HALAMAN HASIL DAN DOWNLOAD ---
@app.route('/result/decrypt')
def decryption_result():
    if 'decrypted_info' not in session: return redirect(url_for('index'))
    return render_template('result_decrypt.html', decrypted_info=session['decrypted_info'], original_filename=session.get('uploaded_file', 'Unknown'))

@app.route('/download/<type>/<filename>')
def download_file_route(type, filename):
    folder = app.config['TEMP_FOLDER'] if type in ['encrypted', 'decrypted'] else app.config['UPLOAD_FOLDER']
    return send_from_directory(folder, filename, as_attachment=True)

@app.route('/preview/<filename>')
def preview_video(filename):
    return send_from_directory(app.config['TEMP_FOLDER'], filename)

@app.route('/clear-session')
def clear_session_files():
    safe_remove(session.get('uploaded_path'))
    if 'file_info' in session:
        safe_remove(session['file_info'].get('encrypted_path'))
        safe_remove(session['file_info'].get('original_path'))
    if 'decrypted_info' in session:
        safe_remove(session['decrypted_info'].get('path'))
    session.clear()
    flash('Session & file sementara dibersihkan.', 'info')
    return redirect(url_for('index'))

@app.route('/test-results')
def test_results():
    data = load_results()
    encryption_data = data.get('encryption', [])
    decryption_data = data.get('decryption', [])
    
    merged_data = {}
    
    for enc_item in encryption_data:
        key = f"{enc_item['file_name']}|{enc_item['algorithm']}"
        merged_data[key] = {
            'filename': enc_item['file_name'],
            'algorithm': enc_item['algorithm'],
            'encryption_time': enc_item.get('time'),
            'size_mb': enc_item.get('size_mb', 0),
            'decryption_time': None,
            'is_valid': None
        }
    
    for dec_item in decryption_data:
        original_filename = dec_item['file_name'].replace('.enc', '')
        algorithm = dec_item['algorithm']
        key = f"{original_filename}|{algorithm}"
        if key in merged_data:
            merged_data[key]['decryption_time'] = dec_item.get('time')
            merged_data[key]['is_valid'] = dec_item.get('is_valid')
    
    test_data = list(merged_data.values())
    test_data.sort(key=lambda x: (x['filename'], x['algorithm']))
    
    logger.info(f"Total test data untuk ditampilkan: {len(test_data)}")
    
    return render_template('test_results.html', test_data=test_data)

if __name__ == '__main__':
    logger.info("Starting SecureVault Video Application")
    app.run(debug=True, host='0.0.0.0', port=5000)