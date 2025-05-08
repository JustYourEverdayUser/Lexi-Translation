from gi.repository import Adw, Gio, Gtk

from lexi import enums, shared
from lexi.logging.logger import logger
from lexi.ui.WordRow import WordRow
from lexi.utils.backend import Lexicon

gtc = Gtk.Template.Child  # pylint: disable=invalid-name


# pylint: disable=unused-private-member
@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/LexiconRow.ui")
class LexiconRow(Gtk.Box):
    __gtype_name__ = "LexiconRow"

    title: Gtk.Label = gtc()
    add_word_dialog: Adw.AlertDialog = gtc()
    word_entry_row: Adw.EntryRow = gtc()
    translation_entry_row: Adw.EntryRow = gtc()
    example_entry_row: Adw.EntryRow = gtc()
    actions_popover: Gtk.Popover = gtc()
    rename_alert_dialog: Adw.AlertDialog = gtc()
    rename_entry: Gtk.Entry = gtc()
    deletion_alert_dialog: Adw.AlertDialog = gtc()

    def __init__(self, lexicon: Lexicon) -> "LexiconRow":
        super().__init__()

        self.title.set_label(lexicon.name)
        self.lexicon = lexicon
        self.lexicon.connect(
            "notify::name", lambda *_: self.title.set_label(lexicon.name)
        )

        self.rmb_gesture = Gtk.GestureClick(button=3)
        self.long_press_gesture = Gtk.GestureLongPress()
        self.add_controller(self.rmb_gesture)
        self.add_controller(self.long_press_gesture)
        self.rmb_gesture.connect("released", lambda *_: self.actions_popover.popup())
        self.long_press_gesture.connect(
            "pressed", lambda *_: self.actions_popover.popup()
        )

        actions: Gio.SimpleActionGroup = Gio.SimpleActionGroup()
        rename_action: Gio.SimpleAction = Gio.SimpleAction.new("rename", None)
        rename_action.connect("activate", self.__rename_lexicon)
        delete_action: Gio.SimpleAction = Gio.SimpleAction.new("delete", None)
        delete_action.connect(
            "activate", lambda *_: self.deletion_alert_dialog.present(shared.win)
        )
        actions.add_action(rename_action)
        actions.add_action(delete_action)
        self.insert_action_group("lexicon", actions)

        self.actions_popover.set_parent(self)

    @Gtk.Template.Callback()
    def delete_lexicon(self, _alert_dialog: Adw.AlertDialog, response: str) -> None:
        """Handle the delete action.

        Parameters
        ----------
        _alert_dialog : Adw.AlertDialog
            The alert dialog that was used to delete the lexicon.
        response : str
            The response from the alert dialog.
        """
        if response == "delete":
            logger.info("Deleting lexicon “%s”", self.lexicon.name)
            shared.lexictrl.rm_lexicon(self.lexicon.id)
            logger.info("Lexicon “%s” deleted", self.lexicon.name)
            shared.win.build_sidebar()
            shared.win.set_property("loaded-lexicon", None)
        else:
            logger.debug("Lexicon “%s” deletion cancelled", self.lexicon.name)

    def __rename_lexicon(self, *_args) -> None:
        """Show the rename popover for the lexicon."""
        logger.info("Renaming lexicon %s", self.lexicon.name)
        self.rename_alert_dialog.present(shared.win)
        self.rename_entry.set_buffer(Gtk.EntryBuffer.new(self.lexicon.name, -1))
        self.rename_entry.grab_focus()

    @Gtk.Template.Callback()
    def on_rename_entry_changed(self, text: Gtk.Text) -> None:
        """Handle changes to the rename entry field.

        Parameters
        ----------
        text : Gtk.Text
            The text entry field being edited.
        """
        if text.get_text_length() == 0:
            self.rename_entry.add_css_class("error")
        else:
            if "error" in self.rename_entry.get_css_classes():
                self.rename_entry.remove_css_class("error")

    @Gtk.Template.Callback()
    def do_rename(self, alert_dialog: Adw.AlertDialog, response: str) -> None:
        """Handle the rename action.

        Parameters
        ----------
        alert_dialog : Adw.AlertDialog
            The alert dialog that was used to rename the lexicon.
        response : str
            The response from the alert dialog.
        """
        if response == "rename":
            if alert_dialog.get_extra_child().get_text_length() != 0:
                logger.info(
                    "Renaming lexicon “%s” to “%s”",
                    self.lexicon.name,
                    alert_dialog.get_extra_child().get_buffer().get_text(),
                )
                self.lexicon.name = (
                    alert_dialog.get_extra_child().get_buffer().get_text()
                )
            else:
                logger.warning("Lexicon name is empty")
            shared.win.build_sidebar()
        else:
            logger.debug("Lexicon “%s” renaming cancelled", self.lexicon.name)

    def show_add_word_dialog(self, *_args) -> None:
        self.word_entry_row.set_text("")
        self.word_entry_row.remove_css_class("error")
        self.translation_entry_row.set_text("")
        self.example_entry_row.set_text("")
        logger.info("Showing add word dialog for lexicon “%s”", self.lexicon.name)
        self.add_word_dialog.present(shared.win)
        self.add_word_dialog.grab_focus()

    @Gtk.Template.Callback()
    def check_if_word_is_empty(self, row: Adw.EntryRow) -> None:
        """Check if the word entry is empty and apply error styling.

        Parameters
        ----------
        row : Adw.EntryRow
            The entry row to check.
        """
        if len(row.get_text()) == 0:
            row.add_css_class("error")
        else:
            row.remove_css_class("error")

    @Gtk.Template.Callback()
    def on_add_word_dialog_enter_press(self, *_args) -> None:
        """Handle the Enter key press in the add word dialog."""
        self.add_word()

    @Gtk.Template.Callback()
    def add_word(self, *_args) -> None:
        word = self.word_entry_row.get_text()
        translation = self.translation_entry_row.get_text()
        example = self.example_entry_row.get_text()

        if len(word) == 0:
            self.word_entry_row.add_css_class("error")
            logger.warning("Word cannot be empty")
            raise AttributeError("Word cannot be empty")

        if len(translation) == 0:
            translation = []

        if len(example) == 0:
            example = []

        id_ = max((w.id for w in self.lexicon.words), default=0) + 1
        new_word: dict = {
            "id": id_,
            "word": word,
            "translations": [translation] if translation else [],
            "pronunciation": "",
            "types": [],
            "examples": example if example == [] else [example],
            "references": [],
            "tags": [],
        }
        self.lexicon.add_word(new_word)
        logger.info("Word “%s” added to the “%s” Lexicon", word, self.lexicon.name)
        shared.win.lexicon_list_box.append(
            word_row := WordRow(self.lexicon.get_word(id_))
        )
        shared.win.lexicon_list_box.select_row(word_row)
        word_row.activate()
        shared.win.set_property("state", enums.WindowState.WORDS)
        self.add_word_dialog.close()
        shared.win.lexicon_list_box.invalidate_sort()
        shared.win.lexicon_list_box.invalidate_filter()
