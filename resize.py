from PIL import Image

# Check the image size
image_path = "screen1.png"  # Change to your actual image filename
img = Image.open(image_path)
print(f"Image dimensions: {img.size}")  # (width, height)

