import os
import qrcode
from PIL import Image
def generate_qrcode(url:str):
    """it generates qrcode for the url of the user profile"""
    if os.path.exists("./Notification/qr-code-store/images/Warehouse-qrcode.png"):
        os.remove("./Notification/qr-code-store/images/Warehouse-qrcode.png")
    Logo_link = "./static/images/warehouse-icon.png"
    logo = Image.open(Logo_link)
    basewidth = 75 #Please Enter the Base Width [Default=75]:
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth,hsize), Image.ANTIALIAS)
    qr_big = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr_big.add_data(url)
    qr_big.make()
    qr_color ="#f57ddd"# input('What Color Would You like Your QR Code to be? [Default=Black]: ' or 'Black')
    img_qr_big = qr_big.make_image(fill_color=qr_color, back_color="white").convert('RGB')
    pos = ((img_qr_big.size[0] - logo.size[0]) // 2, (img_qr_big.size[1] - logo.size[1]) // 2)
    img_qr_big.paste(logo, pos)
    save_path = "./Notification/qr-code-store/images/Warehouse-qrcode.png"#Please enter the filename you want for your branded qr code:
    img_qr_big.save(save_path)