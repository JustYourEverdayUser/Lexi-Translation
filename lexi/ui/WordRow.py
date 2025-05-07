from typing import Self

from gi.repository import Adw, Gtk

from lexi import shared
from lexi.logging.logger import logger
from lexi.utils.backend import Word

gtc = Gtk.Template.Child  # pylint: disable=invalid-name


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/WordRow.ui")
class WordRow(Adw.ActionRow):
    """Word row class
    
    Parameters
    ----------
    word : Word
        a Word class object representing one word from the Lexicon
    """

    __gtype_name__ = "WordRow"

    # Word-related components
    title_label: Gtk.Label = gtc()
    subtitle_label: Gtk.Label = gtc()
    tags_box: Adw.WrapBox = gtc()
    check_button_revealer: Gtk.Revealer = gtc()
    check_button: Gtk.CheckButton = gtc()
    refs_count_label_box: Gtk.Box = gtc()
    refs_count_label: Gtk.Label = gtc()
    tag_alert_dialog: Adw.AlertDialog = gtc()
    tag_alert_dialog_entry: Gtk.Entry = gtc()

    def __init__(self, word: Word) -> "WordRow":
        super().__init__()
        self.word = word
        self.title = word.word.replace("&rtl", "")
        try:
            self.subtitle = word.translations[0].replace("&rtl", "")
        except IndexError:
            self.subtitle = _("No translation yet")

        self.__generate_tag_chips()

        self.word.connect("notify::word", self.__reactivity)
        self.word.connect("tags-changed", self.__reactivity)

    def __reactivity(self, *_args) -> None:
        self.title = self.word.word
        try:
            self.subtitle = self.word.translations[0]
        except IndexError:
            _("No translation yet")

        self.__generate_tag_chips()

    def __generate_tag_chips(self) -> None:
        for _tag in self.tags_box:  # pylint: disable=not-an-iterable
            self.tags_box.remove(_tag)
        if self.word.tags != []:

            def __clicked(_button: Gtk.Button, tag: str) -> None:
                current_text = shared.win.lexicon_search_entry.get_text()
                if not current_text.startswith("#") and current_text != "":
                    return
                logger.info(
                    "Searching for words with tag “%s”", current_text + f"#{tag}"
                )
                shared.win.lexicon_search_entry.set_text(f"{current_text}#{tag}")

            def __rmb_clicked(
                _button: Gtk.Button,
                _gesture: Gtk.GestureClick,
                _x: float,
                _y: float,
                tag: str,
            ) -> None:
                self.word.tags.remove(tag)
                logger.info("Tag “#%s” removed from “%s”", tag, self.word.word)
                for _tag in self.tags_box:  # pylint: disable=not-an-iterable
                    self.tags_box.remove(_tag)
                self.__generate_tag_chips()

            for tag in self.word.tags:
                button = Gtk.Button(
                    label=f"#{tag}",
                    valign=Gtk.Align.CENTER,
                    css_classes=["pill", "small"],
                    # pylint: disable=line-too-long
                    tooltip_text=_(
                        "Click LMB to search words with this tag\nClick RMB to remove this tag"
                    ),
                )
                button.connect("clicked", __clicked, tag)
                rmb = Gtk.GestureClick(button=3)
                rmb.connect("released", __rmb_clicked, tag)
                button.add_controller(rmb)
                self.tags_box.append(button)

    @property
    def title(self) -> str:
        """The `self` title"""
        return self.title_label.get_label()

    @title.setter
    def title(self, word: str) -> None:
        """The `self` title"""
        self.title_label.set_label(word)

    @property
    def subtitle(self) -> str:
        """The `self` subtitle"""
        return self.subtitle_label.get_label()

    @subtitle.setter
    def subtitle(self, translation: str) -> None:
        """The `self` subtitle"""
        self.subtitle_label.set_label(translation)
