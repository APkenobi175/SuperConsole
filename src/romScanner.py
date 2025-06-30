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

        # --- Wii hybrid support: both .rvz files and folder-based WBFS ---
        if platform.lower() == "wii":
            # Handle flat RVZ, ISO, WBFS in root of /Wii
            for file in os.listdir(platform_path):
                full_path = os.path.join(platform_path, file)
                ext = os.path.splitext(file)[1].lower()

                if not os.path.isfile(full_path) or ext not in ['.rvz', '.iso', '.wbfs']:
                    continue

                title = os.path.splitext(file)[0]
                cleaned_title = clean_title(title)
                cover_img = os.path.join(cover_path, f"{title}.png")
                if not os.path.exists(cover_img):
                    cover_img = os.path.join("assets", "default_cover.png")

                game_list.append({
                    "platform": platform,
                    "title": title,
                    "rom_path": full_path,
                    "cover_path": cover_img
                })

            # Handle subfolders with WBFS files and game IDs
            for folder in os.listdir(platform_path):
                folder_path = os.path.join(platform_path, folder)
                if not os.path.isdir(folder_path):
                    continue

                # Extract game ID from folder name like "Game Title [GAMEID]"
                game_id = folder.split('[')[-1].split(']')[0] if '[' in folder and ']' in folder else ""
                title = folder.split('[')[0].strip() if '[' in folder else folder

                wbfs_file = None
                for f in os.listdir(folder_path):
                    if f.lower().endswith('.wbfs'):
                        wbfs_file = os.path.join(folder_path, f)
                        break

                if not wbfs_file:
                    continue

                # Cover by GAMEID
                cover_img = os.path.join(cover_path, f"{game_id}.png") if game_id else os.path.join("assets",
                                                                                                    "default_cover.png")
                if not os.path.exists(cover_img):
                    cover_img = os.path.join("assets", "default_cover.png")

                game_list.append({
                    "platform": platform,
                    "title": title,
                    "rom_path": wbfs_file,
                    "cover_path": cover_img
                })


            continue  # Skip the flat-file scanner for Wii

        if platform.lower() == "gamecube":
            for entry in os.listdir(platform_path):
                full_path = os.path.join(platform_path, entry)

                # --- Handle folder-based games ---
                if os.path.isdir(full_path):
                    iso_file = None
                    for subfile in os.listdir(full_path):
                        if subfile.lower().endswith(".iso"):
                            iso_file = subfile
                            break
                    if not iso_file:
                        continue  # Skip folders with no ISO

                    # Attempt to extract GameID
                    game_id = ""
                    if "[" in entry and "]" in entry:
                        game_id = entry.split('[')[-1].split(']')[0]
                        title = entry.split('[')[0].strip()
                    else:
                        # Check for GameID-looking text at end (like "Mario Kart GGPE01")
                        parts = entry.split()
                        last_part = parts[-1] if parts else ""
                        game_id = last_part if len(last_part) == 6 else ""
                        title = entry.replace(game_id, "").strip() if game_id else entry

                    # Cover matching
                    cover_img = os.path.join(cover_path, f"{game_id}.png") if game_id else None
                    if not cover_img or not os.path.exists(cover_img):
                        # fallback to fuzzy match
                        matched_file = None
                        if os.path.exists(cover_path):
                            for cover_file in os.listdir(cover_path):
                                if clean_title(os.path.splitext(cover_file)[0]) == clean_title(title):
                                    matched_file = cover_file
                                    break
                        cover_img = os.path.join(cover_path, matched_file) if matched_file else os.path.join("assets", "default_cover.png")

                    game_list.append({
                        "platform": platform,
                        "title": title,
                        "rom_path": os.path.join(full_path, iso_file),
                        "cover_path": cover_img
                    })

                # --- Flat ISO files ---
                elif os.path.isfile(full_path) and entry.lower().endswith(".iso"):
                    title = os.path.splitext(entry)[0]
                    cleaned_title = clean_title(title)

                    cover_img = None
                    for ext in ['.png', '.jpg']:
                        if os.path.exists(os.path.join(cover_path, title + ext)):
                            cover_img = os.path.join(cover_path, title + ext)
                            break

                    if not cover_img and os.path.exists(cover_path):
                        for cover_file in os.listdir(cover_path):
                            if clean_title(os.path.splitext(cover_file)[0]) == cleaned_title:
                                cover_img = os.path.join(cover_path, cover_file)
                                break

                    if not cover_img:
                        cover_img = os.path.join("assets", "default_cover.png")

                    game_list.append({
                        "platform": platform,
                        "title": title,
                        "rom_path": full_path,
                        "cover_path": cover_img
                    })

        # --- Flat file ROMs for all other platforms ---
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
            cover_img = None
            for ext_img in ['.jpg', '.png']:
                potential = os.path.join(cover_path, f"{title}{ext_img}")
                if os.path.exists(potential):
                    cover_img = potential
                    break

            # Fallback to fuzzy match
            if not cover_img and os.path.exists(cover_path):
                for cover_file in os.listdir(cover_path):
                    if clean_title(os.path.splitext(cover_file)[0]) == cleaned_title:
                        cover_img = os.path.join(cover_path, cover_file)
                        break

            if not cover_img:
                cover_img = os.path.join("assets", "default_cover.png")

            game_list.append({
                "platform": platform,
                "title": title.split("[")[0].strip() if "[" in title else title,
                "rom_path": full_rom_path,
                "cover_path": cover_img
            })

    return game_list
