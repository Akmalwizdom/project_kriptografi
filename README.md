<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Security-AES%20%7C%20Blowfish-00C853?style=for-the-badge&logo=gnuprivacyguard&logoColor=white" alt="Security"/>
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License"/>
</p>

<h1 align="center">SecureVault Video</h1>

<p align="center">
  <strong>Military-Grade Video Encryption & Decryption Platform</strong>
</p>

<p align="center">
  Secure your video assets with AES-256 and Blowfish encryption algorithms.<br/>
  Simple. Fast. Reliable.
</p>

---

## Features

| Feature | Description |
|---------|-------------|
| **Dual Encryption Algorithms** | Choose between AES-256-CBC or Blowfish-CBC for maximum security |
| **Multi-Format Support** | Supports MP4, MOV, AVI, MKV, and WMV video formats |
| **Streaming Encryption** | Memory-efficient chunk-based processing for large files (up to 500MB) |
| **Password Protection** | Secure key derivation using SHA-256 hashing |
| **Integrity Verification** | SHA-256 hash verification ensures file integrity after decryption |
| **Benchmark Results** | Track and compare encryption/decryption performance |
| **Modern UI** | Beautiful glassmorphism design with dark mode |

---

## Security Algorithms

### AES-256 (Advanced Encryption Standard)
- **Key Size**: 256-bit
- **Block Size**: 128-bit
- **Mode**: CBC (Cipher Block Chaining)
- **Use Case**: Industry standard for secure file encryption

### Blowfish
- **Key Size**: 128-bit
- **Block Size**: 64-bit  
- **Mode**: CBC (Cipher Block Chaining)
- **Use Case**: Fast encryption for legacy compatibility

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Akmalwizdom/project_kriptografi.git
   cd project_kriptografi
   ```

2. **Create virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## Project Structure

```
securevault-video/
├── app.py                 # Main Flask application
├── crypto_logic.py        # Encryption/decryption logic
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html             # Base layout template
│   ├── index.html            # Home page
│   ├── select_algorithm.html # Algorithm selection
│   ├── upload.html           # File upload page
│   ├── result_encrypt.html   # Encryption result
│   ├── result_decrypt.html   # Decryption result
│   └── test_results.html     # Benchmark results
├── static/                # Static assets (CSS, JS)
├── user_uploads/          # Temporary upload storage
└── output_temp/           # Processed files output
```

---

## Usage Guide

### Encrypting a Video

1. Click **"Enkripsi Video"** on the home page
2. Select your preferred algorithm (**AES** or **Blowfish**)
3. Upload your video file (max 500MB)
4. Enter a secure password
5. Click **"Encrypt"** and download your `.enc` file

### Decrypting a Video

1. Click **"Dekripsi Video"** on the home page
2. Select the algorithm used during encryption
3. Upload the `.enc` file
4. Enter the correct password
5. Click **"Decrypt"** and download your restored video

---

## Performance Benchmarks

The application includes built-in benchmarking to compare encryption algorithms:

| Metric | AES-256 | Blowfish |
|--------|---------|----------|
| Security Level | High | Medium-High |
| Encryption Speed | Fast | Faster |
| Block Size | 128-bit | 64-bit |
| Recommended For | High Security | Speed Priority |

> Access benchmarks at `/test-results` to view your encryption/decryption history.

---

## Security Best Practices

> [!IMPORTANT]
> Follow these guidelines to maximize security:

- Use strong, unique passwords (12+ characters with mixed case, numbers, symbols)
- Store encrypted files and passwords separately
- Remember your password - there's no recovery option
- Verify file integrity after decryption using the built-in hash check
- Never share your encryption password over unsecured channels

---

## Technical Details

### Encryption Process

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Video File │ ──► │ SHA-256 Key  │ ──► │ CBC Encryption  │
│   (Input)   │     │  Derivation  │     │ (AES/Blowfish)  │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                  │
                    ┌──────────────┐              │
                    │ .enc Output  │ ◄────────────┘
                    │  (IV + Data) │
                    └──────────────┘
```

### Key Features

- **Chunked Processing**: Files are processed in 64KB chunks for memory efficiency
- **Random IV Generation**: Each encryption uses a unique Initialization Vector
- **PKCS7 Padding**: Standard padding scheme for block cipher alignment
- **Secure File Cleanup**: Temporary files are safely removed after processing

---

## Dependencies

| Package | Purpose |
|---------|---------|
| Flask | Web framework |
| PyCryptodome | Cryptographic operations |
| psutil | System monitoring |

---

<p align="center">
  <strong>Secure Your Videos with Confidence</strong>
</p>

<p align="center">
  Made for Cryptography Class Project
</p>
