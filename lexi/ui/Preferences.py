from gi.repository import Adw, Gtk

from lexi import shared

gtc = Gtk.Template.Child  # pylint: disable=invalid-name


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/Preferences.ui")
class LexiPreferences(Adw.PreferencesDialog):
    """Lexi preferences dialog"""

    __gtype_name__ = "LexiPreferences"

    import_confirmation_dialog: Adw.AlertDialog = gtc()
    available_word_types_scrolled_window: Gtk.ScrolledWindow = gtc()
    available_word_types_list_box: Gtk.ListBox = gtc()
    use_debug_log_switch_row: Adw.SwitchRow = gtc()

    opened: bool = False

    def __init__(self) -> None:
        super().__init__()
