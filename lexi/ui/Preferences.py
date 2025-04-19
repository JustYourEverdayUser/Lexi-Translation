from gi.repository import Adw, Gio, Gtk

from lexi import shared
from lexi.utils import backup

gtc = Gtk.Template.Child  # pylint: disable=invalid-name


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/Preferences.ui")
class LexiPreferences(Adw.PreferencesDialog):
    """Lexi preferences dialog"""

    __gtype_name__ = "LexiPreferences"

    word_autosave_switch_row: Adw.SwitchRow = gtc()
    import_confirmation_dialog: Adw.AlertDialog = gtc()

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
        """
        Handle the export button click event.

        Opens a file dialog to save the database backup.
        """
        dialog = Gtk.FileDialog(initial_name="lexi_backup.zip")
        dialog.save(shared.win, None, self.on_export_database)

    def on_export_database(self, file_dialog: Gtk.FileDialog, result: Gio.Task) -> None:
        """
        Export the database to the selected file path.

        Parameters
        ----------
        file_dialog : Gtk.FileDialog
            The file dialog used for selecting the export location.
        result : Gio.Task
            The result of the file dialog operation.
        """
        path = file_dialog.save_finish(result).get_path()
        backup.export_database(path)
        self.close()

    @Gtk.Template.Callback()
    def on_import_button_clicked(self, *_args) -> None:
        """
        Handle the import button click event.

        Presents a confirmation dialog before importing a database.
        """
        self.import_confirmation_dialog.present(shared.win)

    @Gtk.Template.Callback()
    def on_import_confirmation_dialog_response(
        self, _alert_dialog: Adw.AlertDialog, response: str
    ) -> None:
        """
        Handle the response from the import confirmation dialog.

        Parameters
        ----------
        _alert_dialog : Adw.AlertDialog
            The alert dialog that emitted this method.
        response : str
            The response ID from the dialog.
        """
        if response == "import":
            dialog = Gtk.FileDialog(
                default_filter=Gtk.FileFilter(mime_types=["application/zip"])
            )
            dialog.open(shared.win, None, self.on_import_database)

    def on_import_database(self, file_dialog: Gtk.FileDialog, result: Gio.Task) -> None:
        """
        Import the database from the selected file path.

        Parameters
        ----------
        file_dialog : Gtk.FileDialog
            The file dialog used for selecting the import file.
        result : Gio.Task
            The result of the file dialog operation.
        """
        path = file_dialog.open_finish(result).get_path()
        backup.import_database(path)
        self.close()
