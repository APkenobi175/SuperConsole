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


def _popen_with_cwd(emulator_path, args):
    emulator_path = os.path.abspath(emulator_path)
    emu_dir = os.path.dirname(emulator_path)
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    return subprocess.Popen(
        [emulator_path] + args,
        cwd=emu_dir,
        creationflags=flags
    )

def _resolve_wiiu_path(p):
    p = os.path.abspath(p)
    if os.path.isdir(p):
        code_dir = os.path.join(p, "code")
        if os.path.isdir(code_dir):
            # pick the first .rpx in code/
            for f in os.listdir(code_dir):
                if f.lower().endswith(".rpx"):
                    return os.path.join(code_dir, f)
    return p


def launch_game(platform, rom_path):
    """
    Launches the appropriate emulator with the given ROM.
    Returns subprocess.Popen so UI can wait() and rebind input.
    """
    emulator_path = EMULATOR_MAP.get(platform)
    if not emulator_path:
        print(f"[ERROR] No emulator configured for platform: {platform}")
        return None
    if not os.path.exists(emulator_path):
        print(f"[ERROR] Emulator not found: {emulator_path}")
        return None

    # >>> CRITICAL LINE: make ROM path absolute <<<
    rom_path = os.path.abspath(rom_path)

    # Optional: sanity check to help debug bad paths
    if not os.path.exists(rom_path):
        print(f"[ERROR] ROM path does not exist: {rom_path}")
        return None

    if platform == "WiiU":
        rom_path = _resolve_wiiu_path(rom_path)
        return _popen_with_cwd(emulator_path, ["-f", "-g", rom_path])

    elif platform == "PS3":
        return _popen_with_cwd(emulator_path, [rom_path])
    elif platform == "Xbox":
        return _popen_with_cwd(emulator_path, ["-dvd_path", rom_path])
    else:
        return _popen_with_cwd(emulator_path, [rom_path])
