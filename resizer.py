from PIL import Image

image_path = "screen3.png"
img = Image.open(image_path)

# Resize to exactly 408x500
img_resized = img.resize((458, 550))
img_resized.save("screen3.png")  # Save the corrected image

print("Resized image saved as screen3.png")

