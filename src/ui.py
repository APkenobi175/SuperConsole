import webbrowser
import os
import json
from functools import partial

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
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
from kivy.clock import Clock

from src.romScanner import scan_roms
from src.gameLauncher import launch_game
from src.Recent import load_recent as load_recent_games, save_recent

RECENT_FILE = "recent.json"
FAVORITES_FILE = "favorites.json"

class GameButton(ButtonBehavior, BoxLayout):
    def __init__(self, game_info, **kwargs):
        super(GameButton, self).__init__(orientation='vertical', size_hint_y=None, height=250, **kwargs)
        self.game_info = game_info

        self.image = KivyImage(source=game_info['cover_path'], allow_stretch=False, keep_ratio=True, size_hint_y=0.85)
        self.label = Label(text=game_info['title'], size_hint_y=0.15, font_size=14, color=(1, 1, 1, 1))

        self.add_widget(self.image)
        self.add_widget(self.label)

    def on_press(self):
        add_to_recent(self.game_info)
        launch_game(self.game_info['platform'], self.game_info['rom_path'])

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
    save_recent(new_entry)

class PlatformScreen(Screen):
    def __init__(self, platform, games, **kwargs):
        super(PlatformScreen, self).__init__(name=platform, **kwargs)

        layout = GridLayout(cols=4, spacing=10, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        for game in games:
            layout.add_widget(GameButton(game))

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

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos) and not self.active:
            self.rect_color.rgba = self.bg_color_hover
        return super().on_touch_move(touch)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.highlight(True)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos) and not self.active:
            self.rect_color.rgba = self.bg_color_default
        return super().on_touch_up(touch)

class SuperConsoleLauncher(App):
    def build(self):
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

        def highlight_tab(tag):
            for k, btn in self.tab_buttons.items():
                btn.highlight(k == tag)
            self.current_tab_index = self.tab_order.index(tag)

        def create_icon_text_button(icon_path, label_text, callback, tag):
            btn = TabButton(icon_path=icon_path, text_label=label_text)
            btn.bind(on_release=callback)
            btn.bind(on_release=lambda inst: highlight_tab(tag))
            self.tab_buttons[tag] = btn
            return btn

        home_btn = create_icon_text_button("assets/home.png", "Home", lambda x: self.switch_platform("Home"), "Home")
        tab_bar.add_widget(home_btn)

        for platform in self.platforms:
            btn = create_icon_text_button(None, platform, lambda x, plat=platform: self.switch_platform(plat), platform)
            tab_bar.add_widget(btn)
            screen = PlatformScreen(platform, self.platforms[platform])
            self.sm.add_widget(screen)

        steam_btn = create_icon_text_button("assets/steam.png", "Steam", lambda x: webbrowser.open("steam://open/bigpicture"), "Steam")
        tab_bar.add_widget(steam_btn)

        root.add_widget(tab_bar)
        root.add_widget(self.sm)

        self.tab_order = list(self.tab_buttons.keys())
        self.current_tab_index = self.tab_order.index("Home")

        Window.bind(on_joy_button_down=self.on_joy_button_down)

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

    def on_joy_button_down(self, window, stickid, button):
        if button == 4:  # LB
            self.current_tab_index = (self.current_tab_index - 1) % len(self.tab_order)
            tag = self.tab_order[self.current_tab_index]
            self.tab_buttons[tag].dispatch('on_release')
        elif button == 5:  # RB
            self.current_tab_index = (self.current_tab_index + 1) % len(self.tab_order)
            tag = self.tab_order[self.current_tab_index]
            self.tab_buttons[tag].dispatch('on_release')
