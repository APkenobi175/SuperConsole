import os
from PIL import Image, ImageTk
import re
def load_image(path, size=(150, 200)):
    """
    Loads an image from disk, resizes it, and returns a Tkinter-compatible PhotoImage.
    If loading fails, falls back to the default cover.
    """
    try:
        img = Image.open(path)
    except Exception:
        img = Image.open(os.path.join("assets", "default_cover.png"))

    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


def get_base_dir():
    """
    Returns the absolute path to the directory where the launcher is located.
    Useful for resolving relative paths when running from an EXE.
    """
    return os.path.dirname(os.path.abspath(__file__))


def is_valid_rom(filename, valid_exts):
    """
    Checks if the given file has a valid ROM extension.
    """
    ext = os.path.splitext(filename)[1].lower()
    return ext in valid_exts

def clean_title(raw_title):
    # Removes things like (USA), [!], Rev 1, etc. and extra characters
    title = re.sub(r"[-_]", " ", raw_title)                    # dashes/underscores → spaces
    title = re.sub(r"\\(.*?\\)|\\[.*?\\]", "", title)          # remove (...) and [...]
    title = re.sub(r"[^a-zA-Z0-9 ]", "", title)                # remove special chars
    return title.strip().lower()


