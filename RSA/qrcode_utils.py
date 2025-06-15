import qrcode # type: ignore
import base64
import hashlib

def generate_qr_code(file_data, signature, filename, output_path):
    sha256 = hashlib.sha256(file_data).hexdigest()
    data = {
        "filename": filename,
        "sha256": sha256,
        "signature": base64.b64encode(signature).decode()
    }
    img = qrcode.make(data)
    img.save(output_path)
