import qrcode #pip install qrcode pillow
import random
import string

def generate_qr_code(data=None, filename=None): #both none to generate random string/filename
    # Generate random data if none provided
    if data is None:
        data = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    if filename is None:
        filename = f"QR_{random.randint(1000, 9999)}.png"
    elif not filename.endswith('.png'):
        filename += '.png'

    # Create and save QR code
    img = qrcode.make(data)
    img.save(filename)
    
    return filename

