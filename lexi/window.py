from gi.repository import Adw, Gtk

from lexi import shared
from lexi.ui.LexiconRow import LexiconRow


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "LexiWindow"

    gtc = Gtk.Template.Child

    # Status pages
    no_lexicons_yet: Adw.StatusPage = gtc()

    # Main window
    toast_overlay: Adw.ToastOverlay = gtc()
    navigation_view: Adw.NavigationView = gtc()
    main_navigation_page: Adw.NavigationPage = gtc()
    overlay_split_view: Adw.OverlaySplitView = gtc()
    lexicon_split_view: Adw.NavigationSplitView = gtc()

    # Lexicons sidebar
    sidebar_page: Adw.NavigationPage = gtc()
    lexicons_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicons_listbox: Gtk.ListBox = gtc()

    # Lexicon sidebar
    lexicon_navigation_page: Adw.NavigationPage = gtc()
    toggle_search_button: Gtk.ToggleButton = gtc()
    search_bar: Gtk.SearchBar = gtc()
    search_entry: Gtk.SearchEntry = gtc()
    lexicon_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicon: Gtk.ListBox = gtc()
    pair_key_entry: Gtk.Entry = gtc()

    # Pair page
    pair: Adw.NavigationPage = gtc()
    pair_text_view: Gtk.TextView = gtc()
    attachments_scrolled_window: Gtk.ScrolledWindow = gtc()
    attachments: Gtk.ListBox = gtc()

    # Popovers
    add_lexicon_popover: Gtk.Popover = gtc()
    name_lexicon_entry: Adw.EntryRow = gtc()
    add_lexicon_popover_2: Gtk.Popover = gtc()
    name_lexicon_entry_2: Adw.EntryRow = gtc()

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        if shared.APP_ID.endswith("Devel"):
            self.add_css_class("devel")

        self.search_bar.connect_entry(self.search_entry)
        self.name_lexicon_entry.connect(
            "apply", lambda entry_row: shared.app.add_lexicon(entry_row.get_text())
        )
        self.name_lexicon_entry_2.connect(
            "apply", lambda entry_row: shared.app.add_lexicon(entry_row.get_text())
        )

        self.build_sidebar()

    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggles sidebar of `self`"""
        self.overlay_split_view.set_show_sidebar(
            not self.overlay_split_view.get_show_sidebar()
        )

    def on_toggle_search_action(self, *_args) -> None:
        """Toggles search field of `self`"""
        if self.navigation_view.get_visible_page() == self.main_navigation_page:
            search_bar = self.search_bar
            search_entry = self.search_entry
        else:
            return

        search_bar.set_search_mode(not (search_mode := search_bar.get_search_mode()))

        if not search_mode:
            self.set_focus(search_entry)

        search_entry.set_text("")

    def build_sidebar(self) -> None:
        """Rebuilds lexicons sidebar content"""
        self.lexicons_listbox.remove_all()
        if len(shared.data["lexicons"]) > 0:
            lexicons = []
            for lexicon in shared.data["lexicons"]:
                lexicons.append(lexicon)
            lexicons = sorted(lexicons, key=lambda x: x["name"].lower())
            for lexicon in lexicons:
                self.lexicons_listbox.append(
                    LexiconRow(label=lexicon["name"], identificator=lexicon["id"])
                )
            self.lexicons_scrolled_window.set_child(self.lexicons_listbox)
        else:
            self.lexicons_scrolled_window.set_child(self.no_lexicons_yet)

    def on_open_lexicon_actions_menu_action(self, *_args) -> None:
        """Presents lexicon action menu on F10 press"""
        for row in self.lexicons_listbox:  # pylint: disable=not-an-iterable
            if row.has_focus():
                row.get_child().open_menu()
