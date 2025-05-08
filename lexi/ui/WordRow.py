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

    title_label: Gtk.Label = gtc()
    subtitle_label: Gtk.Label = gtc()
    tags_box: Adw.WrapBox = gtc()
    check_button_revealer: Gtk.Revealer = gtc()
    check_button: Gtk.CheckButton = gtc()
    refs_count_label_box: Gtk.Box = gtc()
    refs_count_label: Gtk.Label = gtc()
    tag_alert_dialog: Adw.AlertDialog = gtc()
    tag_alert_dialog_entry: Gtk.Entry = gtc()

    __tmp_tags_buttons = []  # Since Adw.FlowBox doesn't have a remove_all() method

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
        self.word.connect("translations-changed", self.__reactivity)

    @Gtk.Template.Callback()
    def on_add_tag_button_clicked(self, *_args) -> None:
        logger.debug("Showing tag addition alert dialog for “%s”", self.word.word)
        self.tag_alert_dialog_entry.set_text("")
        self.tag_alert_dialog.present(shared.win)
        self.tag_alert_dialog_entry.grab_focus()

    @Gtk.Template.Callback()
    def on_tag_alert_dialog_entry_changed(self, entry: Gtk.Entry) -> None:
        if (
            "#" in entry.get_text()
            or entry.get_text().lower() in self.word.tags
            or " " in entry.get_text().strip()
        ):
            entry.add_css_class("error")
        else:
            if "error" in entry.get_css_classes():
                entry.remove_css_class("error")

    @Gtk.Template.Callback()
    def on_tag_entry_activated(self, *_args) -> None:
        self.on_tag_alert_dialog_response(
            _alert_dialog=self.tag_alert_dialog, response="add"
        )
        self.tag_alert_dialog.close()

    @Gtk.Template.Callback()
    def on_tag_alert_dialog_response(
        self, _alert_dialog: Adw.AlertDialog, response: str
    ) -> None:
        if response == "add":
            tag = self.tag_alert_dialog_entry.get_text().lower().strip()
            if "#" in tag or " " in tag or tag == "":
                logger.warning("Tag cannot contain spaces or '#'")
                raise AttributeError("Tag cannot contain spaces or '#'")

            if tag in self.word.tags:
                logger.warning("Tag already exists")
                raise AttributeError("Tag already exists")

            self.word.add_tag(tag)
            self.__generate_tag_chips()
            logger.info("Tag “#%s” added to “%s”", tag, self.word.word)
        else:
            logger.debug("Tag addition cancelled")

    def __reactivity(self, *_args) -> None:
        self.title = self.word.word.replace("&rtl", "")
        try:
            self.subtitle = self.word.translations[0].replace("&rtl", "")
        except IndexError:
            _("No translation yet")

        self.__generate_tag_chips()

    def __generate_tag_chips(self) -> None:
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
                _gesture: Gtk.GestureClick,
                _n_press: int,
                _x: float,
                _y: float,
                tag: str,
            ) -> None:
                self.word.rm_tag(tag)
                logger.info("Tag “#%s” removed from “%s”", tag, self.word.word)

                for button in self.__tmp_tags_buttons:
                    if button.get_label() == f"#{tag}":
                        self.tags_box.remove(button)
                        self.__tmp_tags_buttons.remove(button)
                        break

            for _tag in self.__tmp_tags_buttons:
                if _tag.get_parent() == self.tags_box:
                    self.tags_box.remove(_tag)
            self.__tmp_tags_buttons.clear()

            for tag in self.word.tags:
                button = Gtk.Button(
                    label=f"#{tag}",
                    valign=Gtk.Align.CENTER,
                    css_classes=["pill", "small"],
                    tooltip_text=_(
                        "Click LMB to search words with this tag\nClick RMB to remove this tag"
                    ),
                )
                self.__tmp_tags_buttons.append(button)
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
