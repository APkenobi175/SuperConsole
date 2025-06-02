from urllib.request import proxy_bypass_macosx_sysconf

# Super Console Launcher - SDP

## Project Overview

Description: Create a portable cross-PC emulation launcher with a GUI created with TKinter

It will be easy to use, the only thing the user will have to do is place roms in the appropriate folder. 

The Program will have all the emulators installed already so the user will not need to install any emulators. 

## Features:
* Autodetects which emulator to open
* List of games organized by console
* Games will have Title and also cover image displayed
* There will be tabs that will allow you to switch between which console you want to use
* Includes steam games/shortcut to controller steam layout
* Portable structure, (run the EXE and or copy all files from flashdrive and have everything you need)
* Lightweight easy to use UI, just all games listed.

## File Structure
```
SuperConsole/
├── launcher.py
├── src/ [All Scripts here]
├── Emulators/
│   └── [All emulators pre-installed here]
├── ROMs/
│   └── [Console folders: NES, SNES, PS2, etc.]
├── Covers/
│   └── [Box art images, matched by filename]
├── assets/
│   └── [Default icon if no icon]
├── README.md
└── .gitignore
```
# Python Modules Overview:

## launcher.py
### Description: Main Entry point, runs the application
**Steps:**
1. Import the UI entry function from ui.py
2. Set up the main block ```if __name__ == "__main__"```
psuedocode:
```python
# import the UI function
import launch_UI

# Run the application
if __name__ == "__main__":
    RunLauncher()

```


## __init__.py
### Description: Make this a proper python package

## ui.py
### Description: Builds the Tkinter GUI, Tabs, buttons, grid layout, and images
**Steps:**
1. import Scan_Roms() from romScanner.py, and import load_image() from utils.py to load cover image
2. Create the TKinter window, set the title, window size, and icon!
3. Scan for the games, pass in the roms and covers folders, get back a list of game dictionaries
4. Create a dictionary that groups games by platform
5. initialize TKinters "Notebook" widget to create a tabbed interface
6. Run the main loop

#### Functions created:

**launcher_ui()** (Called in launcher.py)

Will set up the window, GUI and load game data

pseudocode:
```python



def launcerh_ui:
    1. initialize main window
    2. call scan_roms function, return list of game dictionaries
    3. calll group_games(gamelist) helper function, returns dict with {platform: [games]}
    4. Create ttk.notebook for the tabs
    5. for each platform create a new ttk.freame and add tab to notebook
    


```





## romScanner.py
### Description: Scans the ROMS folder and returns the game lists and covers to go with it

## gameLauncher.py
### Description: Launches the correct emulator and the correct ROM

## config.py
### Description: May use for a future update if user wants to change settings, reads config.json (Not implementing now)

## utils.py
### Description: This is where all the utilities and reusable functions will be



# Super Console - Phases of design:

##  Phase 1: Setup & Structure
- [x] Set up file/folder structure
- [x] Create `.gitignore`, `README.md`, and initialize Git repo
- [x] Create empty Python files: `launcher.py`, and all files in `src/`
- [x] Set up dummy `ROMs/`, `Covers/`, `Emulators/`, and `assets/` folders with sample files

---

##  Phase 2: UI Framework (Tkinter Base)
- [ ] In `ui.py`, create main window and use `ttk.Notebook` for tabbed layout  
- [ ] Dynamically generate one tab per ROM subfolder (platform)
- [ ] Add placeholder buttons for games (use default cover art for now)
- [ ] Wire up `launcher.py` to call `run_launcher_ui()` from `src.ui`

---

##  Phase 3: ROM + Cover Scanning
- [ ] In `romScanner.py`, build a function to:
  - [ ] Scan each folder in `ROMs/`
  - [ ] Return a list of ROM files
  - [ ] Check `Covers/PlatformName/` for matching `.jpg` or `.png`
- [ ] Format this data into a list of dicts like:
```python
{
  "platform": "Wii",
  "title": "MarioKart",
  "rom_path": "ROMs/Wii/MarioKart.iso",
  "cover_path": "Covers/Wii/MarioKart.jpg"
}
```
--- 

##  Phase 4: Display Games in UI
- [ ] In `ui.py`, build per-tab game grids:
  - [ ] Display cover image and title
  - [ ] Make them clickable (use `lambda` or `functools.partial`)
- [ ] Load images using `PIL.Image` and `ImageTk.PhotoImage`
- [ ] Fallback to default cover image if missing

---

##  Phase 5: Launch Games
- [ ] In `gameLauncher.py`, map each platform to its emulator path
- [ ] Handle unique launch styles:
  - [ ] Cemu → `-g` argument
  - [ ] RPCS3 → folder path instead of file
- [ ] In `ui.py`, connect button click to `launch_game(platform, rom_path)`

---

##  Phase 6: Portability & Path Handling
- [ ] Use `os.path.abspath(__file__)` to get base path
- [ ] Normalize all paths to work from any drive letter or system
- [ ] Make sure everything runs when copied to USB

---

##  Phase 7: Polish & Extras
- [ ] Add Steam shortcut support (optional phase)
- [ ] Add error handling/logging in `utils.py`
- [ ] Add scrollbar or pagination for long game lists
- [ ] Add config system (`config.py` + `config.json`) for user overrides
- [ ] Add favorites, search bar, or recent games tracking (stretch goals)


##  Phase 8: TESTING
- [ ] Test 
---

##  Phase 9: Publish
- [ ] Use PyInstaller to create `.exe`
- [ ] Test on different PCs and drive letters
- [ ] Add usage instructions to `README.md`