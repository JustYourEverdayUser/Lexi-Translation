# pylint: disable=all
from gi.repository import Adw, Gio, Gtk

class LexiPreferences(Adw.PreferencesDialog):
    """Lexi preferences dialog"""

    __gtype_name__: str

    word_autosave_switch_row: Adw.SwitchRow
    import_confirmation_dialog: Adw.AlertDialog

    opened: bool

    def __init__(self) -> None: ...
    def set_save_button_sensetive(self, *_args) -> None: ...
    def set_opened(self, opened: bool) -> None: ...
    def on_export_button_clicked(self, *_args) -> None: ...
    def on_export_database(
        self, file_dialog: Gtk.FileDialog, result: Gio.Task
    ) -> None: ...
    def on_import_button_clicked(self, *_args) -> None: ...
    def on_import_confirmation_dialog_response(
        self, _alert_dialog: Adw.AlertDialog, response: str
    ) -> None: ...
    def on_import_database(
        self, file_dialog: Gtk.FileDialog, result: Gio.Task
    ) -> None: ...
