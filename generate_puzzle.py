from PIL import Image, ImageDraw, ImageFont
import random

# Define image dimensions (should match your game window size, e.g., 640x480)
width, height = 640, 480

# Create a new image with a white background
img = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(img)

# Define a list of colors to choose from
colors = ["red", "green", "blue", "orange", "purple", "cyan", "magenta"]

# Draw a pattern of random colored rectangles
for i in range(20):
    # Generate random coordinates and size
    x1 = random.randint(0, width - 50)
    y1 = random.randint(0, height - 50)
    x2 = x1 + random.randint(30, 150)
    y2 = y1 + random.randint(30, 150)
    color = random.choice(colors)
    draw.rectangle([x1, y1, x2, y2], fill=color, outline="black")

# Optionally, add some text to the center
try:
    # Attempt to load a truetype font (if available)
    font = ImageFont.truetype("arial.ttf", 40)
except IOError:
    # Fallback to the default PIL font if arial.ttf is not available
    font = ImageFont.load_default()

text = "Puzzle"
# Use draw.textbbox to get the text dimensions
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_position = ((width - text_width) // 2, (height - text_height) // 2)
draw.text(text_position, text, fill="black", font=font)

# Save the generated image as "puzzle.jpg"
img.save("puzzle.jpg")
print("puzzle.jpg has been generated!")
