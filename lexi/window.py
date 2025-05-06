import os
import random
import string

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from lexi import enums, shared
from lexi.logging.logger import logger
from lexi.ui.LexiconRow import LexiconRow
from lexi.ui.Preferences import LexiPreferences
from lexi.utils.backend import Lexicon


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "LexiWindow"

    gtc = Gtk.Template.Child

    # Status pages
    no_lexicons_yet: Adw.StatusPage = gtc()
    no_words_yet: Adw.StatusPage = gtc()
    lexicon_not_selected: Adw.StatusPage = gtc()

    # Toast overlay
    toast_overlay: Adw.ToastOverlay = gtc()

    # Navigation view and pages
    navigation_view: Adw.NavigationView = gtc()
    lexicon_nav_page: Adw.NavigationPage = gtc()
    word_nav_page: Adw.NavigationPage = gtc()

    # Overlay and split views
    overlay_split_view: Adw.OverlaySplitView = gtc()
    lexicon_split_view: Adw.NavigationSplitView = gtc()

    # Sidebar components
    lexicons_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicons_list_box: Gtk.ListBox = gtc()
    add_lexicon_alert_dialog: Adw.AlertDialog = gtc()
    add_lexicon_entry: Gtk.Entry = gtc()
    search_bar: Gtk.SearchBar = gtc()
    search_entry: Gtk.SearchEntry = gtc()

    # Lexicon-related components
    lexicon_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicon_list_box: Gtk.ListBox = gtc()
    lexicon_search_entry: Gtk.Entry = gtc()

    # Word-related components
    word_entry_row: Adw.EntryRow = gtc()
    pronunciation_entry_row: Adw.EntryRow = gtc()
    translations_expander_row: Adw.ExpanderRow = gtc()
    word_type_expander_row: Adw.ExpanderRow = gtc()
    examples_expander_row: Adw.ExpanderRow = gtc()
    references_expander_row: Adw.ExpanderRow = gtc()
    save_word_button: Gtk.Button = gtc()
    selection_mode_toggle_button: Gtk.ToggleButton = gtc()
    delete_selected_words_button: Gtk.Button = gtc()
    delete_selected_words_button_revealer: Gtk.Revealer = gtc()
    words_bottom_bar_revealer: Gtk.Revealer = gtc()
    assign_word_type_dialog: Adw.Dialog = gtc()
    assign_word_type_dialog_list_box: Gtk.ListBox = gtc()
    filter_dialog: Adw.Dialog = gtc()
    filter_dialog_list_box: Gtk.ListBox = gtc()

    # References dialog
    references_dialog: Adw.Dialog = gtc()
    references_dialog_list_box: Gtk.ListBox = gtc()

    # IPA charset flow box
    # ipa_charset_flow_box: Gtk.FlowBox = gtc()

    # Keybindings overlay
    help_overlay: Gtk.ShortcutsWindow = gtc()

    translations_list_box: Gtk.ListBox
    examples_list_box: Gtk.ListBox
    word_types_list_box: Gtk.ListBox
    references_list_box: Gtk.ListBox

    sort_method: str = shared.state_schema.get_string("sort-method")
    sort_type: str = shared.state_schema.get_string("sort-type")

    # Variables to store the currently loaded lexicon and word
    loaded_lexicon: LexiconRow = None
    # loaded_word: WordRow = None
    selected_words: list = []

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Add a CSS class for development mode
        if shared.APP_ID.endswith("Devel"):
            logger.debug("Enabling development mode decorations")
            self.add_css_class("devel")

        logger.debug("Setting keybinding window")
        self.set_help_overlay(self.help_overlay)

        if enums.Schema.WORD_AUTOSAVE():
            self.save_word_button.remove_css_class("suggested-action")
            self.save_word_button.set_tooltip_text(_("Word autosave is enabled"))
            self.save_word_button.set_sensitive(False)
        else:
            self.save_word_button.add_css_class("suggested-action")
            self.save_word_button.set_sensitive(True)

        if self.lexicon_list_box.get_selected_row() is None:
            self.lexicon_scrolled_window.set_child(self.lexicon_not_selected)

        key_kapture_controller = Gtk.EventControllerKey()
        self.add_controller(key_kapture_controller)

        # Connections
        # self.lexicons_list_box.set_filter_func(self.filter_lexicons)
        # self.lexicon_list_box.set_sort_func(self.sort_words)
        # self.lexicon_list_box.set_filter_func(self.filter_words)
        self.search_bar.connect_entry(self.search_entry)
        # key_kapture_controller.connect("key-pressed", self.on_key_pressed)

        # Extracts ListBoxes from expander rows
        for epxander_row in (
            (self.translations_expander_row, "translations"),
            (self.examples_expander_row, "examples"),
            (self.word_type_expander_row, "word_types"),
            (self.references_expander_row, "references"),
        ):
            for item in epxander_row[0].get_child():
                for _item in item:
                    if isinstance(_item, Gtk.ListBox):
                        setattr(self, epxander_row[1] + "_list_box", _item)
                        break

        self.build_sidebar()

    def build_sidebar(self) -> None:
        """Builds the sidebar with lexicons"""
        self.lexicons_list_box.remove_all()
        # pylint: disable=protected-access
        if len(shared.lexictrl) != 0:
            for lexicon in sorted(shared.lexictrl, key=lambda x: x.name):
                lexicon_row = LexiconRow(lexicon=lexicon)
                self.lexicons_list_box.append(lexicon_row)
            self.lexicons_scrolled_window.set_child(self.lexicons_list_box)
        else:
            self.lexicons_scrolled_window.set_child(self.no_lexicons_yet)
