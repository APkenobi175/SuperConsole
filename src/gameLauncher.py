import os
import subprocess

# Maps each platform to its emulator path
EMULATOR_MAP = {
    "NES": "Emulators/Mesen/Mesen_2.1.0_Windows/Mesen.exe",
    "SNES": "Emulators/Bsnes/bsnes/bsnes.exe",
    "N64": "Emulators/Project64/Release/Project64.exe",
    "GBA": "Emulators/mGBA/mGBA/mGBA.exe",
    "GameCube": "Emulators/Dolphin/Dolphin-x64/Dolphin.exe",
    "Wii": "Emulators/Dolphin/Dolphin-x64/Dolphin.exe",
    "WiiU": "Emulators/Cemu/Cemu/Cemu.exe",
    "PS1": "Emulators/DuckStation/Duckstation/duckstation-qt-x64-ReleaseLTCG.exe",
    "PS2": "Emulators/PCSX2/pcsx2-qt.exe",
    "PS3": "Emulators/RPCS3/rpcs3.exe",
    "Xbox": "Emulators/Xemu/xemu.exe",
    "Xbox360": "Emulators/Xenia/xenia.exe"
}

def launch_game(platform, rom_path):
    """
    Launches the appropriate emulator with the given ROM.
    Some platforms require special arguments.
    """
    emulator_path = EMULATOR_MAP.get(platform)

    if not emulator_path:
        print(f"[ERROR] No emulator configured for platform: {platform}")
        return

    if not os.path.exists(emulator_path):
        print(f"[ERROR] Emulator not found: {emulator_path}")
        return

    # Platform-specific launch handling
    if platform == "WiiU":
        subprocess.Popen([emulator_path, "-g", rom_path])
    elif platform == "PS3":
        subprocess.Popen([emulator_path, rom_path])
    elif platform == "Xbox":
        subprocess.Popen([emulator_path, "-dvd_path", rom_path])
    else:
        subprocess.Popen([emulator_path, rom_path])

