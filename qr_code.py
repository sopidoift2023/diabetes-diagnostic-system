import qrcode
import os
from PIL import Image


def create_diabetes_qr_code():
    # Your live website URL
    url = "https://OriereEmmanuel.pythonanywhere.com"

    # Create QR code with professional settings
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=12,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Generate QR image with professional colors
    qr_img = qr.make_image(fill_color="#2E86AB", back_color="#FFFFFF")

    # Save in your project root directory
    qr_img.save("diabetes_system_qr.png")

    # Get the full file path
    file_path = os.path.join(os.getcwd(), "diabetes_system_qr.png")

    print("QR Code Generated Successfully!")
    print(f"File saved at: {file_path}")
    print(f"URL: {url}")



if __name__ == "__main__":
    create_diabetes_qr_code()