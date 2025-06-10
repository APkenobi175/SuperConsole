import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from src.romScanner import scan_roms
from src.gameLauncher import launch_game
from src.utils import load_image


def run_launcher_ui():
    # Step 1: Initialize main window
    root = tk.Tk()
    root.title("Super Console Launcher")
    root.geometry("1280x720")

    # Step 2: Scan ROMs
    games = scan_roms("ROMs/", "Covers/")

    # Step 3: Group games by platform
    platform_tabs = _group_games_by_platform(games)

    # Step 4: Create tabbed interface
    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both')

    for platform, game_list in platform_tabs.items():
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=platform)

        row, col = 0, 0
        for game in game_list:
            button = _create_game_button(tab, game)
            button.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col >= 5:
                col = 0
                row += 1

    # Step 5: Run main event loop
    root.mainloop()


def _group_games_by_platform(games):
    grouped = {}
    for game in games:
        platform = game["platform"]
        if platform not in grouped:
            grouped[platform] = []
        grouped[platform].append(game)
    return grouped


def _create_game_button(parent, game):
    image = load_image(game["cover_path"], size=(150, 200))
    button = tk.Button(
        parent,
        image=image,
        text=game["title"],
        compound="top",
        command=lambda: launch_game(game["platform"], game["rom_path"])
    )
    button.image = image  # prevent garbage collection
    return button