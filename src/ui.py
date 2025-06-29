import webbrowser
import os
import json
from functools import partial

'''
KIVY UI IMPORTS IN CASE I WANT TO COME BACK TO IT

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex
from kivy.uix.anchorlayout import AnchorLayout
from kivy.graphics import Color, Rectangle, Line
from kivy.utils import platform
from kivy.core.window import Keyboard

'''
from src.romScanner import scan_roms
from src.gameLauncher import launch_game
from src.Recent import load_recent as load_recent_games, save_recent


RECENT_FILE = "recent.json"
FAVORITES_FILE = "favorites.json"

focused_game_index = 0
focused_game_buttons = []

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r') as f:
            return json.load(f)
    return []

def add_to_recent(game_info):
    recent = load_recent_games()
    new_entry = {
        "title": game_info["title"],
        "platform": game_info["platform"],
        "rom_path": game_info["rom_path"],
        "cover_path": game_info["cover_path"]
    }
    recent = [g for g in recent if g["title"] != new_entry["title"]]
    recent.insert(0, new_entry)
    if len(recent) > 5:
        recent = recent[:5]
    with open(RECENT_FILE, 'w') as f:
        json.dump(recent, f)

'''
class GameButton(ButtonBehavior, BoxLayout):
    def __init__(self, game_info, **kwargs):
        super(GameButton, self).__init__(orientation='vertical', size_hint_y=None, height=250, **kwargs)
        self.game_info = game_info

        self.image = KivyImage(source=game_info['cover_path'], allow_stretch=False, keep_ratio=True, size_hint_y=0.85)
        self.label = Label(text=game_info['title'], size_hint_y=0.15, font_size=14, color=(1, 1, 1, 1))

        self.add_widget(self.image)
        self.add_widget(self.label)

        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 0)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def set_focus(self, focused):
        self.bg_color.rgba = (0.2, 0.6, 1, 0.4) if focused else (1, 1, 1, 0)

    def on_press(self):
        add_to_recent(self.game_info)
        launch_game(self.game_info['platform'], self.game_info['rom_path'])

class TabButton(ButtonBehavior, BoxLayout):
    def __init__(self, icon_path=None, text_label="", **kwargs):
        super(TabButton, self).__init__(orientation='horizontal', spacing=5, padding=[10, 10], size_hint=(None, 1), width=160, **kwargs)
        self.icon_path = icon_path
        self.bg_color_default = get_color_from_hex("#1b2838")
        self.bg_color_active = get_color_from_hex("#2a475e")
        self.bg_color_hover = get_color_from_hex("#2f4f67")
        self.canvas_color = self.bg_color_default
        self.active = False

        with self.canvas.before:
            self.rect_color = Color(*self.canvas_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
            self.border_line = Line(rectangle=(self.x, self.y, self.width, self.height), width=1.2)
            self.bind(size=self._update_rect, pos=self._update_rect)

        if icon_path:
            self.icon = KivyImage(source=icon_path, size_hint=(None, None), size=(24, 24))
            self.add_widget(self.icon)

        self.label = Label(text=text_label, color=(1, 1, 1, 1), bold=True, halign='center', valign='middle')
        self.label.bind(size=self.label.setter('text_size'))
        self.add_widget(self.label)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.border_line.rectangle = (self.x, self.y, self.width, self.height)

    def highlight(self, active):
        self.active = active
        new_color = self.bg_color_active if active else self.bg_color_default
        self.rect_color.rgba = new_color

class PlatformScreen(Screen):
    def __init__(self, platform, games, **kwargs):
        super(PlatformScreen, self).__init__(name=platform, **kwargs)

        layout = GridLayout(cols=4, spacing=10, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        global focused_game_buttons, focused_game_index

        focused_game_buttons = []

        for game in games:
            button = GameButton(game)
            layout.add_widget(button)
            focused_game_buttons.append(button)

        if focused_game_buttons:
            focused_game_index = 0
            focused_game_buttons[focused_game_index].set_focus(True)

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(layout)
        self.add_widget(scroll)

class HomeScreen(Screen):
    def __init__(self, all_games, **kwargs):
        super(HomeScreen, self).__init__(name="Home", **kwargs)
        self.all_games = all_games

        self.layout = BoxLayout(orientation='vertical', spacing=10)
        self.add_widget(self.layout)

        self._build_search_bar()

        scroll_wrapper = ScrollView()
        anchor = AnchorLayout(anchor_y='top')
        self.dynamic_section = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.dynamic_section.bind(minimum_height=self.dynamic_section.setter('height'))
        anchor.add_widget(self.dynamic_section)
        scroll_wrapper.add_widget(anchor)
        self.layout.add_widget(scroll_wrapper)

        self._rebuild_content()

    def _build_search_bar(self):
        search_bar_box = BoxLayout(size_hint_y=None, height=50, padding=[10, 5], spacing=10)
        with search_bar_box.canvas.before:
            Color(*get_color_from_hex("#1b2838"))
            self.rect = Rectangle(size=search_bar_box.size, pos=search_bar_box.pos)
            search_bar_box.bind(size=lambda inst, val: setattr(self.rect, 'size', val))
            search_bar_box.bind(pos=lambda inst, val: setattr(self.rect, 'pos', val))

        search_icon = KivyImage(source="assets/search.png", size_hint=(None, 1), size=(30, 30))
        self.search_input = TextInput(
            hint_text="Search games...",
            size_hint=(1, 1),
            multiline=False,
            background_color=get_color_from_hex("#1b2838"),
            foreground_color=(1, 1, 1, 1)
        )
        self.search_input.bind(text=self.on_search)

        search_bar_box.add_widget(search_icon)
        search_bar_box.add_widget(self.search_input)
        self.layout.add_widget(search_bar_box)

    def _rebuild_content(self):
        self.dynamic_section.clear_widgets()

        fav_label = Label(text="★ Favorites", size_hint_y=None, height=30, color=(1, 1, 1, 1))
        fav_grid = self._create_game_grid(load_favorites())
        self.dynamic_section.add_widget(fav_label)
        self.dynamic_section.add_widget(self._wrap_scroll(fav_grid))

        recent_label = Label(text="🕹 Recently Played", size_hint_y=None, height=30, color=(1, 1, 1, 1))
        recent_grid = self._create_game_grid(load_recent_games())
        self.dynamic_section.add_widget(recent_label)
        self.dynamic_section.add_widget(self._wrap_scroll(recent_grid))

    def on_search(self, instance, value):
        self.dynamic_section.clear_widgets()
        if value.strip() == "":
            self._rebuild_content()
        else:
            filtered = [g for g in self.all_games if value.lower() in g['title'].lower()]
            result_label = Label(text="🔍 Search Results", size_hint_y=None, height=30, color=(1, 1, 1, 1))
            result_grid = self._create_game_grid(filtered)
            self.dynamic_section.add_widget(result_label)
            self.dynamic_section.add_widget(self._wrap_scroll(result_grid))

    def _create_game_grid(self, game_list):
        layout = GridLayout(cols=4, spacing=10, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        for game in game_list:
            layout.add_widget(GameButton(game))
        return layout

    def _wrap_scroll(self, grid):
        scroll = ScrollView(size_hint=(1, None), height=250)
        scroll.add_widget(grid)
        return scroll

class SuperConsoleLauncher(App):
    def on_key_down(self, window, keycode, scancode, codepoint, modifiers):
        global focused_game_index, focused_game_buttons

        key_name = keycode[1] if isinstance(keycode, tuple) else keycode
        print("Key pressed:", key_name)

        if not focused_game_buttons:
            return False

        focused_game_buttons[focused_game_index].set_focus(False)

        if key_name == 'up':
            focused_game_index = max(0, focused_game_index - 4)
        elif key_name == 'down':
            focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 4)
        elif key_name == 'left':
            focused_game_index = max(0, focused_game_index - 1)
        elif key_name == 'right':
            focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 1)
        elif key_name in ('enter', 'numpadenter'):
            focused_game_buttons[focused_game_index].dispatch('on_press')
            return True

        focused_game_buttons[focused_game_index].set_focus(True)
        return True

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_joy_hat=self.on_joy_hat)
        Window.bind(on_joy_axis=self.on_joy_axis)
        screen_width, screen_height = Window.system_size
        Window.size = (screen_width, screen_height)
        Window.borderless = False
        Window.fullscreen = False

        root = BoxLayout(orientation='vertical')
        with root.canvas.before:
            Color(*get_color_from_hex("#1b2838"))
            self.bg_rect = Rectangle(size=root.size, pos=root.pos)
            root.bind(size=lambda instance, value: setattr(self.bg_rect, 'size', value))
            root.bind(pos=lambda instance, value: setattr(self.bg_rect, 'pos', value))

        self.sm = ScreenManager()

        all_games = scan_roms("ROMs/", "Covers/")
        self.platforms = self.group_games_by_platform(all_games)

        self.sm.add_widget(HomeScreen(all_games))

        tab_bar = BoxLayout(size_hint_y=None, height=50, spacing=5, padding=5)
        self.tab_buttons = {}
        self.tab_order = []

        def highlight_tab(tag):
            for k, btn in self.tab_buttons.items():
                if hasattr(btn, 'highlight'):
                    btn.highlight(k == tag)
            self.current_tab_index = self.tab_order.index(tag)

        def create_icon_text_button(icon_path, label_text, callback, tag):
            btn = TabButton(icon_path=icon_path, text_label=label_text)
            btn.bind(on_release=callback)
            btn.bind(on_release=lambda inst: highlight_tab(tag))
            self.tab_buttons[tag] = btn
            self.tab_order.append(tag)
            return btn

        # Add Home button
        home_btn = create_icon_text_button("assets/home.png", "Home", lambda x: self.switch_platform("Home"), "Home")
        tab_bar.add_widget(home_btn)

        # Add platform buttons
        for platform in self.platforms:
            btn = create_icon_text_button(None, platform, lambda x, plat=platform: self.switch_platform(plat), platform)
            tab_bar.add_widget(btn)
            screen = PlatformScreen(platform, self.platforms[platform])
            self.sm.add_widget(screen)

        # Add Steam button
        steam_btn = create_icon_text_button("assets/steam.png", "Steam", lambda x: webbrowser.open("steam://open/bigpicture"), "Steam")
        tab_bar.add_widget(steam_btn)

        root.add_widget(tab_bar)
        root.add_widget(self.sm)

        self.current_tab_index = self.tab_order.index("Home")

        # Bind controller input
        Window.bind(on_joy_button_down=self.on_joy_button_down)

        # Initial highlight
        highlight_tab("Home")

        return root

    def group_games_by_platform(self, games):
        grouped = {}
        for game in games:
            platform = game["platform"]
            if platform not in grouped:
                grouped[platform] = []
            grouped[platform].append(game)
        return grouped

    def switch_platform(self, platform, *args):
        self.sm.current = platform

        # 👉 Refresh focus state if it's a platform screen
        if platform != "Home" and platform in self.platforms:
            screen = self.sm.get_screen(platform)
            global focused_game_buttons, focused_game_index

            focused_game_buttons = []
            focused_game_index = 0

            # Rebuild focus list
            layout = screen.children[0].children[0]  # ScrollView -> GridLayout
            for child in reversed(layout.children):  # reversed = top-to-bottom order
                if isinstance(child, GameButton):
                    focused_game_buttons.append(child)

            if focused_game_buttons:
                focused_game_buttons[focused_game_index].set_focus(True)

    def on_joy_button_down(self, window, stickid, button):
        global focused_game_index, focused_game_buttons
        print("Controller button pressed:", button)

        if button == 4:  # LB
            self.current_tab_index = (self.current_tab_index - 1) % len(self.tab_order)
            tag = self.tab_order[self.current_tab_index]
            self.tab_buttons[tag].dispatch('on_release')
        elif button == 5:  # RB
            self.current_tab_index = (self.current_tab_index + 1) % len(self.tab_order)
            tag = self.tab_order[self.current_tab_index]
            self.tab_buttons[tag].dispatch('on_release')
        elif button == 0:  # A button
            if 0 <= focused_game_index < len(focused_game_buttons):
                focused_game_buttons[focused_game_index].dispatch('on_press')
        elif button == 11:  # D-pad up
            if focused_game_buttons:
                focused_game_buttons[focused_game_index].set_focus(False)
                focused_game_index = max(0, focused_game_index - 4)
                focused_game_buttons[focused_game_index].set_focus(True)
        elif button == 12:  # D-pad down
            if focused_game_buttons:
                focused_game_buttons[focused_game_index].set_focus(False)
                focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 4)
                focused_game_buttons[focused_game_index].set_focus(True)
        elif button == 13:  # D-pad left
            if focused_game_buttons:
                focused_game_buttons[focused_game_index].set_focus(False)
                focused_game_index = max(0, focused_game_index - 1)
                focused_game_buttons[focused_game_index].set_focus(True)
        elif button == 14:  # D-pad right
            if focused_game_buttons:
                focused_game_buttons[focused_game_index].set_focus(False)
                focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 1)
                focused_game_buttons[focused_game_index].set_focus(True)

    def on_joy_hat(self, window, stickid, hatid, value):
        global focused_game_index, focused_game_buttons
        print("D-pad (hat) input:", value)
        x, y = value

        if focused_game_buttons:
            focused_game_buttons[focused_game_index].set_focus(False)

            if y == 1:  # UP
                focused_game_index = max(0, focused_game_index - 4)
            elif y == -1:  # DOWN
                focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 4)
            elif x == -1:  # LEFT
                focused_game_index = max(0, focused_game_index - 1)
            elif x == 1:  # RIGHT
                focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 1)

            focused_game_buttons[focused_game_index].set_focus(True)

    def on_joy_axis(self, window, stickid, axisid, value):
        # Optional: Add cooldown logic to prevent spamming input
        print(f"Analog axis {axisid} value: {value}")
        threshold = 0.6
        global focused_game_index, focused_game_buttons

        if abs(value) < threshold:
            return  # Ignore small movements

        if focused_game_buttons:
            focused_game_buttons[focused_game_index].set_focus(False)

            if axisid == 0:  # Left/Right
                if value > threshold:
                    focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 1)
                elif value < -threshold:
                    focused_game_index = max(0, focused_game_index - 1)
            elif axisid == 1:  # Up/Down
                if value > threshold:
                    focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 4)
                elif value < -threshold:
                    focused_game_index = max(0, focused_game_index - 4)

            focused_game_buttons[focused_game_index].set_focus(True)
            
            
            KIVY UI LOGIC COMMENTED OUT IN CASE I WOULD LIKE TO COME BACK TO IT
            
            
            
            
'''



'''

PySide 6 UI LOGIC

'''