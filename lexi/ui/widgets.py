import os
from typing import TextIO

import yaml
from gi.repository import Adw, Gio, Gtk

from lexi import enums, shared
from lexi.logging.logger import logger
from lexi.ui.Preferences import LexiPreferences

gtc = Gtk.Template.Child  # pylint: disable=invalid-name


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/LexiconRow.ui")
class LexiconRow(Gtk.Box):
    """Lexicon row widget.

    Represents a single lexicon in the sidebar.

    Parameters
    ----------
    file : str
        The file to load the lexicon from.
    """

    __gtype_name__ = "LexiconRow"

    add_word_dialog: Adw.Dialog = gtc()
    word_entry_row: Adw.EntryRow = gtc()
    translation_entry_row: Adw.EntryRow = gtc()
    example_entry_row: Adw.EntryRow = gtc()
    actions_popover: Gtk.PopoverMenu = gtc()
    rename_alert_dialog: Adw.AlertDialog = gtc()
    rename_entry: Gtk.Entry = gtc()
    deletion_alert_dialog: Adw.AlertDialog = gtc()

    title: Gtk.Label = gtc()

    def __init__(self, file: str) -> None:
        """Initialize the LexiconRow widget.

        Parameters
        ----------
        file : str
            Path to the lexicon file.
        """
        super().__init__()
        self.file: TextIO = open(file, "r+")
        self.data: dict = yaml.safe_load(self.file)
        self.title.set_label(self.data["name"])
        self.actions_popover.set_parent(self)

        self.rmb_gesture = Gtk.GestureClick(button=3)
        self.long_press_gesture = Gtk.GestureLongPress()
        self.add_controller(self.rmb_gesture)
        self.add_controller(self.long_press_gesture)
        self.rmb_gesture.connect("released", lambda *_: self.actions_popover.popup())
        self.long_press_gesture.connect(
            "pressed", lambda *_: self.actions_popover.popup()
        )

        actions: Gio.SimpleActionGroup = Gio.SimpleActionGroup.new()
        rename_action: Gio.SimpleAction = Gio.SimpleAction.new("rename", None)
        rename_action.connect("activate", self.rename_lexicon)
        delete_action: Gio.SimpleAction = Gio.SimpleAction.new("delete", None)
        delete_action.connect(
            "activate", lambda *_: self.deletion_alert_dialog.present(shared.win)
        )
        actions.add_action(rename_action)
        actions.add_action(delete_action)
        self.insert_action_group("lexicon", actions)

    def save_lexicon(self) -> None:
        """Save the lexicon to the file."""
        self.file.seek(0)
        self.file.truncate(0)
        logger.info("Saving lexicon %s", self.data["name"])
        yaml.dump(
            self.data, self.file, sort_keys=False, encoding=None, allow_unicode=True
        )

    @Gtk.Template.Callback()
    def delete_lexicon(self, _alert_dialog: Adw.AlertDialog, response: str) -> None:
        """Delete the lexicon if the user confirms.

        Parameters
        ----------
        _alert_dialog : Adw.AlertDialog
            The alert dialog prompting the user.
        response : str
            The user's response to the dialog.
        """
        if response == "delete":
            logger.info("Deleting lexicon %s", self.data["name"])
            if shared.win.loaded_lexicon == self:
                shared.win.set_word_rows_sensetiveness(False)
                try:
                    if shared.win.loaded_word.lexicon == self:
                        shared.win.loaded_word.delete()
                except AttributeError:
                    pass

                shared.win.lexicon_scrolled_window.set_child(
                    shared.win.lexicon_not_selected
                )
                shared.win.words_bottom_bar_revealer.set_reveal_child(False)

            self.file.close()
            os.remove(self.file.name)
            logger.info("Lexicon %s deleted", self.data["name"])
            shared.win.build_sidebar()
        else:
            logger.info("Lexicon %s deletion cancelled", self.data["name"])

    def rename_lexicon(self, *_args) -> None:
        """Show the rename popover for the lexicon."""
        logger.info("Renaming lexicon %s", self.data["name"])
        self.rename_alert_dialog.present(shared.win)
        self.rename_entry.set_buffer(Gtk.EntryBuffer.new(self.name, -1))
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
        """Rename the lexicon.

        Parameters
        ----------
        entry_row : Adw.EntryRow
            The entry row containing the new name.
        """
        if response == "rename":
            if alert_dialog.get_extra_child().get_text_length() != 0:
                logger.info(
                    "Renaming lexicon: %s -> %s",
                    self.name,
                    alert_dialog.get_extra_child().get_buffer().get_text(),
                )
                self.name = alert_dialog.get_extra_child().get_buffer().get_text()
            else:
                logger.warning("Lexicon name cannot be empty")
            shared.win.build_sidebar()
        else:
            logger.info("Lexicon %s renaming cancelled", self.data["name"])

    def show_add_word_dialog(self) -> None:
        """Show the dialog for adding a new word."""
        self.word_entry_row.set_text("")
        self.word_entry_row.remove_css_class("error")
        self.translation_entry_row.set_text("")
        self.example_entry_row.set_text("")
        logger.info("Showing add word dialog for lexicon %s", self.data["name"])
        self.add_word_dialog.present(shared.win)
        self.add_word_dialog.grab_focus()

    @Gtk.Template.Callback()
    def add_word(self, *_args) -> None:
        """Add a new word to the lexicon.

        Raises
        ------
        AttributeError
            If the word field is empty.
        """
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

        new_word = {
            "id": max((word["id"] for word in self.data["words"]), default=0) + 1,
            "word": word,
            "translations": translation if translation == [] else [translation],
            "pronunciation": "",
            "types": [],
            "examples": example if example == [] else [example],
            "references": [],
            "tags": [],
        }
        self.data["words"].append(new_word)
        logger.info(
            "Word %s added to the %s Lexicon", new_word["word"], self.data["name"]
        )
        self.save_lexicon()
        shared.win.lexicon_list_box.append(WordRow(new_word, self))
        shared.win.lexicon_scrolled_window.set_child(shared.win.lexicon_list_box)
        shared.win.words_bottom_bar_revealer.set_reveal_child(True)
        self.add_word_dialog.close()
        shared.win.lexicon_list_box.invalidate_sort()

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

    @property
    def name(self) -> str:
        return self.data["name"]

    @name.setter
    def name(self, name: str) -> None:
        if len(name) == 0:
            logger.warning("Lexicon name cannot be empty")
            raise AttributeError("Lexicon name cannot be empty")

        self.data["name"] = name
        self.save_lexicon()
        self.title.set_label(name)


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/WordRow.ui")
class WordRow(Adw.ActionRow):
    """Word row widget.

    Represents a single word in the lexicon.

    Parameters
    ----------
    word : dict
        A dictionary containing word details.
    lexicon : LexiconRow
        The parent lexicon row.
    """

    __gtype_name__ = "WordRow"

    title_label: Gtk.Label = gtc()
    subtitle_label: Gtk.Label = gtc()
    tags_box: Adw.WrapBox = gtc()
    check_button: Gtk.CheckButton = gtc()
    check_button_revealer: Gtk.Revealer = gtc()
    refs_count_label_box: Gtk.Box = gtc()
    refs_count_label: Gtk.Label = gtc()
    tag_alert_dialog: Adw.AlertDialog = gtc()
    tag_alert_dialog_entry: Gtk.Entry = gtc()

    def __init__(self, word: dict, lexicon: LexiconRow) -> None:
        """Initialize the WordRow widget.

        Parameters
        ----------
        word : dict
            The word data.
        lexicon : LexiconRow
            The parent lexicon row.
        """
        super().__init__()
        self.lexicon: LexiconRow = lexicon
        self.word_dict: dict = word
        self.title = self.word_dict["word"].replace("&rtl", "")
        try:
            self.subtitle = word["translations"][0]
        except IndexError:
            self.subtitle = _("No translation yet")

        self.generate_tag_chips()

    @Gtk.Template.Callback()
    def load_word(self, *_args) -> None:
        """Load the word into the main window."""
        logger.info("Loading word %s", self.word_dict["word"])
        shared.win.loaded_word = self
        shared.win.translations_list_box.remove_all()
        shared.win.examples_list_box.remove_all()
        for child in shared.win.word_entry_row.get_child():
            for _item in child:
                if isinstance(_item, Gtk.Text):
                    _item.set_buffer(
                        Gtk.EntryBuffer.new(self.word.replace("&rtl", ""), -1)
                    )
                    if self.word.startswith("&rtl"):
                        _item.set_direction(Gtk.TextDirection.RTL)
                    else:
                        _item.set_direction(Gtk.TextDirection.LTR)
                    _item.connect(
                        "direction-changed",
                        shared.win.on_word_direction_changed,
                    )
                    break
        shared.win.pronunciation_entry_row.set_text(self.pronunciation)
        for expander_row in (
            (shared.win.translations_expander_row, "translations", _("Translation")),
            (shared.win.examples_expander_row, "examples", _("Example")),
        ):
            for item in self.word_dict[expander_row[1]]:
                row: EntryRow = EntryRow(
                    text=item.replace("&rtl", ""), title=expander_row[2]
                )
                _item = row.get_gtk_text()
                if item.startswith("&rtl"):
                    _item.set_direction(Gtk.TextDirection.RTL)
                _item.connect("changed", self.update_word)
                _item.connect("backspace", self.remove_list_prop_on_backspace)
                _item.connect("direction-changed", self.set_word_direction)
                expander_row[0].add_row(row)

        self.generate_word_type()

        if self.word != "":
            shared.win.word_nav_page.set_title(self.word.replace("&rtl", ""))
        else:
            shared.win.word_nav_page.set_title(_("Word"))
            self.title = _("Word")

        shared.win.references_list_box.remove_all()
        for word_row in shared.win.lexicon_list_box:
            if word_row.word_dict["id"] in self.word_dict["references"]:
                shared.win.references_list_box.append(ReferenceRow(word_row, True))

        if shared.win.lexicon_split_view.get_collapsed():
            shared.win.lexicon_split_view.set_show_content(True)

        shared.win.set_word_rows_sensetiveness(True)
        logger.info("Word %s loaded", self.word_dict["word"])

    def set_word_direction(
        self, text: Gtk.Text, prev_direction: Gtk.TextDirection
    ) -> None:
        """Set the text direction for a word property.

        Parameters
        ----------
        text : Gtk.Text
            The text widget whose direction is being set.
        prev_direction : Gtk.TextDirection
            The previous direction of the text.
        """
        directionable_row = text.get_ancestor(EntryRow)
        expander_row = directionable_row.get_ancestor(Adw.ExpanderRow)

        for attr in dir(shared.win):
            if (
                attr.endswith("_expander_row")
                and getattr(shared.win, attr) == expander_row
            ):
                list_box = getattr(
                    shared.win, attr.replace("_expander_row", "") + "_list_box"
                )
                for index, row in enumerate(list_box):
                    if row == directionable_row:
                        if prev_direction in (
                            Gtk.TextDirection.LTR,
                            Gtk.TextDirection.NONE,
                        ):
                            logger.debug(
                                "Setting RTL direction for %s item",
                                attr.replace("_expander_row", ""),
                            )
                            self.word_dict[attr.replace("_expander_row", "")][index] = (
                                "&rtl" + text.get_text()
                            )
                            break
                        logger.debug(
                            "Setting LTR direction for %s item",
                            attr.replace("_expander_row", ""),
                        )
                        self.word_dict[attr.replace("_expander_row", "")][
                            index
                        ] = text.get_text().replace("&rtl", "")
                        break
                break
        if enums.Schema.WORD_AUTOSAVE():
            self.lexicon.save_lexicon()

    def generate_word_type(self) -> None:
        """Generate the word type subtitle and toggle check buttons."""
        shared.win.word_types_list_box.remove_all()
        subtitle = ""
        for word_type in self.word_type:
            shared.win.word_types_list_box.append(WordTypeRow(word_type))
            subtitle += word_type + ", "
        if len(subtitle) > 0:
            subtitle = subtitle[:-2]
            shared.win.word_type_expander_row.set_subtitle(subtitle)
        else:
            shared.win.word_type_expander_row.set_subtitle("")

    def remove_list_prop_on_backspace(self, text: Gtk.Text) -> None:
        """Remove a list property row on backspace.

        Parameters
        ----------
        text : Gtk.Text
            The text widget triggering the action.
        """
        if text.get_text_length() > 0:
            return

        row = text.get_ancestor(EntryRow)
        expander_row = row.get_ancestor(Adw.ExpanderRow)

        for attr_name, expander in (
            (attr.replace("_expander_row", ""), getattr(shared.win, attr))
            for attr in dir(shared.win)
            if attr.endswith("_expander_row")
        ):
            if expander is expander_row:
                list_box = getattr(shared.win, attr_name + "_list_box")
                row_index = next(
                    (i for i, _row in enumerate(list_box) if row == _row), None
                )
                if row_index is not None:
                    expander_row.remove(row)
                    logger.info("Removing %s row", attr_name)
                    del self.word_dict[attr_name][row_index]
                    if enums.Schema.WORD_AUTOSAVE():
                        self.lexicon.save_lexicon()
                return

    def update_word(self, text: Gtk.Text) -> None:
        """Update the word dictionary when a property changes.

        Parameters
        ----------
        text : Gtk.Text
            The text widget triggering the update.
        """
        row = text.get_ancestor(EntryRow)
        expander_row = row.get_ancestor(Adw.ExpanderRow)

        for attr_name, expander in (
            (attr.replace("_expander_row", ""), getattr(shared.win, attr))
            for attr in dir(shared.win)
            if attr.endswith("_expander_row")
        ):
            if expander is expander_row:
                list_box = getattr(shared.win, attr_name + "_list_box")
                row_index = next(
                    (i for i, _row in enumerate(list_box) if row == _row), None
                )
                if row_index is not None:
                    if self.word_dict[attr_name][row_index].startswith("&rtl"):
                        self.word_dict[attr_name][row_index] = "&rtl" + row.get_text()
                    else:
                        self.word_dict[attr_name][row_index] = row.get_text()
                    try:
                        if self.word_dict["translations"][0] != "":
                            self.subtitle = self.word_dict["translations"][0]
                        else:
                            self.subtitle = _("No translation yet")
                    except IndexError:
                        self.subtitle = _("No translation yet")
                    if enums.Schema.WORD_AUTOSAVE():
                        self.lexicon.save_lexicon()
                return

    def add_list_prop(self, button: Gtk.Button) -> None:
        """Add a new property to the word's list attributes.

        Parameters
        ----------
        button : Gtk.Button
            The button triggering the action.
        """
        expander_row: Adw.ExpanderRow = button.get_ancestor(Adw.ExpanderRow)

        for attr_name, expander in (
            (attr.replace("_expander_row", ""), getattr(shared.win, attr))
            for attr in dir(shared.win)
            if attr.endswith("_expander_row")
        ):
            if expander is expander_row:
                new_row: EntryRow = EntryRow(
                    title=(
                        _("Translation")
                        if attr_name == "translations"
                        else _("Example")
                    )
                )
                text = new_row.get_gtk_text()
                logger.info("Adding %s row", attr_name)
                expander_row.add_row(new_row)
                self.word_dict[attr_name].append("")
                text.connect("changed", self.update_word)
                text.connect("backspace", self.remove_list_prop_on_backspace)
                if enums.Schema.WORD_AUTOSAVE():
                    self.lexicon.save_lexicon()
                return

    def delete(self) -> None:
        """Delete the word from the lexicon."""
        self.lexicon.data["words"].remove(self.word_dict)
        logger.info("Dereffering %s from other words", self.word)
        for word in self.lexicon.data["words"]:
            if self.word_dict["id"] in word["references"]:
                logger.info("Removing %s from %s references", self.word, word["word"])
                word["references"].remove(self.word_dict["id"])
        shared.win.lexicon_list_box.remove(self)
        if shared.win.loaded_word is self:
            shared.win.word_nav_page.set_title(_("Word"))
            shared.win.word_entry_row.set_text("")
            shared.win.pronunciation_entry_row.set_text("")
            shared.win.translations_list_box.remove_all()
            shared.win.examples_list_box.remove_all()
            shared.win.references_list_box.remove_all()
        shared.win.loaded_word = None
        self.lexicon.save_lexicon()

    def do_check_button(self, *_args) -> None:
        """Toggle the visibility of the check button."""
        if not self.check_button_revealer.get_reveal_child():
            shared.win.selection_mode_toggle_button.set_active(True)
            self.check_button.set_active(True)
            logger.debug("Check button activated")
        else:
            self.check_button.set_active(not self.check_button.get_active())
            logger.debug("Check button deactivated")

    @Gtk.Template.Callback()
    def on_check_button_toggled(self, button: Gtk.CheckButton) -> None:
        """Handle toggling of the check button.

        Parameters
        ----------
        button : Gtk.CheckButton
            The check button being toggled.
        """
        if button.get_active():
            logger.debug("Adding %s to deleatable words", self.word)
            shared.win.selected_words.append(self)
        else:
            shared.win.selected_words.remove(self)
            logger.debug("Removing %s from deleatable words", self.word)

    def get_ref_count(self) -> None:
        """Update the reference count label."""
        logger.debug("Updating reference count for %s", self.word)
        if self.ref_count > 0:
            self.refs_count_label_box.set_visible(True)
            self.refs_count_label.set_label(str(self.ref_count))
        else:
            self.refs_count_label_box.set_visible(False)

    @Gtk.Template.Callback()
    def on_add_tag_button_clicked(self, *_args) -> None:
        logger.info("Showing tag addition alert dialog for %s", self.word)
        self.tag_alert_dialog_entry.set_text("")
        self.tag_alert_dialog.present(shared.win)

    @Gtk.Template.Callback()
    def on_tag_alert_dialog_entry_changed(self, entry: Gtk.Entry) -> None:
        if (
            "#" in entry.get_text()
            or entry.get_text().lower() in self.tags
            or " " in entry.get_text().strip()
        ):
            entry.add_css_class("error")
        else:
            if "error" in entry.get_css_classes():
                entry.remove_css_class("error")

    @Gtk.Template.Callback()
    def on_tag_alert_dialog_response(
        self, _alert_dialog: Adw.AlertDialog, response: str
    ) -> None:
        if response == "add":
            tag = self.tag_alert_dialog_entry.get_text().lower().strip()
            if "#" in tag or " " in tag or tag == "":
                logger.warning("Tag cannot contain spaces or '#'")
                raise AttributeError("Tag cannot contain spaces or '#'")

            if tag in self.tags:
                logger.warning("Tag already exists")
                raise AttributeError("Tag already exists")

            self.tags.append(tag)
            self.tags.sort()
            self.lexicon.save_lexicon()
            logger.info("Tag #%s added to %s", tag, self.word)
            self.generate_tag_chips()
        else:
            logger.info("Tag addition cancelled")

    def generate_tag_chips(self) -> None:
        for _tag in self.tags_box:  # pylint: disable=not-an-iterable
            self.tags_box.remove(_tag)
        if self.tags != []:

            def clicked(_button: Gtk.Button, tag: str) -> None:
                current_text = shared.win.lexicon_search_entry.get_text()
                if not current_text.startswith("#") and current_text != "":
                    return  # Do nothing if the string doesn't start with '#'
                logger.info("Searching for words with tag %s", current_text + f"#{tag}")
                shared.win.lexicon_search_entry.set_text(current_text + f"#{tag}")

            def rmb_clicked(
                _button: Gtk.Button,
                _gesture: Gtk.GestureClick,
                _x: float,
                _y: float,
                tag: str,
            ) -> None:
                self.tags.remove(tag)
                logger.info("Tag #%s removed from %s", tag, self.word)
                self.lexicon.save_lexicon()
                for _tag in self.tags_box:  # pylint: disable=not-an-iterable
                    self.tags_box.remove(_tag)
                self.generate_tag_chips()

            for tag in self.tags:
                button = Gtk.Button(
                    label=f"#{tag}",
                    valign=Gtk.Align.CENTER,
                    css_classes=["pill", "small"],
                    # pylint: disable=line-too-long
                    tooltip_text=_(
                        "Click LMB to search words with this tag\nClick RMB to remove this tag"
                    ),
                )
                button.connect("clicked", clicked, tag)
                rmb = Gtk.GestureClick(button=3)
                rmb.connect("released", rmb_clicked, tag)
                button.add_controller(rmb)
                self.tags_box.append(button)

    # UI Props
    @property
    def title(self) -> str:
        return self.title_label.get_label()

    @title.setter
    def title(self, title: str) -> None:
        self.title_label.set_label(title)

    @property
    def subtitle(self) -> str:
        return self.subtitle_label.get_label()

    @subtitle.setter
    def subtitle(self, subtitle: str) -> None:
        self.subtitle_label.set_label(subtitle)

    # data props
    @property
    def word(self) -> str:
        return self.word_dict["word"]

    @word.setter
    def word(self, word: str) -> None:
        self.word_dict["word"] = word
        self.title = word
        if word != "":
            shared.win.word_nav_page.set_title(word)
        else:
            shared.win.word_nav_page.set_title(_("Word"))
            self.title = _("Word")

        if enums.Schema.WORD_AUTOSAVE():
            self.lexicon.save_lexicon()

    @property
    def pronunciation(self) -> str:
        return self.word_dict["pronunciation"]

    @pronunciation.setter
    def pronunciation(self, pronunciation: str) -> None:
        self.word_dict["pronunciation"] = pronunciation

        if enums.Schema.WORD_AUTOSAVE():
            self.lexicon.save_lexicon()

    @property
    def translation(self) -> str:
        try:
            return self.word_dict["translations"][0]
        except IndexError:
            return ""

    @property
    def ref_count(self) -> int:
        count: int = 0
        for row in shared.win.lexicon_list_box:
            for ref in row.word_dict["references"]:
                if ref == self.word_dict["id"]:
                    count += 1
                    break
        return count

    @property
    def word_type(self) -> list:
        return self.word_dict["types"]

    @property
    def tags(self) -> list:
        return self.word_dict["tags"]


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/ReferenceRow.ui")
class ReferenceRow(Adw.ActionRow):
    """Reference row widget.

    Represents a reference to another word.

    Parameters
    ----------
    word_row : WordRow
        The word row being referenced.
    show_delete_button : bool
        Whether to show the delete button.
    """

    __gtype_name__ = "ReferenceRow"

    delete_button_box: Gtk.Box = gtc()

    def __init__(self, word_row: WordRow, show_delete_button: bool = False) -> None:
        """Initialize the ReferenceRow widget.

        Parameters
        ----------
        word_row : WordRow
            The word row being referenced.
        show_delete_button : bool, optional
            Whether to show the delete button, by default False.
        """
        super().__init__()
        self.delete_button_box.set_visible(show_delete_button)
        self.word_row: WordRow = word_row
        self.set_title(self.word_row.word)
        self.set_subtitle(self.word_row.translation)

    def refer_this_word(self, *_args) -> None:
        """Add a reference to the word."""
        shared.win.loaded_word.word_dict["references"].append(
            self.word_row.word_dict["id"]
        )
        if enums.Schema.WORD_AUTOSAVE():
            shared.win.loaded_lexicon.save_lexicon()
        shared.win.references_dialog_list_box.remove(self)

        shared.win.references_list_box.remove_all()
        for word_row in shared.win.lexicon_list_box:
            if (
                word_row.word_dict["id"]
                in shared.win.loaded_word.word_dict["references"]
            ):
                shared.win.references_list_box.append(ReferenceRow(word_row, True))

        logger.info(
            "%s added to %s references", self.word_row.word, shared.win.loaded_word.word
        )
        if shared.win.references_dialog_list_box.get_row_at_index(0) is None:
            logger.info("No more words to refer")
            shared.win.references_dialog.close()
        shared.win.update_refs_count()

    def open_this_word(self, *_args) -> None:
        """Open the referenced word."""
        logger.info("Opening word %s", self.word_row.word)
        shared.win.lexicon_list_box.select_row(self.word_row)
        self.word_row.load_word()

    @Gtk.Template.Callback()
    def on_clicked(self, *_args) -> None:
        """Handle click events."""
        if shared.win.references_dialog is shared.win.props.visible_dialog:
            self.refer_this_word()
        else:
            self.open_this_word()

    @Gtk.Template.Callback()
    def on_delete_button_clicked(self, *_args) -> None:
        """Remove the reference to the word."""
        shared.win.loaded_word.word_dict["references"].remove(
            self.word_row.word_dict["id"]
        )
        logger.info(
            "%s removed from %s references",
            self.word_row.word,
            shared.win.loaded_word.word,
        )

        if enums.Schema.WORD_AUTOSAVE():
            shared.win.loaded_lexicon.save_lexicon()
        shared.win.references_list_box.remove(self)
        shared.win.update_refs_count()


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

    __gtype_name__ = "LexiEntryRow"

    def __init__(self, title: str = "", text: str = "") -> None:
        """Initialize the EntryRow widget.

        Parameters
        ----------
        title : str, optional
            The title of the entry row, by default "".
        text : str, optional
            The initial text of the entry row, by default "".
        """
        super().__init__(title=title, text=text)

    def get_gtk_text(self) -> Gtk.Text:
        """Retrieve the Gtk.Text widget from the entry row.

        Returns
        -------
        Gtk.Text
            The Gtk.Text widget contained in the entry row.
        """
        for item in self.get_child():
            for _item in item:
                if isinstance(_item, Gtk.Text):
                    return _item


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/WordTypeRow.ui")
class WordTypeRow(Adw.ActionRow):
    """WordTypeRow widget.

    Parameters
    ----------
    word_type : str
        The type of the word.
    deactivate : bool, optional
        Whether to deactivate the row and activate the button, by default True.
    """

    __gtype_name__ = "WordTypeRow"

    unassign_button: Gtk.Button = gtc()

    def __init__(self, word_type: str, deactivate: bool = True) -> None:
        """Initialize the WordTypeRow widget.

        Parameters
        ----------
        word_type : str
            The type of the word.
        deactivate : bool, optional
            Whether to deactivate the row and activate the button, by default True.
        """
        super().__init__()
        self.set_title(word_type)
        self.word_type: str = word_type

        if deactivate:
            self.set_activatable(False)
        else:
            self.unassign_button.set_visible(False)

    @Gtk.Template.Callback()
    def on_unassign_clicked(self, *_args) -> None:
        """Unassign the word type from the word."""
        if not isinstance(dialog := shared.win.props.visible_dialog, LexiPreferences):
            shared.win.loaded_word.word_dict["types"].remove(self.word_type)
            shared.win.word_types_list_box.remove(self)
            logger.info(
                "Unassigning %s from %s", self.word_type, shared.win.loaded_word.word
            )
            shared.win.loaded_word.generate_word_type()
            if enums.Schema.WORD_AUTOSAVE():
                shared.win.loaded_lexicon.save_lexicon()
        else:
            logger.info("Removing %s from word types", self.word_type)
            dialog.available_word_types_list_box.remove(self)
            shared.config["word-types"].remove(self.word_type)
            dialog.gen_word_types()

    @Gtk.Template.Callback()
    def on_clicked(self, *_args) -> None:
        """Assign the word type to the word."""
        logger.info("Assigning %s to %s", self.word_type, shared.win.loaded_word.word)
        shared.win.loaded_word.word_type.append(self.word_type)
        shared.win.loaded_word.generate_word_type()
        if enums.Schema.WORD_AUTOSAVE():
            shared.win.loaded_lexicon.save_lexicon()
        if shared.win.props.visible_dialog == shared.win.assign_word_type_dialog:
            shared.win.assign_word_type_dialog_list_box.remove(self)
