import os
import shutil

import yaml
from gi.repository import Adw, Gio, GObject, Gtk

from lexi import shared
from lexi.ui.PairRow import PairRow


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/LexiconRow.ui")
class LexiconRow(Gtk.Box):
    """Row for the lexicon

    Parameters
    ----------
    label: str
        label displayed on the row

    identificator: str
        id of the lexicon
    """

    __gtype_name__ = "LexiconRow"

    # Row
    label_text: Gtk.Label = Gtk.Template.Child()

    # Miscellaneous
    actions_menu_popover: Gtk.PopoverMenu = Gtk.Template.Child()
    entry_popover: Gtk.Popover = Gtk.Template.Child()
    entry_popover_entry_row: Adw.EntryRow = Gtk.Template.Child()

    def __init__(self, label: str, identificator: str):
        super().__init__()
        self._label: str = label
        self.id: str = identificator
        self.update_label()

        # Sets mouse gesture for detecting RMB click
        mouse_gesture = Gtk.GestureClick.new()
        mouse_gesture.set_button(3)
        mouse_gesture.connect("released", self.open_menu)

        # Adds new action group for popover menu working
        actions = Gio.SimpleActionGroup.new()
        rename_action = Gio.SimpleAction.new("rename", None)
        rename_action.connect("activate", self.rename)
        delete_action = Gio.SimpleAction.new("delete", None)
        delete_action.connect("activate", self.delete)
        actions.add_action(rename_action)
        actions.add_action(delete_action)
        self.insert_action_group("lexicon", actions)

        self.connect("notify::label", self.update_label)
        self.entry_popover_entry_row.connect("changed", self.warn_on_emtpy)
        self.add_controller(mouse_gesture)
        self.entry_popover.set_parent(self)
        self.actions_menu_popover.set_parent(self)

    def update_label(self, *_args) -> None:
        """Updates label displayed text"""
        self.label_text.set_label(self.label)

    def open_menu(self, *_args) -> None:
        """Shows actions menu for `self`"""
        if not self.actions_menu_popover.is_visible():
            self.actions_menu_popover.popup()
        else:
            self.actions_menu_popover.popdown()

    def rename(self, *_args) -> None:
        """Shows rename popover"""
        self.entry_popover_entry_row.set_show_apply_button(True)
        self.entry_popover_entry_row.set_title(_("Rename"))
        self.entry_popover_entry_row.set_text(self.label)
        self.entry_popover_entry_row.remove_css_class("error")
        self.entry_popover_entry_row.connect("apply", self.rename_callback)
        self.entry_popover.popup()

    def rename_callback(self, entry_row: Adw.EntryRow) -> None:
        """Renames `self` with new label provided by user

        Parameters
        ----------
        entry_row : Adw.EntryRow
            Adw.EntryRow to get new label from
        """
        if entry_row.get_text() != "":
            self.props.label = entry_row.get_text()
            self.update_data()
            self.entry_popover.popdown()
        else:
            self.entry_popover_entry_row.set_show_apply_button(False)
            self.entry_popover_entry_row.add_css_class("error")

    def delete(self, *_args) -> None:
        """Shows delete popup"""
        self.entry_popover_entry_row.set_show_apply_button(True)
        self.entry_popover_entry_row.set_title(_("Delete"))
        self.entry_popover_entry_row.set_tooltip_text(
            _("Write current lexicon name to delete it. This action cannot be reversed")
        )
        self.entry_popover_entry_row.set_text("")
        self.entry_popover_entry_row.connect("apply", self.delete_callback)
        self.entry_popover.popup()

    def delete_callback(self, entry_row: Adw.EntryRow) -> None:
        """Deletes `self` from sidebar and deletes respective lexicon hierarhy

        Parameters
        ----------
        entry_row : Adw.EntryRow
            Adw.EntryRow to get text from
        """
        if self.label == entry_row.get_text():  # pylint: disable=all
            self.entry_popover.popdown()
            for index, lexicon in enumerate(shared.data["lexico ns"]):
                if lexicon["id"] == self.id:
                    del shared.data["lexicons"][index]
                    shutil.rmtree(os.path.join(shared.data_dir, self.id))
                    shared.data_file.seek(0)
                    shared.data_file.truncate(0)
                    yaml.dump(
                        shared.data,
                        shared.data_file,
                        sort_keys=False,
                        encoding=None,
                        allow_unicode=True,
                    )
                    break
            shared.win.build_sidebar()
            del self
        else:
            self.entry_popover_entry_row.set_show_apply_button(False)
            self.entry_popover_entry_row.add_css_class("error")

    def update_data(self) -> None:
        """Updates label on the disk"""
        for index, lexicon in enumerate(shared.data["lexicons"]):
            if lexicon["id"] == self.id:
                shared.data["lexicons"][index]["name"] = self.label
                break
        shared.data_file.seek(0)
        shared.data_file.truncate(0)
        yaml.dump(
            shared.data,
            shared.data_file,
            sort_keys=False,
            encoding=None,
            allow_unicode=True,
        )

    def warn_on_emtpy(self, entry_row: Adw.EntryRow) -> None:
        """Warn user when the entry text is empty

        Parameters
        ----------
        entry_row : Adw.EntryRow
            Adw.EntryRow for warning
        """
        if entry_row.get_text() == "":
            self.entry_popover_entry_row.set_show_apply_button(False)
            self.entry_popover_entry_row.add_css_class("error")
        else:
            self.entry_popover_entry_row.set_show_apply_button(True)
            self.entry_popover_entry_row.remove_css_class("error")

    def load_lexicon(self) -> None:
        """Adds rows to the lexicon listbox on selection"""
        for pair in os.path.join(shared.data_dir, self.id, "resources"):
            shared.win.lexicon.append(
                PairRow(
                    tag=pair["tag"],
                    pair={pair["key"]: pair["value"]},
                    attachments=pair["attachments"],
                )
            )

    @GObject.Property(type=str)
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str) -> None:
        self._label = label
