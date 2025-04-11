import os
from typing import TextIO

import yaml
from gi.repository import Adw, Gio, Gtk

from lexi import enums, shared

gtc = Gtk.Template.Child  # pylint: disable=invalid-name


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/LexiconRow.ui")
class LexiconRow(Gtk.Box):
    """Lexicon row widget

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
    rename_popover: Gtk.Popover = gtc()
    rename_entry: Adw.EntryRow = gtc()
    deletion_alert_dialog: Adw.AlertDialog = gtc()

    title: Gtk.Label = gtc()

    def __init__(self, file: str) -> None:
        super().__init__()
        self.file: TextIO = open(file, "r+")
        self.data: dict = yaml.safe_load(self.file)
        self.title.set_label(self.data["name"])
        self.actions_popover.set_parent(self)
        self.rename_popover.set_parent(self)

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
        yaml.dump(
            self.data, self.file, sort_keys=False, encoding=None, allow_unicode=True
        )

    @Gtk.Template.Callback()
    def delete_lexicon(self, _alert_dialog: Adw.AlertDialog, response: str) -> None:
        if response == "delete":
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
            shared.win.build_sidebar()

    def rename_lexicon(self, *_args) -> None:
        self.rename_popover.popup()
        self.rename_entry.set_text(self.name)

    @Gtk.Template.Callback()
    def on_rename_entry_changed(self, text: Gtk.Text) -> None:
        if text.get_text_length() == 0:
            self.rename_entry.add_css_class("error")
        else:
            if "error" in self.rename_entry.get_css_classes():
                self.rename_entry.remove_css_class("error")

    @Gtk.Template.Callback()
    def do_rename(self, entry_row: Adw.EntryRow) -> None:
        if entry_row.get_text() != "":
            self.name = entry_row.get_text()
        self.rename_popover.popdown()
        shared.win.build_sidebar()

    def show_add_word_dialog(self) -> None:
        """Shows the add word dialog"""
        self.word_entry_row.set_text("")
        self.word_entry_row.remove_css_class("error")
        self.translation_entry_row.set_text("")
        self.example_entry_row.set_text("")
        self.add_word_dialog.present(shared.win)
        self.add_word_dialog.grab_focus()

    @Gtk.Template.Callback()
    def add_word(self, *_args) -> None:
        """Adds a new word to the lexicon

        Raises
        ------
        AttributeError
            Raised if the `Word` field is empty
        """
        word = self.word_entry_row.get_text()
        translation = self.translation_entry_row.get_text()
        example = self.example_entry_row.get_text()

        if len(word) == 0:
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
            "types": {
                "noun": False,
                "verb": False,
                "adjective": False,
                "adverb": False,
                "pronoun": False,
                "preposition": False,
                "conjunction": False,
                "interjection": False,
                "article": False,
                "idiom": False,
                "clause": False,
                "prefix": False,
                "suffix": False,
            },
            "examples": example if example == [] else [example],
            "references": [],
        }
        self.data["words"].append(new_word)
        self.save_lexicon()
        shared.win.lexicon_list_box.append(WordRow(new_word, self))
        shared.win.lexicon_scrolled_window.set_child(shared.win.lexicon_list_box)
        shared.win.words_bottom_bar_revealer.set_reveal_child(True)
        self.add_word_dialog.close()
        shared.win.lexicon_list_box.invalidate_sort()

    @Gtk.Template.Callback()
    def check_if_word_is_empty(self, row: Adw.EntryRow) -> None:
        """Applies `error` CSS class to the `Word` row if the field is empty

        Parameters
        ----------
        row : Adw.EntryRow
            Adw.EntryRow to set CSS to
        """
        if len(row.get_text()) == 0:
            row.add_css_class("error")
        else:
            row.remove_css_class("error")

    @property
    def name(self) -> str:
        return self.data["name"]

    @name.setter
    def name(self, name: str) -> None:
        if len(name) == 0:
            raise AttributeError("Lexicon name cannot be empty")

        self.data["name"] = name
        self.save_lexicon()
        self.title.set_label(name)


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/WordRow.ui")
class WordRow(Adw.ActionRow):
    # pylint: disable=line-too-long
    """Word row widget

    Parameters
    ----------
    word : dict
        a dict with the word [id, word, pronunciation, translations, types, examples, references]
    """

    __gtype_name__ = "WordRow"

    check_button: Gtk.CheckButton = gtc()
    check_button_revealer: Gtk.Revealer = gtc()
    refs_count_label_box: Gtk.Box = gtc()
    refs_count_label: Gtk.Label = gtc()

    def __init__(self, word: dict, lexicon: LexiconRow) -> None:
        super().__init__()
        self.lexicon: LexiconRow = lexicon
        self.word_dict: dict = word
        self.set_title(self.word_dict["word"])
        try:
            self.set_subtitle(word["translations"][0])
        except IndexError:
            self.set_subtitle(_("No translation yet"))

        self.rmb_gesture = Gtk.GestureClick(button=3)
        self.long_press_gesture = Gtk.GestureLongPress()
        self.add_controller(self.rmb_gesture)
        self.add_controller(self.long_press_gesture)

        self.rmb_gesture.connect("released", self.do_check_button)
        self.long_press_gesture.connect("pressed", self.do_check_button)

    @Gtk.Template.Callback()
    def load_word(self, *_args) -> None:
        """Loads word to the window"""
        shared.win.loaded_word = self
        shared.win.translations_list_box.remove_all()
        shared.win.examples_list_box.remove_all()
        shared.win.word_entry_row.set_text(self.word)
        shared.win.pronunciation_entry_row.set_text(self.pronunciation)
        for expander_row in (
            (shared.win.translations_expander_row, "translations", _("Translation")),
            (shared.win.examples_expander_row, "examples", _("Example")),
        ):
            for item in self.word_dict[expander_row[1]]:
                row: Adw.EntryRow = Adw.EntryRow(text=item, title=expander_row[2])
                for child in row.get_child():
                    for _item in child:
                        if isinstance(_item, Gtk.Text):
                            _item.connect("changed", self.update_word)
                            _item.connect(
                                "backspace", self.remove_list_prop_on_backspace
                            )
                            break
                expander_row[0].add_row(row)

        self.generate_word_type()

        if self.word != "":
            shared.win.word_nav_page.set_title(self.word)
        else:
            shared.win.word_nav_page.set_title(_("Word"))
            self.set_title(_("Word"))

        shared.win.references_list_box.remove_all()
        for word_row in shared.win.lexicon_list_box:
            if word_row.word_dict["id"] in self.word_dict["references"]:
                shared.win.references_list_box.append(ReferenceRow(word_row, True))

        if shared.win.lexicon_split_view.get_collapsed():
            shared.win.lexicon_split_view.set_show_content(True)

        shared.win.set_word_rows_sensetiveness(True)

    def generate_word_type(self) -> None:
        """Toggles Word Type check buttons and sets subtitle for the Word Type expander row"""
        word_type_subtitle: str = ""
        for word_type, word_type_val in self.word_dict["types"].items():
            if word_type_val:
                getattr(shared.win, word_type + "_check_button").set_active(True)
                word_type_subtitle += enums.WordType[word_type.upper()] + ", "
            else:
                getattr(shared.win, word_type + "_check_button").set_active(False)

        if word_type_subtitle.endswith(", "):
            shared.win.word_type_expander_row.set_subtitle(word_type_subtitle[:-2])
        else:
            shared.win.word_type_expander_row.set_subtitle("")

    def remove_list_prop_on_backspace(self, text: Gtk.Text) -> None:
        """Removes one line from any expandable row

        Parameters
        ----------
        text : Gtk.Text
            A Gtk.Text to get text from and to get all necessary widgets from
        """
        if text.get_text_length() > 0:
            return

        row = text.get_ancestor(Adw.EntryRow)
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
                    del self.word_dict[attr_name][row_index]
                    if shared.schema.get_boolean("word-autosave"):
                        self.lexicon.save_lexicon()
                return

    def update_word(self, text: Gtk.Text) -> None:
        """Updates `self.word_dict` on change in any line from expandable rows

        Parameters
        ----------
        text : Gtk.Text
            A Gtk.Text to get text from and to get all necessary widgets from
        """
        row = text.get_ancestor(Adw.EntryRow)
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
                    self.word_dict[attr_name][row_index] = row.get_text()
                    try:
                        (
                            shared.win.loaded_word.set_subtitle(
                                self.word_dict["translations"][0]
                            )
                            if self.word_dict["translations"][0] != ""
                            else shared.win.loaded_word.set_subtitle(
                                _("No translation yet")
                            )
                        )
                    except IndexError:
                        self.set_subtitle(_("No translation yet"))
                    if shared.schema.get_boolean("word-autosave"):
                        self.lexicon.save_lexicon()
                return

    def add_list_prop(self, button: Gtk.Button) -> None:
        """Adds a new line to any expandable row

        Parameters
        ----------
        button : Gtk.Button
            A Gtk.Button to get all necessery widgets from
        """
        expander_row: Adw.ExpanderRow = button.get_ancestor(Adw.ExpanderRow)

        for attr_name, expander in (
            (attr.replace("_expander_row", ""), getattr(shared.win, attr))
            for attr in dir(shared.win)
            if attr.endswith("_expander_row")
        ):
            if expander is expander_row:
                new_row: Adw.EntryRow = Adw.EntryRow(
                    title=(
                        _("Translation")
                        if attr_name == "translations"
                        else _("Example")
                    )
                )
                for child in new_row.get_child():
                    for _item in child:
                        if isinstance(_item, Gtk.Text):
                            text = _item
                            break
                expander_row.add_row(new_row)
                self.word_dict[attr_name].append("")
                text.connect("changed", self.update_word)
                text.connect("backspace", self.remove_list_prop_on_backspace)
                if shared.schema.get_boolean("word-autosave"):
                    self.lexicon.save_lexicon()
                return

    def delete(self) -> None:
        """Deletes a word from the lexicon"""
        self.lexicon.data["words"].remove(self.word_dict)
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
        """Toggle `self.check_button` visibility on RMB click or long press"""
        if not self.check_button_revealer.get_reveal_child():
            shared.win.selection_mode_toggle_button.set_active(True)
            self.check_button.set_active(True)
        else:
            self.check_button.set_active(not self.check_button.get_active())

    @Gtk.Template.Callback()
    def on_check_button_toggled(self, button: Gtk.CheckButton) -> None:
        """Adds `self` to the `shared.win.selected_rows` for future deletion

        Parameters
        ----------
        button : Gtk.CheckButton
            A Gtk.CheckButton to decide to remove or add
        """
        if button.get_active():
            shared.win.selected_words.append(self)
        else:
            shared.win.selected_words.remove(self)

    def get_ref_count(self) -> None:
        """Sets the reference count label"""
        if self.ref_count > 0:
            self.refs_count_label_box.set_visible(True)
            self.refs_count_label.set_label(str(self.ref_count))
        else:
            self.refs_count_label_box.set_visible(False)

    @property
    def word(self) -> str:
        return self.word_dict["word"]

    @word.setter
    def word(self, word: str) -> None:
        self.word_dict["word"] = word
        self.set_title(word)
        if word != "":
            shared.win.word_nav_page.set_title(word)
        else:
            shared.win.word_nav_page.set_title(_("Word"))
            self.set_title(_("Word"))

        if shared.schema.get_boolean("word-autosave"):
            self.lexicon.save_lexicon()

    @property
    def pronunciation(self) -> str:
        return self.word_dict["pronunciation"]

    @pronunciation.setter
    def pronunciation(self, pronunciation: str) -> None:
        self.word_dict["pronunciation"] = pronunciation

        if shared.schema.get_boolean("word-autosave"):
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


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/ReferenceRow.ui")
class ReferenceRow(Adw.ActionRow):
    """Reference row widget

    Parameters
    ----------
    word_row : WordRow
        The word row to which this reference belongs.
    show_delete_button : bool
        Whether to show the delete button or not.
    """

    __gtype_name__ = "ReferenceRow"

    delete_button_box: Gtk.Box = gtc()

    def __init__(self, word_row: WordRow, show_delete_button: bool = False) -> None:
        super().__init__()
        self.delete_button_box.set_visible(show_delete_button)
        self.word_row: WordRow = word_row
        self.set_title(self.word_row.word)
        self.set_subtitle(self.word_row.translation)

    def refer_this_word(self, *_args) -> None:
        """Adds a reference to the word"""
        shared.win.loaded_word.word_dict["references"].append(
            self.word_row.word_dict["id"]
        )
        if shared.schema.get_boolean("word-autosave"):
            shared.win.loaded_lexicon.save_lexicon()
        shared.win.references_dialog_list_box.remove(self)

        shared.win.references_list_box.remove_all()
        for word_row in shared.win.lexicon_list_box:
            if (
                word_row.word_dict["id"]
                in shared.win.loaded_word.word_dict["references"]
            ):
                shared.win.references_list_box.append(ReferenceRow(word_row, True))

        if shared.win.references_dialog_list_box.get_row_at_index(0) is None:
            shared.win.references_dialog.close()
        shared.win.update_refs_count()

    def open_this_word(self, *_args) -> None:
        shared.win.lexicon_list_box.select_row(self.word_row)
        self.word_row.load_word()

    @Gtk.Template.Callback()
    def on_clicked(self, *_args) -> None:
        if shared.win.references_dialog is shared.win.props.visible_dialog:
            self.refer_this_word()
        else:
            self.open_this_word()

    @Gtk.Template.Callback()
    def on_delete_button_clicked(self, *_args) -> None:
        """Removes a reference to the word"""
        shared.win.loaded_word.word_dict["references"].remove(
            self.word_row.word_dict["id"]
        )

        if shared.schema.get_boolean("word-autosave"):
            shared.win.loaded_lexicon.save_lexicon()
        shared.win.references_list_box.remove(self)
        shared.win.update_refs_count()
