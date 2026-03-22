from PIL import Image, ImageDraw
import os

def create_image(size, filename, color):
    img = Image.new('RGB', size, color=color)
    d = ImageDraw.Draw(img)
    w, h = size
    cx, cy = w//2, h//2
    thickness = w//5
    length = w//2
    # Draw a simple medical cross
    d.rectangle([cx-thickness//2, cy-length//2, cx+thickness//2, cy+length//2], fill='white')
    d.rectangle([cx-length//2, cy-thickness//2, cx+length//2, cy+thickness//2], fill='white')
    img.save(filename)

# Ensure static folder exists
os.makedirs('static', exist_ok=True)

# Generate assets
create_image((192, 192), 'static/icon-192.png', '#2563eb')
create_image((512, 512), 'static/icon-512.png', '#2563eb')
create_image((1080, 1920), 'static/screenshot1.png', '#f8fafc')

print("Icons successfully generated!")
