import qrcode
import os
import random
import string

QR_FOLDER = "static/qrcodes"  

os.makedirs(QR_FOLDER, exist_ok=True)

def generate_qr_code(data=None):
    """Generates a QR code and saves it in static/qrcodes/ folder."""
    # generate random data if none provided
    if data is None:
        data = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

    filename = f"{data}.png"  # name QR code based on class code
    filepath = os.path.join(QR_FOLDER, filename)

    # generate and save QR
    img = qrcode.make(data)
    img.save(filepath)

    return filename  # return filename only, not full path
