# pylint: disable=all
from typing import Any, Dict

from gi.repository import Adw, Gtk

class LexiconRow(Gtk.Box):
    """Lexicon row widget

    Parameters
    ----------
    file : str
        The file to load the lexicon from.
    """

    __gtype_name__: str
    add_word_dialog: Adw.Dialog
    word_entry_row: Adw.EntryRow
    translation_entry_row: Adw.EntryRow
    example_entry_row: Adw.EntryRow
    actions_popover: Gtk.PopoverMenu
    rename_alert_dialog: Adw.AlertDialog
    rename_entry: Gtk.Entry
    deletion_alert_dialog: Adw.AlertDialog
    title: Gtk.Label

    def __init__(self, file: str) -> None: ...
    def save_lexicon(self) -> None: ...
    def delete_lexicon(self, _alert_dialog: Adw.AlertDialog, response: str) -> None: ...
    def rename_lexicon(self, *_args: Any) -> None: ...
    def on_rename_entry_changed(self, text: Gtk.Text) -> None: ...
    def do_rename(self, alert_dialog: Adw.AlertDialog, response: str) -> None: ...
    def show_add_word_dialog(self) -> None: ...
    def add_word(self, *_args: Any) -> None: ...
    def check_if_word_is_empty(self, row: Adw.EntryRow) -> None: ...
    def on_add_word_dialog_enter_press(self, *_args: Any) -> None: ...
    @property
    def name(self) -> str: ...
    @name.setter
    def name(self, name: str) -> None: ...

class WordRow(Adw.ActionRow):
    """Word row widget

    Parameters
    ----------
    word : dict
        A dictionary with the word [id, word, pronunciation, translations, types, examples, references].
    lexicon : LexiconRow
        The parent lexicon row.
    """

    __gtype_name__: str
    check_button: Gtk.CheckButton
    check_button_revealer: Gtk.Revealer
    refs_count_label_box: Gtk.Box
    refs_count_label: Gtk.Label
    lexicon: LexiconRow
    word_dict: Dict[str, Any]

    def __init__(self, word: Dict[str, Any], lexicon: LexiconRow) -> None: ...
    def load_word(self, *_args: Any) -> None: ...
    def set_word_direction(
        self, text: Gtk.Text, prev_direction: Gtk.TextDirection
    ) -> None: ...
    def generate_word_type(self) -> None: ...
    def remove_list_prop_on_backspace(self, text: Gtk.Text) -> None: ...
    def update_word(self, text: Gtk.Text) -> None: ...
    def add_list_prop(self, button: Gtk.Button) -> None: ...
    def delete(self) -> None: ...
    def do_check_button(self, *_args: Any) -> None: ...
    def on_check_button_toggled(self, button: Gtk.CheckButton) -> None: ...
    def get_ref_count(self) -> None: ...
    @property
    def word(self) -> str: ...
    @word.setter
    def word(self, word: str) -> None: ...
    @property
    def pronunciation(self) -> str: ...
    @pronunciation.setter
    def pronunciation(self, pronunciation: str) -> None: ...
    @property
    def translation(self) -> str: ...
    @property
    def ref_count(self) -> int: ...

class ReferenceRow(Adw.ActionRow):
    """Reference row widget

    Parameters
    ----------
    word_row : WordRow
        The word row to which this reference belongs.
    show_delete_button : bool
        Whether to show the delete button or not.
    """

    __gtype_name__: str
    delete_button_box: Gtk.Box

    def __init__(self, word_row: WordRow, show_delete_button: bool = False) -> None: ...
    def refer_this_word(self, *_args: Any) -> None: ...
    def open_this_word(self, *_args: Any) -> None: ...
    def on_clicked(self, *_args: Any) -> None: ...
    def on_delete_button_clicked(self, *_args: Any) -> None: ...

class EntryRow(Adw.EntryRow):
    """Custom entry row widget.

    Used for displaying and editing text entries with a title.

    Parameters
    ----------
    title : str, optional
        The title of the entry row, by default "".
    text : str, optional
        The initial text of the entry row, by default "".
    """

    __gtype_name__: str

    def __init__(self, title: str = "", text: str = "") -> None: ...
    def get_gtk_text(self) -> Gtk.Text: ...
