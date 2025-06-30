import webbrowser
import os
import json
from functools import partial


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


from src.romScanner import scan_roms
from src.gameLauncher import launch_game
from src.Recent import load_recent as load_recent_games, save_recent


RECENT_FILE = "recent.json"
FAVORITES_FILE = "favorites.json"

focused_game_index = 0
focused_game_buttons = []
focus_mode = "none"  # can be "tab" or "grid"
focused_tab_index = 0


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


from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout


from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior
import json
import os


class GameButton(ButtonBehavior, FloatLayout):
    def __init__(self, game_info, **kwargs):
        super(GameButton, self).__init__(size_hint=(1, None), height=250, **kwargs)
        self.game_info = game_info
        self.is_favorited = self._is_in_favorites()

        # Fallback cover image if missing
        image_path = game_info.get("cover_path") or "assets/placeholder.png"
        if not os.path.exists(image_path):
            image_path = "assets/placeholder.png"

        # Game cover image
        self.image = KivyImage(
            source=image_path,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 0.85),
            pos_hint={'x': 0, 'top': 1}
        )
        self.add_widget(self.image)

        # Game title label
        self.label = Label(
            text=game_info["title"],
            size_hint=(1, 0.15),
            pos_hint={"x": 0, "y": 0},
            halign="center",
            valign="middle",
            font_size=12,
            color=(1, 1, 1, 1),
            bold=True
        )
        self.label.bind(size=self.label.setter("text_size"))
        self.add_widget(self.label)

        # Favorite star icon (top-right)
        self.star_button = StarButton(
            source="assets/star_filled.png" if self.is_favorited else "assets/star_empty.png",
            size_hint=(None, None),
            size=(32, 32),
            pos_hint={"right": 1, "top": 1}
        )
        self.star_button.bind(on_press=self.toggle_favorite)
        self.add_widget(self.star_button)

        # Focus highlight
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 0)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

    def _is_in_favorites(self):
        favorites = load_favorites()
        return any(f["title"] == self.game_info["title"] for f in favorites)

    def toggle_favorite(self, *args):
        favorites = load_favorites()
        title = self.game_info["title"]

        if self.is_favorited:
            favorites = [f for f in favorites if f["title"] != title]
            self.is_favorited = False
        else:
            favorites.insert(0, self.game_info)
            self.is_favorited = True

        with open(FAVORITES_FILE, "w") as f:
            json.dump(favorites, f)

        self.star_button.source = "assets/star_filled.png" if self.is_favorited else "assets/star_empty.png"
        self.star_button.reload()

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def set_focus(self, focused):
        self.bg_color.rgba = (0.2, 0.6, 1, 0.4) if focused else (1, 1, 1, 0)

    def on_press(self):
        add_to_recent(self.game_info)
        launch_game(self.game_info['platform'], self.game_info['rom_path'])


class StarButton(ButtonBehavior, KivyImage):
    def __init__(self, **kwargs):
        super(StarButton, self).__init__(**kwargs)


class TabButton(ButtonBehavior, BoxLayout):
    def __init__(self, icon_path=None, text_label="", **kwargs):
        super(TabButton, self).__init__(orientation='horizontal', spacing=5, padding=[10, 10], size_hint=(1, 1), width=160, **kwargs)
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
        super().__init__(**kwargs)
        self.name = platform

        layout = BoxLayout(orientation='vertical')

        # Title Label
        title = Label(text=platform, size_hint_y=None, height=50, font_size=24)
        layout.add_widget(title)

        # Scrollable Game Grid
        self.grid = GridLayout(
            cols=5,
            spacing=10,
            padding=10,
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))

        for game in games:
            self.grid.add_widget(GameButton(game))

        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_view.add_widget(self.grid)

        layout.add_widget(scroll_view)
        self.add_widget(layout)


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

        total_height = 0  # Track total height manually

        # --- Favorites Section ---
        favorites = load_favorites()
        if favorites:
            fav_section = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
            fav_label = self._create_section_header("assets/star.png", "Favorites")

            fav_grid = self._create_game_grid(favorites)
            wrapped_fav_scroll = self._wrap_scroll(fav_grid)

            fav_section.add_widget(fav_label)
            fav_section.add_widget(wrapped_fav_scroll)

            fav_section.height = fav_label.height + wrapped_fav_scroll.height + 10
            total_height += fav_section.height
            self.dynamic_section.add_widget(fav_section)

        # --- Recently Played Section ---
        recent_section = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        recent_label = self._create_section_header("assets/joystick.png", "Recently Played")

        recent_grid = GridLayout(cols=5, spacing=10, padding=10, size_hint_y=None, height=250)
        for game in load_recent_games()[:5]:
            recent_grid.add_widget(GameButton(game))

        recent_section.add_widget(recent_label)
        recent_section.add_widget(recent_grid)
        recent_section.height = recent_label.height + recent_grid.height + 10
        total_height += recent_section.height
        self.dynamic_section.add_widget(recent_section)

        # --- Steam and Xbox Buttons ---
        button_bar = BoxLayout(size_hint=(None, None), height=170, spacing=40, padding=[10, 10])
        button_bar.size_hint_x = None
        button_bar.width = 360  # 2 x 150 width + spacing

        steam_btn = IconButton("assets/steam.png", "Steam")
        steam_btn.on_press = lambda: webbrowser.open("steam://open/bigpicture")

        xbox_btn = IconButton("assets/xbox.png", "Xbox")
        xbox_btn.on_press = lambda: os.system("start xbox:" if platform == "win" else "")

        button_bar.add_widget(steam_btn)
        button_bar.add_widget(xbox_btn)

        centered_buttons = AnchorLayout(anchor_x='center', anchor_y='top', size_hint_y=None, height=button_bar.height)
        centered_buttons.add_widget(button_bar)
        total_height += centered_buttons.height
        self.dynamic_section.add_widget(centered_buttons)

        # --- Final Height ---
        self.dynamic_section.height = total_height + 80

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
        layout = GridLayout(
            cols=5,
            spacing=20,
            padding=[40, 10],
            size_hint=(1, None)
        )

        row_count = (len(game_list) + 4) // 5  # 4 columns
        layout.height = row_count * 250 + (row_count - 1) * 20 + 20  # Adjust height based on rows

        for game in game_list:
            layout.add_widget(GameButton(game))

        return layout

    def _wrap_scroll(self, grid):
        scroll = ScrollView(size_hint=(1, None), height=250)
        scroll.add_widget(grid)
        return scroll

    def _create_section_header(self, icon_path, label_text):
        header_box = BoxLayout(
            orientation="horizontal",
            spacing=5,
            size_hint_y=None,
            height=30,
            size_hint_x=None,
            width=200,
            pos_hint={"center_x": 0.5}  # Center the whole section header
        )

        icon = KivyImage(source=icon_path, size_hint=(None, None), size=(24, 24))
        label = Label(
            text=label_text,
            color=(1, 1, 1, 1),
            size_hint=(None, 1),
            width=160,
            halign="left",
            valign="middle",
            font_size = 19,
            bold = True
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        header_box.add_widget(icon)
        header_box.add_widget(label)
        return header_box


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
        self.scroll_to_focused_game()

        return True

    def update_hud_context(self, context):
        if not hasattr(self, "hud"):
            return

        if context == "tab":
            self.hud.set_actions(a_text="Select")
        elif context == "grid":
            self.hud.set_actions(a_text="Play", y_text="Toggle Favorite")
        elif context == "search_bar":
            self.hud.set_actions(a_text="Search")
        elif context in ["favorites", "recently_played"]:
            self.hud.set_actions(a_text="Play", y_text="Toggle Favorite")

    def scroll_to_focused_game(self):
        current_screen = self.sm.get_screen(self.sm.current)
        if hasattr(current_screen, 'children') and current_screen.children:
            boxlayout = current_screen.children[0]  # Vertical layout
            if boxlayout.children:
                scroll = boxlayout.children[0]  # ScrollView
                if hasattr(scroll, 'children') and scroll.children:
                    grid = scroll.children[0]  # GridLayout inside ScrollView
                    if 0 <= focused_game_index < len(focused_game_buttons):
                        target = focused_game_buttons[focused_game_index]
                        scroll.scroll_to(target)

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

        # Tab bar with LB and RB icons
        self.tab_bar = BoxLayout(size_hint=(1, None), height=50, spacing=5, padding=[10, 0])

        self.tab_buttons = {}
        self.tab_order = []
        global focused_tab_index
        focused_tab_index = 0

        # Add LB icon to tab bar (left side)
        lb_icon = KivyImage(source="assets/button_lb.png", size_hint=(None, 1), width=50)
        self.tab_bar.add_widget(lb_icon)

        def highlight_tab(tag):
            global focused_tab_index
            for i, k in enumerate(self.tab_order):
                btn = self.tab_buttons[k]
                btn.highlight(k == tag)
                if k == tag:
                    focused_tab_index = i

        def create_icon_text_button(icon_path, label_text, callback, tag):
            btn = TabButton(icon_path=icon_path, text_label=label_text)
            btn.bind(on_release=callback)
            btn.bind(on_release=lambda inst: highlight_tab(tag))
            self.tab_buttons[tag] = btn
            self.tab_order.append(tag)
            return btn

        # Add Home button
        home_btn = create_icon_text_button("assets/home.png", "Home", lambda x: self.switch_platform("Home"), "Home")
        self.tab_bar.add_widget(home_btn)

        # Add platform buttons
        for platform in self.platforms:
            btn = create_icon_text_button(None, platform, lambda x, plat=platform: self.switch_platform(plat), platform)
            self.tab_bar.add_widget(btn)
            screen = PlatformScreen(platform, self.platforms[platform])
            self.sm.add_widget(screen)

        # Add RB icon to tab bar (right side)
        rb_icon = KivyImage(source="assets/button_rb.png", size_hint=(None, 1), width=50)
        self.tab_bar.add_widget(rb_icon)

        root.add_widget(self.tab_bar)
        root.add_widget(self.sm)

        self.current_tab_index = self.tab_order.index("Home")

        self.tab_buttons[self.tab_order[focused_tab_index]].highlight(True)

        # Bind controller input
        Window.bind(on_joy_button_down=self.on_joy_button_down)

        # Initial highlight
        highlight_tab("Home")

        global focus_mode
        focus_mode = "tab"
        self.hud = HUD()
        hud_anchor = AnchorLayout(anchor_x='right', anchor_y='bottom', size_hint=(1, None), height=120)
        hud_anchor.add_widget(self.hud)
        root.add_widget(hud_anchor)

        self.update_hud_context("tab")

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

        if platform != "Home" and platform in self.platforms:
            screen = self.sm.get_screen(platform)
            global focused_game_buttons, focused_game_index

            layout = screen.children[0].children[0]  # ScrollView -> GridLayout

            # 🔥 Clear all visual highlights before resetting list
            for child in layout.children:
                if isinstance(child, GameButton):
                    child.set_focus(False)

            # ✅ FIX: Rebuild list of GameButtons (reversed because Kivy adds children in reverse)
            focused_game_buttons = [
                child for child in reversed(layout.children)
                if isinstance(child, GameButton)
            ]
            focused_game_index = 0

            # ✅ Apply initial focus (if there are games)
            if focused_game_buttons:
                focused_game_buttons[focused_game_index].set_focus(True)

            # ✅ Set mode to grid so input works
            global focus_mode
            focus_mode = "grid"
            self.update_hud_context("grid")

    def on_joy_button_down(self, window, stickid, button):
        global focused_game_index, focused_game_buttons
        print("Controller button pressed:", button)

        if button == 4:  # LB
            self.hud.pulse_button(self.tab_bar.children[0])
            self.current_tab_index = (self.current_tab_index - 1) % len(self.tab_order)
            tag = self.tab_order[self.current_tab_index]
            self.tab_buttons[tag].dispatch('on_release')

        elif button == 5:  # RB
            self.hud.pulse_button(self.tab_bar.children[-1])
            self.current_tab_index = (self.current_tab_index + 1) % len(self.tab_order)
            tag = self.tab_order[self.current_tab_index]
            self.tab_buttons[tag].dispatch('on_release')
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

        elif button == 0:
            self.hud.pulse_button(self.hud.a_label)# A button
            if focus_mode == "grid" and 0 <= focused_game_index < len(focused_game_buttons):
                self.update_hud_context("grid")  # ✅ ADD
                focused_game_buttons[focused_game_index].dispatch('on_press')
            elif focus_mode == "tab":
                self.update_hud_context("tab")  # ✅ ADD
                tag = self.tab_order[focused_tab_index]
                self.tab_buttons[tag].dispatch('on_release')
        elif button == 1:  # B button
            self.hud.pulse_button(self.hud.b_label)
        elif button == 2:  # X button
            self.hud.pulse_button(self.hud.x_label)
        elif button == 3:  # Y button
            self.hud.pulse_button(self.hud.y_label)
            if focus_mode == "grid" and 0 <= focused_game_index < len(focused_game_buttons):
                self.update_hud_context("grid")  # ✅ ADD
                focused_game_buttons[focused_game_index].star_button.dispatch('on_press')

    def on_joy_hat(self, window, stickid, hatid, value):
        global focused_game_index, focused_game_buttons, focus_mode, focused_tab_index
        print("D-pad event triggered. Focus mode:", focus_mode)
        print("D-pad (hat) input:", value)
        x, y = value

        if focus_mode == "tab":
            if x == 1:
                focused_tab_index = (focused_tab_index + 1) % len(self.tab_order)
            elif x == -1:
                focused_tab_index = (focused_tab_index - 1) % len(self.tab_order)

            for i, k in enumerate(self.tab_order):
                self.tab_buttons[k].highlight(i == focused_tab_index)
            self.current_tab_index = focused_tab_index

            if y == -1:  # ↓ into grid
                screen = self.sm.get_screen(self.sm.current)
                if hasattr(screen, 'children') and screen.children:
                    boxlayout = screen.children[0]  # This is the vertical layout
                    scroll = boxlayout.children[0]  # This is the ScrollView
                    if hasattr(scroll, 'children') and scroll.children:
                        grid = scroll.children[0]  # This is the GridLayout with GameButtons
                        focused_game_buttons = [
                            child for child in reversed(grid.children)
                            if isinstance(child, GameButton)
                        ]
                        focused_game_index = 0
                        focus_mode = "grid"
                        if focused_game_buttons:
                            focused_game_buttons[focused_game_index].set_focus(True)
                            self.update_hud_context("grid")
                        return


        elif focus_mode == "grid":
            self.update_hud_context("grid")
            if focused_game_buttons:
                focused_game_buttons[focused_game_index].set_focus(False)

            if y == 1:  # ↑ key
                if focused_game_index < 5:
                    # Top row → go to tab bar
                    focus_mode = "tab"
                    self.update_hud_context("tab")
                    for i, k in enumerate(self.tab_order):
                        self.tab_buttons[k].highlight(i == focused_tab_index)
                    return
                else:
                    focused_game_index = max(0, focused_game_index - 5)
            elif y == -1:
                focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 5)
            elif x == -1:
                focused_game_index = max(0, focused_game_index - 1)
            elif x == 1:
                focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 1)

            if focused_game_buttons:
                focused_game_buttons[focused_game_index].set_focus(True)
                self.scroll_to_focused_game()

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
                    focused_game_index = min(len(focused_game_buttons) - 1, focused_game_index + 5)
                elif value < -threshold:
                    focused_game_index = max(0, focused_game_index - 5)

            focused_game_buttons[focused_game_index].set_focus(True)
            self.scroll_to_focused_game()


class IconButton(ButtonBehavior, BoxLayout):
    def __init__(self, image_path, label_text, **kwargs):
        super(IconButton, self).__init__(orientation='vertical', size_hint=(None, None), size=(150, 150), **kwargs)
        self.padding = 10
        self.spacing = 5

        self.image = KivyImage(source=image_path, size_hint=(1, 0.8))
        self.label = Label(text=label_text, font_size=14, color=(1, 1, 1, 1), size_hint=(1, 0.2))

        self.add_widget(self.image)
        self.add_widget(self.label)

        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 0)  # No highlight initially
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def set_focus(self, focused):
        self.bg_color.rgba = (0.2, 0.6, 1, 0.4) if focused else (1, 1, 1, 0)

            

class HUD(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(size_hint=(None, None), size=(200, 200), **kwargs)
        self.pos_hint = {"right": 1, "bottom": 1}

        self.a_label = self._create_button("assets/button_a.png")
        self.b_label = self._create_button("assets/button_b.png")
        self.x_label = self._create_button("assets/button_x.png")
        self.y_label = self._create_button("assets/button_y.png")

        # Position buttons in diamond shape (tighter)
        self.y_label.pos_hint = {"center_x": 0.5, "top": 1}             # Y
        self.a_label.pos_hint = {"center_x": 0.5, "y": 0}               # A
        self.x_label.pos_hint = {"x": 0, "center_y": 0.5}               # X
        self.b_label.pos_hint = {"right": 1, "center_y": 0.5}           # B

        self.add_widget(self.y_label)
        self.add_widget(self.a_label)
        self.add_widget(self.x_label)
        self.add_widget(self.b_label)



    def pulse_button(self, button):
        from kivy.animation import Animation
        anim = Animation(size=(70, 70), duration=0.1) + Animation(size=(60, 60), duration=0.1)
        anim.start(button)

    def _create_button(self, icon_path):
        from kivy.uix.relativelayout import RelativeLayout

        container = RelativeLayout(size_hint=(None, None), size=(60, 70))

        icon = KivyImage(source=icon_path, size_hint=(None, None), size=(32, 32), pos_hint={"center_x": 0.5, "top": 1})

        label = Label(
            text="",
            font_size=11,
            color=(1, 1, 1, 1),
            halign='center',
            valign='top',
            size_hint=(None, None),
            size=(80, 30),
            pos_hint={"center_x": 0.5, "y": 0}
        )
        label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        container.icon = icon
        container.label = label
        container.add_widget(icon)
        container.add_widget(label)

        return container

    def set_actions(self, a_text=None, b_text=None, x_text=None, y_text=None):
        self.a_label.label.text = a_text or ""
        self.b_label.label.text = b_text or ""
        self.x_label.label.text = x_text or ""
        self.y_label.label.text = y_text or ""

    def _update_text_size(self, instance, size):
        instance.text_size = (instance.width, None)


'''

PySide 6 UI LOGIC

'''