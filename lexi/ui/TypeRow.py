from gi.repository import Adw, Gtk

from lexi import enums, shared
from lexi.logging.logger import logger


class TypeRow(Adw.ActionRow):
    __gtype_name__ = "TypeRow"

    def __init__(self, type_: str, has_suffix: bool = True) -> "TypeRow":
        super().__init__(activatable=not has_suffix)
        self.type = type_
        self.__setup_ui(has_suffix)

    def __setup_ui(self, has_suffix: bool) -> None:
        if has_suffix:
            box = Gtk.Box(valign=Gtk.Align.CENTER)
            button = Gtk.Button(
                icon_name=enums.Icon.DELETE,
                tooltip_text=_("Delete this reference"),
                css_classes=["destructive-action"],
            )
            button.connect("clicked", self.__on_clicked)
            box.append(button)
            self.add_suffix(box)
        else:
            self.connect("activated", self.__on_activated)
        self.set_title(self.type)

    def __on_activated(self, *_args) -> None:
        logger.info(
            "Assigning word type “%s” to “%s”", self.type, shared.win.loaded_word.word
        )
        shared.win.loaded_word.add_type(self.type)
        shared.win.word_types_list_box.append(TypeRow(self.type))
        shared.win.assign_word_type_dialog_list_box.remove(self)
        shared.win.assign_word_type_dialog.close()

    def __on_clicked(self, *_args) -> None:
        # pylint: disable=import-outside-toplevel
        from lexi.ui.Preferences import LexiPreferences

        if not isinstance(dialog := shared.win.props.visible_dialog, LexiPreferences):
            shared.win.loaded_word.rm_type(self.type)
            logger.info(
                "“%s” type unassigned from “%s”", self.type, shared.win.loaded_word.word
            )
            shared.win.word_types_list_box.remove(self)
        else:
            logger.info("Deleting “%s” type", self.type)
            dialog.available_word_types_list_box.remove(self)
            shared.config["word-types"].remove(self.type)
            dialog.gen_word_types()
