from typing import Literal, Tuple

from gi.repository import Adw, GObject, Gtk

from lexi import shared


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/PairRow.ui")
class PairRow(Adw.ActionRow):
    """Key-value pair row

    Parameters
    ----------
    tag: str
        tag assigned to the pair

    pair: dict
        a key-value itself

    attachments: list
        list of true/false attachments. Each is true or false, controlling displaying\
 of the respective icon

    `Attachments` ::

        0 -> attachment_document
        1 -> attachment_audio
        2 -> attachment_video
        3 -> attachment_text

    """

    __gtype_name__ = "PairRow"

    gtc = Gtk.Template.Child

    set_tag_button: Gtk.Button = gtc()
    selection_button: Gtk.CheckButton = gtc()
    attachments_box: Gtk.Box = gtc()
    attachment_document: Gtk.Image = gtc()
    attachment_audio: Gtk.Image = gtc()
    attachment_video: Gtk.Image = gtc()
    attachment_text: Gtk.Image = gtc()

    attachments_dict: dict = {
        0: attachment_document,
        1: attachment_audio,
        2: attachment_video,
        3: attachment_text,
    }

    def __init__(self, tag: str, pair: dict, attachments: list) -> None:
        super().__init__()
        self.key: str = pair["key"]
        self.value: str = pair["value"]
        self.tag: str = tag
        self._attachments: list = attachments

        if self.value != "":
            # Checks if there is no value to disable its icon
            self.attachments[3] = False

        self.connect("notify::attachments", self.invalidate_attachments_icons)
        self.invalidate_attachments_icons()

    def invalidate_attachments_icons(self) -> None:
        for state, index in enumerate(self.attachments):
            self.attachments_dict[index].set_visible(state)

    @GObject.Property
    def attachments(self) -> list:
        return self._attachments

    @attachments.setter
    def attachments(
        self, list_of_pairs: Tuple[Literal[0, 1, 2, 3], bool]
    ) -> None:
        self._attachments[list_of_pairs[0]] = list_of_pairs[2]
