# pylint: disable=all
from gi.repository import Adw

class LexiPreferences(Adw.PreferencesDialog):
    """Lexi preferences dialog"""
    __gtype_name__: str

    word_autosave_switch_row: Adw.SwitchRow

    opened: bool

    def set_save_button_sensetive(self, *_args) -> None: ...
    def set_opened(self, opened: bool) -> None: ...
