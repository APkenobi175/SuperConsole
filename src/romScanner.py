import os
from src.utils import clean_title

# Supported ROM file types
SUPPORTED_EXTENSIONS = {
    '.iso', '.bin', '.img', '.n64', '.smc', '.gba', '.gcn', '.cue', '.elf', '.rpx'
}

def scan_roms(rom_base_dir, cover_base_dir):
    """
    Scans the ROMs directory and returns a list of game dictionaries.
    Handles both flat ROM files and structured folders (like for Wii U).
    """
    game_list = []

    for platform in os.listdir(rom_base_dir):
        platform_path = os.path.join(rom_base_dir, platform)
        cover_path = os.path.join(cover_base_dir, platform)

        if not os.path.isdir(platform_path):
            continue

        # -- Wii U folder-style scanning --
        for game_folder in os.listdir(platform_path):
            game_folder_path = os.path.join(platform_path, game_folder)

            # Look for structured game folders like Zelda BOTW
            rpx_path = os.path.join(game_folder_path, "code", "U-King.rpx")
            if os.path.exists(rpx_path):
                cover_img = os.path.join(cover_path, f"{game_folder}.jpg")
                if not os.path.exists(cover_img):
                    cover_img = os.path.join("assets", "default_cover.png")

                game_list.append({
                    "platform": platform,
                    "title": game_folder,
                    "rom_path": rpx_path,
                    "cover_path": cover_img
                })

        # -- Standard ROM file scanning --
        for file in os.listdir(platform_path):
            full_rom_path = os.path.join(platform_path, file)

            if not os.path.isfile(full_rom_path):
                continue

            ext = os.path.splitext(file)[1].lower()

            # PS1 rule: only accept .cue
            if platform.lower() in ["ps1", "playstation", "playstation1"] and ext != ".cue":
                continue

            if ext not in SUPPORTED_EXTENSIONS:
                continue

            title = os.path.splitext(file)[0]
            cleaned_title = clean_title(title)

            # Try exact match for JPG and PNG
            possible_filenames = [f"{title}.jpg", f"{title}.png"]
            potential_cover = None

            for fname in possible_filenames:
                path = os.path.join(cover_path, fname)
                if os.path.exists(path):
                    potential_cover = path
                    break

            # Fuzzy fallback
            if not potential_cover:
                cleaned_title = clean_title(title)
                matched_file = None

                if os.path.exists(cover_path):
                    for cover_file in os.listdir(cover_path):
                        if clean_title(os.path.splitext(cover_file)[0]) == cleaned_title and \
                                os.path.splitext(cover_file)[1].lower() in ['.jpg', '.png']:
                            matched_file = cover_file
                            break

                if matched_file:
                    potential_cover = os.path.join(cover_path, matched_file)
                else:
                    potential_cover = os.path.join("assets", "default_cover.png")

            game_list.append({
                "platform": platform,
                "title": title,
                "rom_path": full_rom_path,
                "cover_path": potential_cover
            })

    return game_list
