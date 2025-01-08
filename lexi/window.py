from gi.repository import Adw, Gtk

from lexi import shared


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "LexiWindow"

    gtc = Gtk.Template.Child
    toast_overlay: Adw.ToastOverlay = gtc()
    navigation_view: Adw.NavigationView = gtc()
    lexicon_page: Adw.NavigationPage = gtc()
    overlay_split_view: Adw.OverlaySplitView = gtc()
    sidebar_page: Adw.NavigationPage = gtc()
    sidebar_scrolled_window: Gtk.ScrolledWindow = gtc()
    collections_listbox: Gtk.ListBox = gtc()
    lexicon_view: Adw.ToolbarView = gtc()
    lexicon_split_view: Adw.NavigationSplitView = gtc()
    lexicon_navigation_page: Adw.NavigationPage = gtc()
    toggle_search_button: Gtk.ToggleButton = gtc()
    search_bar: Gtk.SearchBar = gtc()
    search_entry: Gtk.SearchEntry = gtc()
    lexicon_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicon: Gtk.ListBox = gtc()
    pair_key_entry: Gtk.Entry = gtc()
    pair: Adw.NavigationPage = gtc()
    pair_text_view: Gtk.TextView = gtc()
    attachments_scrolled_window: Gtk.ScrolledWindow = gtc()
    attachments: Gtk.ListBox = gtc()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        if shared.APP_ID.endswith("Devel"):
            self.add_css_class("devel")

        self.search_bar.connect_entry(self.search_entry)

    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggles sidebar of `self`"""
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
