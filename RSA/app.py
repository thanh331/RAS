from flask import Flask, render_template, request, send_file, jsonify
import os
import hashlib
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import qrcode # type: ignore

app = Flask(__name__)

# Thư mục cấu hình
UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'static/qrcodes' 
KEY_FOLDER = 'keys'

# Đảm bảo các thư mục tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

# Load private key (demo – dùng chung)
def load_private_key():
    with open(os.path.join(KEY_FOLDER, "private_key.pem"), "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sign', methods=['POST'])
def sign_file():
    uploaded_file = request.files['file']
    if not uploaded_file:
        return "Không có file!", 400

    filename = uploaded_file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(filepath)

    # Đọc file
    with open(filepath, "rb") as f:
        file_data = f.read()

    # Băm SHA-256
    file_hash = hashlib.sha256(file_data).hexdigest()

    # Ký bằng RSA
    private_key = load_private_key()
    signature = private_key.sign(
        file_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    # Lưu chữ ký
    sig_filename = filename + ".sig"
    sig_path = os.path.join(UPLOAD_FOLDER, sig_filename)
    with open(sig_path, "wb") as sig_file:
        sig_file.write(signature)

    # Tạo QR chứa thông tin
    signature_b64 = base64.b64encode(signature).decode()
    qr_data = {
        "filename": filename,
        "sha256": file_hash,
        "signature": signature_b64
    }
    qr_img = qrcode.make(str(qr_data))
    qr_filename = filename + ".png"
    qr_path = os.path.join(QR_FOLDER, qr_filename)
    qr_img.save(qr_path)

    return jsonify({
        "filename": filename,
        "signature_file": sig_filename,
        "qr_image": qr_filename
    })

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return "Không tìm thấy file", 404
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
def load_private_key():
    try:
        with open(os.path.join(KEY_FOLDER, "private_key.pem"), "rb") as key_file:
            return serialization.load_pem_private_key(key_file.read(), password=None)
    except Exception as e:
        print("❌ Lỗi khi load private key:", e)
        raise e
