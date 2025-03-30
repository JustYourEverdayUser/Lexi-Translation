# pylint: disable=all
from typing import Any, Optional

from gi.repository import Adw, Gtk

from lexi.ui import widgets

class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__: str

    # UI components
    no_lexicons_yet: Adw.StatusPage
    no_words_yet: Adw.StatusPage
    lexicon_not_selected: Adw.StatusPage

    add_lexicon_popover: Gtk.Popover
    add_lexicon_popover_entry_row: Adw.EntryRow

    lexicons_scrolled_window: Gtk.ScrolledWindow
    lexicons_list_box: Gtk.ListBox
    lexicon_scrolled_window: Gtk.ScrolledWindow
    lexicon_list_box: Gtk.ListBox
    navigation_view: Adw.NavigationView
    overlay_split_view: Adw.OverlaySplitView
    lexcion_split_view: Adw.NavigationSplitView
    search_bar: Gtk.SearchBar
    search_entry: Gtk.SearchEntry

    lexicon_nav_page: Adw.NavigationPage
    word_nav_page: Adw.NavigationPage

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

    ipa_charset_flow_box: Gtk.FlowBox

    # Variables
    loaded_lexicon: Optional[widgets.LexiconRow]
    loaded_word: Optional[widgets.WordRow]
    selected_words: list[widgets.WordRow]

    def __init__(self, **kwargs: Any) -> None: ...
    def on_key_pressed(
        self, _controller: Gtk.EventControllerKey, keyval: int, *_args: Any
    ) -> None: ...
    def on_toggle_sidebar_action(self, *_args: Any) -> None: ...
    def on_toggle_search_action(self, *_args: Any) -> None: ...
    def on_add_lexicon_entry_changed(self, row: Adw.EntryRow) -> None: ...
    def on_add_lexicon_entry_activated(self, row: Adw.EntryRow) -> None: ...
    def build_sidebar(self) -> None: ...
    def on_lexicon_selected(
        self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow
    ) -> None: ...
    def on_word_entry_changed(self, row: Adw.EntryRow) -> None: ...
    def on_pronunciation_entry_changed(self, row: Adw.EntryRow) -> None: ...
    def on_word_list_prop_button_pressed(self, button: Gtk.Button) -> None: ...
    def on_add_word_action(self, *_args: Any) -> None: ...
    def selection_mode_button_toggled(self, button: Gtk.ToggleButton) -> None: ...
    def set_selection_mode(self, enabled: bool) -> None: ...
    def on_delete_selected_words_action(self, *_args: Any) -> None: ...
    def set_word_rows_sensetiveness(self, active: bool) -> None: ...
