# pylint: disable=all
from typing import Any, Optional

from gi.repository import Adw, Gio, GLib, Gtk

from lexi.ui import widgets

class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__: str

    # Status pages
    no_lexicons_yet: Adw.StatusPage
    no_words_yet: Adw.StatusPage
    lexicon_not_selected: Adw.StatusPage

    # UI components
    toast_overlay: Adw.ToastOverlay

    # Navigation view and pages
    navigation_view: Adw.NavigationView
    lexicon_nav_page: Adw.NavigationPage
    word_nav_page: Adw.NavigationPage

    # Overlay and split views
    overlay_split_view: Adw.OverlaySplitView
    lexicon_split_view: Adw.NavigationSplitView

    # Sidebar components
    lexicons_scrolled_window: Gtk.ScrolledWindow
    lexicons_list_box: Gtk.ListBox
    add_lexicon_alert_dialog: Adw.AlertDialog
    add_lexicon_entry: Gtk.Entry
    search_bar: Gtk.SearchBar
    search_entry: Gtk.SearchEntry

    # Lexicon-related components
    lexicon_scrolled_window: Gtk.ScrolledWindow
    lexicon_list_box: Gtk.ListBox
    lexicon_search_entry: Gtk.Entry

    # Word-related components
    word_entry_row: Adw.EntryRow
    pronunciation_entry_row: Adw.EntryRow
    translations_expander_row: Adw.ExpanderRow
    word_type_expander_row: Adw.ExpanderRow
    examples_expander_row: Adw.ExpanderRow
    references_expander_row: Adw.ExpanderRow
    save_word_button: Gtk.Button
    selection_mode_toggle_button: Gtk.ToggleButton
    delete_selected_words_button: Gtk.Button
    delete_selected_words_button_revealer: Gtk.Revealer
    words_bottom_bar_revealer: Gtk.Revealer

    # References dialog
    references_dialog: Adw.Dialog
    references_dialog_list_box: Gtk.ListBox

    # Word Type filter dialog
    word_types_filter_dialog: Adw.Dialog
    filter_dialog_list_box: Gtk.ListBox
    noun_check_button_filter_dialog: Gtk.CheckButton
    verb_check_button_filter_dialog: Gtk.CheckButton
    adjective_check_button_filter_dialog: Gtk.CheckButton
    adverb_check_button_filter_dialog: Gtk.CheckButton
    pronoun_check_button_filter_dialog: Gtk.CheckButton
    preposition_check_button_filter_dialog: Gtk.CheckButton
    conjunction_check_button_filter_dialog: Gtk.CheckButton
    interjection_check_button_filter_dialog: Gtk.CheckButton
    article_check_button_filter_dialog: Gtk.CheckButton
    idiom_check_button_filter_dialog: Gtk.CheckButton
    clause_check_button_filter_dialog: Gtk.CheckButton
    prefix_check_button_filter_dialog: Gtk.CheckButton
    suffix_check_button_filter_dialog: Gtk.CheckButton

    # Word type check buttons
    noun_check_button: Gtk.CheckButton
    verb_check_button: Gtk.CheckButton
    adjective_check_button: Gtk.CheckButton
    adverb_check_button: Gtk.CheckButton
    pronoun_check_button: Gtk.CheckButton
    preposition_check_button: Gtk.CheckButton
    conjunction_check_button: Gtk.CheckButton
    interjection_check_button: Gtk.CheckButton
    article_check_button: Gtk.CheckButton
    idiom_check_button: Gtk.CheckButton
    clause_check_button: Gtk.CheckButton
    prefix_check_button: Gtk.CheckButton
    suffix_check_button: Gtk.CheckButton

    # Keybindings overlay
    help_overlay: Gtk.ShortcutsWindow

    translations_list_box: Gtk.ListBox
    examples_list_box: Gtk.ListBox
    word_types_list_box: Gtk.ListBox
    references_list_box: Gtk.ListBox

    sort_method: str
    sort_type: str

    # Variables
    loaded_lexicon: Optional[widgets.LexiconRow]
    loaded_word: Optional[widgets.WordRow]
    selected_words: list[widgets.WordRow]

    def __init__(self, **kwargs: Any) -> None: ...
    def on_key_pressed(
        self, _controller: Gtk.EventControllerKey, keyval: int, *_args: Any
    ) -> None: ...
    def on_sorting_method_changed(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None: ...
    def on_sorting_type_changed(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None: ...
    def filter_lexicons(self, row: Gtk.ListBoxRow) -> bool: ...
    def sort_words(self, row1: widgets.WordRow, row2: widgets.WordRow) -> int: ...
    def filter_words(self, row: widgets.WordRow) -> bool: ...
    def on_toggle_sidebar_action(self, *_args: Any) -> None: ...
    def on_toggle_search_action(self, *_args: Any) -> None: ...
    def on_add_lexicon_entry_changed(self, text: Gtk.Text) -> None: ...
    def on_add_lexicon(self, alert_dialog: Adw.AlertDialog, response: str) -> None: ...
    def build_sidebar(self) -> None: ...
    def on_lexicon_selected(
        self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow
    ) -> None: ...
    def update_refs_count(self) -> None: ...
    def on_word_entry_changed(self, row: Adw.EntryRow) -> None: ...
    def on_pronunciation_entry_changed(self, row: Adw.EntryRow) -> None: ...
    def on_word_list_prop_button_pressed(self, button: Gtk.Button) -> None: ...
    def on_references_add_button_pressed(self, *_args: Any) -> None: ...
    def on_add_word_action(self, *_args: Any) -> None: ...
    def selection_mode_button_toggled(self, button: Gtk.ToggleButton) -> None: ...
    def set_selection_mode(self, enabled: bool) -> None: ...
    def on_delete_selected_words_action(self, *_args: Any) -> None: ...
    def set_word_rows_sensetiveness(self, active: bool) -> None: ...
    def on_search_entry_changed(self, *_args: Any) -> None: ...
    def on_word_type_check_button_toggled(self, *_args: Any) -> None: ...
    def on_lexicon_search_entry_changed(self, *_args: Any) -> None: ...
    def on_filter_button_clicked_action(self, *_args: Any) -> None: ...
    def on_filter_check_button_toggled(self, *_args: Any) -> None: ...
    def on_reset_filter_button_clicked(self, *_args: Any) -> None: ...
    def on_show_preferences_action(self, *_args: Any) -> None: ...
    def on_save_word_button_clicked(self, *_args: Any) -> None: ...
    def on_search_action(self, *_args: Any) -> None: ...
    def open_dir(self, _toast: Adw.Toast, path: str) -> None: ...
    def on_word_direction_changed(
        self, text: Gtk.Text, pre_direction: Gtk.TextDirection
    ) -> None: ...
