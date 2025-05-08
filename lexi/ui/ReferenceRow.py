from gi.repository import Adw, Gtk

from lexi import enums, shared
from lexi.logging.logger import logger
from lexi.utils.backend import Word


class ReferenceRow(Adw.ActionRow):
    __gtype_name__ = "ReferenceRow"

    def __init__(
        self, word: Word, has_suffix: bool = True
    ) -> "ReferenceRow":
        super().__init__(activatable=True)
        self.word = word
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
            self.connect("activated", self.__on_activated_go)
        else:
            self.set_activatable(True)
            self.connect("activated", self.__on_activated)
        self.set_title(self.word.word.replace("&rtl", ""))
        self.set_subtitle(
            self.word.translations[0].replace("&rtl", "")
            if self.word.translations[0]
            else _("No translation yet")
        )

    def __on_activated(self, *_args) -> None:
        shared.win.loaded_word.add_reference(self.word.id)
        shared.win.references_list_box.append(ReferenceRow(self.word))
        logger.info(
            "Word “%s” added to the “%s” references",
            self.word.word,
            shared.win.loaded_word.word,
        )
        if shared.win.references_dialog_list_box.get_row_at_index(0) is None:
            logger.debug("No more words to refer")
            shared.win.references_dialog.close()

    def __on_activated_go(self, *_args) -> None:
        # shared.win.set_property("loaded-word", self.word)
        for row in shared.win.lexicon_list_box:
            if row.word == self.word:
                shared.win.lexicon_list_box.select_row(row)
                break

    def __on_clicked(self, *_args) -> None:
        shared.win.loaded_word.rm_reference(self.word.id)
        logger.info(
            "“%s” remove from “%s” references",
            self.word.word,
            shared.win.loaded_word.word,
        )
        shared.win.references_list_box.remove(self)
        # shared.win.update_refs_count()
