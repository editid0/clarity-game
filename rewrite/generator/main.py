from PIL import Image, ImageFilter
import os
from pathlib import Path

files = [
    file
    for file in os.listdir("source")
    if (
        file.lower().endswith("jpg")
        or file.lower().endswith("jpeg")
        or file.lower().endswith("png")
    )
]
output_dir = "out"

for file in files:
    num = input("Which number do you want this image to be? ")
    if not num.isdigit():
        exit(1)
    base = Image.open(Path("source", file))
    blur_1 = base.filter(ImageFilter.GaussianBlur(radius=15))
    blur_2 = blur_1.filter(ImageFilter.GaussianBlur(radius=25))
    blur_3 = blur_2.filter(ImageFilter.GaussianBlur(radius=35))
    blur_4 = blur_3.filter(ImageFilter.GaussianBlur(radius=45))

    base.save(f"{output_dir}/{num}-0.jpg", format="jpeg", quality=80)
    blur_1.save(f"{output_dir}/{num}-1.jpg", format="jpeg", quality=80)
    blur_2.save(f"{output_dir}/{num}-2.jpg", format="jpeg", quality=80)
    blur_3.save(f"{output_dir}/{num}-3.jpg", format="jpeg", quality=80)
    blur_4.save(f"{output_dir}/{num}-4.jpg", format="jpeg", quality=80)
    os.remove(Path("source", file))
