import os
from src.utils import clean_title

SUPPORTED_EXTENSIONS = {
    '.iso', '.bin', '.img', '.n64', '.smc', '.gba', '.gcn', '.cue', '.elf', '.rpx', '.rvz', '.nes', '.z64', '.sfc',
}

def scan_roms(rom_base_dir, cover_base_dir):
    game_list = []

    # --- Scan dev_hdd0 for installed PS3 games ---
    installed_ps3_path = os.path.join("Emulators", "RPCS3", "dev_hdd0", "game")
    ps3_cover_path = os.path.join(cover_base_dir, "PS3")

    if os.path.exists(installed_ps3_path):
        for game_id in os.listdir(installed_ps3_path):
            game_folder = os.path.join(installed_ps3_path, game_id)
            eboot_path = os.path.join(game_folder, "USRDIR", "EBOOT.BIN")

            if os.path.exists(eboot_path):
                cover_img = os.path.join(ps3_cover_path, f"{game_id}.jpg")
                if not os.path.exists(cover_img):
                    cover_img = os.path.join("assets", "default_cover.png")

                game_list.append({
                    "platform": "PS3",
                    "title": game_id,
                    "rom_path": eboot_path,
                    "cover_path": cover_img
                })

    # --- Scan ROMs/ folders ---
    for platform in os.listdir(rom_base_dir):
        platform_path = os.path.join(rom_base_dir, platform)
        cover_path = os.path.join(cover_base_dir, platform)

        if not os.path.isdir(platform_path):
            continue

        # --- Wii U RPX folder detection ---
        if platform.lower() == "wiiu":
            for game_folder in os.listdir(platform_path):
                game_folder_path = os.path.join(platform_path, game_folder)
                code_dir = os.path.join(game_folder_path, "code")

                if os.path.isdir(code_dir):
                    for file in os.listdir(code_dir):
                        if file.lower().endswith(".rpx"):
                            rpx_path = os.path.join(code_dir, file)
                            cover_img = os.path.join(cover_path, f"{game_folder}.jpg")
                            if not os.path.exists(cover_img):
                                cover_img = os.path.join("assets", "default_cover.png")

                            game_list.append({
                                "platform": platform,
                                "title": game_folder,
                                "rom_path": rpx_path,
                                "cover_path": cover_img
                            })
                            break  # Only load one .rpx per game folder

        # --- Flat file ROMs ---
        for file in os.listdir(platform_path):
            full_rom_path = os.path.join(platform_path, file)
            if not os.path.isfile(full_rom_path):
                continue

            ext = os.path.splitext(file)[1].lower()

            if platform.lower() in ["ps1", "playstation", "playstation1"] and ext != ".cue":
                continue

            if ext not in SUPPORTED_EXTENSIONS:
                continue

            title = os.path.splitext(file)[0]
            cleaned_title = clean_title(title)

            # Try exact match first
            possible_filenames = [f"{title}.jpg", f"{title}.png"]
            potential_cover = None

            for fname in possible_filenames:
                path = os.path.join(cover_path, fname)
                if os.path.exists(path):
                    potential_cover = path
                    break

            # Fuzzy fallback
            if not potential_cover:
                matched_file = None
                if os.path.exists(cover_path):
                    for cover_file in os.listdir(cover_path):
                        if clean_title(os.path.splitext(cover_file)[0]) == cleaned_title and \
                                os.path.splitext(cover_file)[1].lower() in ['.jpg', '.png']:
                            matched_file = cover_file
                            break
                potential_cover = os.path.join(cover_path, matched_file) if matched_file else os.path.join("assets", "default_cover.png")

            game_list.append({
                "platform": platform,
                "title": title,
                "rom_path": full_rom_path,
                "cover_path": potential_cover
            })

    return game_list
