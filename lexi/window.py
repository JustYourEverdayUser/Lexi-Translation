from gi.repository import Adw, Gtk

from lexi import shared


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "LexiWindow"

    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    navigation_view: Adw.NavigationView = Gtk.Template.Child()
    lexicon_page: Adw.NavigationPage = Gtk.Template.Child()
    overlay_split_view: Adw.OverlaySplitView = Gtk.Template.Child()
    sidebar_page: Adw.NavigationPage = Gtk.Template.Child()
    sidebar_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    collections_listbox: Gtk.ListBox = Gtk.Template.Child()
    show_sidebar_button: Gtk.Button = Gtk.Template.Child()
    left_buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    add_pair: Gtk.Button = Gtk.Template.Child()
    toggle_search_button: Gtk.ToggleButton = Gtk.Template.Child()
    right_buttons_revealer: Gtk.Revealer = Gtk.Template.Child()
    sorting_button: Gtk.MenuButton = Gtk.Template.Child()
    search_bar: Gtk.SearchBar = Gtk.Template.Child()
    search_entry: Gtk.SearchEntry = Gtk.Template.Child()
    lexicon_scrolled_window: Gtk.ScrolledWindow = Gtk.Template.Child()
    lexicon: Gtk.FlowBox = Gtk.Template.Child()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.search_bar.connect_entry(self.search_entry)

    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggles sidebar of `self`"""
        if self.navigation_view.get_visible_page() is self.lexicon_page:
            self.overlay_split_view.set_show_sidebar(
                not self.overlay_split_view.get_show_sidebar()
            )

    def on_toggle_search_action(self, *_args) -> None:
        """Toggles search field of `self`"""
        if self.navigation_view.get_visible_page() == self.lexicon_page:
            search_bar = self.search_bar
            search_entry = self.search_entry
        else:
            return

        search_bar.set_search_mode(not (search_mode := search_bar.get_search_mode()))

        if not search_mode:
            self.set_focus(search_entry)

        search_entry.set_text("")
