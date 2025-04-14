from gi.repository import Adw, Gio, Gtk

from lexi import shared
from lexi.utils import backup

gtc = Gtk.Template.Child  # pylint: disable=invalid-name


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/Preferences.ui")
class LexiPreferences(Adw.PreferencesDialog):
    """Lexi preferences dialog"""

    __gtype_name__ = "LexiPreferences"

    word_autosave_switch_row: Adw.SwitchRow = gtc()

    opened: bool = False

    def __init__(self) -> None:
        super().__init__()
        self.__class__.opened = True
        self.connect("closed", lambda *_: self.set_opened(False))

        shared.schema.bind(
            "word-autosave",
            self.word_autosave_switch_row,
            "active",
            Gio.SettingsBindFlags.DEFAULT,
        )

        self.word_autosave_switch_row.connect(
            "notify::active", self.set_save_button_sensetive
        )

    def set_save_button_sensetive(self, *_args) -> None:
        """Set save word button sensitiveness according to the word-autosave state"""
        enabled = not self.word_autosave_switch_row.get_active()
        if enabled:
            shared.win.save_word_button.set_sensitive(True)
            shared.win.save_word_button.add_css_class("suggested-action")
        else:
            shared.win.save_word_button.set_sensitive(False)
            shared.win.save_word_button.remove_css_class("suggested-action")

    def set_opened(self, opened: bool) -> None:
        """Allows the existance of only one Preferences dialog at once

        Parameters
        ----------
        opened : bool
            state for the __class__.opened variable
        """
        self.__class__.opened = opened

    @Gtk.Template.Callback()
    def on_export_button_clicked(self, *_args) -> None:
        dialog = Gtk.FileDialog(initial_name="lexi_backup.zip")
        dialog.save(shared.win, None, self.on_export_database)

    def on_export_database(self, file_dialog: Gtk.FileDialog, result: Gio.Task) -> None:
        path = file_dialog.save_finish(result).get_path()
        backup.export_database(path)
        self.close()
