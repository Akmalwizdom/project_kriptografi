# crypto_logic.py
import os
import hashlib
from Crypto.Cipher import AES, Blowfish
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import gc

UKURAN_CHUNK_BACA = 1024 * 1024  # 1 MB

def dapatkan_kunci_iv(password, salt):
    """
    Menghasilkan kunci 16-byte dan IV 16-byte dari password.
    Kita akan simpan 'salt' (IV) di session untuk dekripsi.
    """
    # Gunakan password dan salt (IV) untuk membuat kunci yang deterministik
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000, 32)[:16]
    return key

def proses_kripto(mode_operasi, algoritma, kunci, iv, file_input, file_output):
    """Fungsi inti dari skrip penelitian Anda, disederhanakan."""
    block_size = AES.block_size if algoritma == 'AES' else Blowfish.block_size
    
    if algoritma == 'AES':
        cipher = AES.new(kunci, AES.MODE_CBC, iv)
    elif algoritma == 'Blowfish':
        # Blowfish hanya menggunakan 8 byte IV
        cipher = Blowfish.new(kunci, Blowfish.MODE_CBC, iv[:8])
    else:
        raise ValueError("Algoritma tidak didukung")

    try:
        with open(file_input, 'rb') as fi, open(file_output, 'wb') as fo:
            if mode_operasi == 'enkripsi':
                while True:
                    chunk = fi.read(UKURAN_CHUNK_BACA)
                    if not chunk:
                        break
                    
                    is_last_chunk = len(chunk) < UKURAN_CHUNK_BACA
                    if is_last_chunk:
                         chunk = pad(chunk, block_size)

                    fo.write(cipher.encrypt(chunk))

            elif mode_operasi == 'dekripsi':
                file_size = os.path.getsize(file_input)
                processed_bytes = 0
                while True:
                    chunk = fi.read(UKURAN_CHUNK_BACA)
                    if not chunk:
                        break
                    
                    processed_bytes += len(chunk)
                    decrypted_chunk = cipher.decrypt(chunk)

                    if processed_bytes == file_size:
                        try:
                            decrypted_chunk = unpad(decrypted_chunk, block_size)
                        except ValueError:
                            pass
                    
                    fo.write(decrypted_chunk)
    finally:
        del cipher
        gc.collect()

def hitung_sha256(nama_file):
    """Menghitung hash SHA-256 dari sebuah file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(nama_file, "rb") as f:
            for byte_block in iter(lambda: f.read(UKURAN_CHUNK_BACA), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def safe_remove(filepath):
    """Menghapus file jika ada."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
        return True
    except PermissionError:
        return False