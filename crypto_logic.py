import os
import hashlib
import logging
from typing import Tuple, Optional

from Crypto.Cipher import AES, Blowfish
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# Configure logging
logger = logging.getLogger(__name__)

# Constants
CHUNK_SIZE = 64 * 1024  # 64KB chunks for memory efficiency
MAX_FILE_SIZE_MB = 500
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'wmv'}

class CryptoService:
    """Service class for handling file encryption and decryption."""
    
    @staticmethod
    def _get_params(algorithm: str, password: str) -> Tuple[object, int, bytes]:
        """derive cipher class, block size, and key from algorithm and password."""
        digest = hashlib.sha256(password.encode('utf-8')).digest()
        
        if algorithm == 'AES':
            # AES-256 requires 32 bytes key, block size 16
            return AES, AES.block_size, digest
        elif algorithm == 'Blowfish':
            # Blowfish implementation uses 16 bytes key, block size 8
            return Blowfish, Blowfish.block_size, digest[:16]
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

    @staticmethod
    def encrypt_file(input_path: str, output_path: str, password: str, algorithm: str) -> Tuple[bool, str]:
        """
        Encrypts a file using the specified algorithm (AES or Blowfish) in CBC mode.
        Uses streaming (chunking) to handle large files efficiently.
        """
        try:
            CipherClass, block_size, key = CryptoService._get_params(algorithm, password)
            
            # Generate random IV
            iv = get_random_bytes(block_size)
            cipher = CipherClass.new(key, CipherClass.MODE_CBC, iv)
            
            with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
                # Write IV to the beginning of the file
                f_out.write(iv)
                
                while True:
                    chunk = f_in.read(CHUNK_SIZE)
                    if len(chunk) == 0:
                        break
                    
                    is_last_chunk = False
                    current_pos = f_in.tell()
                    if not f_in.read(1):
                        is_last_chunk = True
                    f_in.seek(current_pos)
                    
                    if is_last_chunk:
                        ciphertext = cipher.encrypt(pad(chunk, block_size))
                        f_out.write(ciphertext)
                        break
                    else:
                        ciphertext = cipher.encrypt(chunk)
                        f_out.write(ciphertext)

            return True, "File berhasil dienkripsi."

        except Exception as e:
            logger.error(f"Encrypt error: {e}")
            return False, f"Enkripsi gagal: {str(e)}"

    @staticmethod
    def decrypt_file(input_path: str, output_path: str, password: str, algorithm: str) -> Tuple[bool, str]:
        """
        Decrypts a file using the specified algorithm.
        Uses streaming to handle large files efficiently.
        """
        try:
            CipherClass, block_size, key = CryptoService._get_params(algorithm, password)
            
            with open(input_path, 'rb') as f_in:
                # Read IV
                iv = f_in.read(block_size)
                if len(iv) != block_size:
                    return False, "File corrupt or invalid IV."
                
                cipher = CipherClass.new(key, CipherClass.MODE_CBC, iv)
                
                with open(output_path, 'wb') as f_out:
                    while True:
                        chunk = f_in.read(CHUNK_SIZE)
                        
                        if len(chunk) == 0:
                            break
                            
                        # Check if this is the last chunk
                        current_pos = f_in.tell()
                        next_byte = f_in.read(1)
                        f_in.seek(current_pos)
                        is_last_chunk = len(next_byte) == 0
                        
                        if is_last_chunk:
                            try:
                                decrypted_chunk = cipher.decrypt(chunk)
                                plaintext = unpad(decrypted_chunk, block_size)
                                f_out.write(plaintext)
                            except ValueError:
                                return False, "Padding error (wrong password or corrupt file)."
                        else:
                            decrypted_chunk = cipher.decrypt(chunk)
                            f_out.write(decrypted_chunk)
                            
            return True, "File berhasil didekripsi."

        except Exception as e:
            logger.error(f"Decrypt error: {e}")
            return False, f"Dekripsi gagal: {str(e)}"


def hitung_sha256(filepath: str) -> Optional[str]:
    """Calculates SHA-256 hash of a file efficiently."""
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error hashing file: {e}")
        return None

def safe_remove(filepath: Optional[str]) -> bool:
    """Safely removes a file."""
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            logger.error(f"Error removing file {filepath}: {e}")
            return False
    return False

def validasi_file_video(filepath: str, allowed_extensions: set) -> Tuple[bool, str]:
    """Validates the uploaded video file."""
    if not os.path.exists(filepath):
        return False, "File tidak ditemukan"
    
    filename = os.path.basename(filepath)
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if ext not in allowed_extensions:
        return False, f"Ekstensi file tidak diizinkan."
    
    size_mb = os.path.getsize(filepath) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return False, f"File terlalu besar ({size_mb:.2f} MB). Maksimal {MAX_FILE_SIZE_MB} MB"
    
    return True, "File valid"