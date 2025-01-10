"""Medule with rows for Collections and Lexicons

   Supported rows: ::

        CollectionRow(label: str, icon: DictRowIcon, path_to_collection: str) ->\
 new row for the Collection
        LexiconRow(label: str, icon: DictRowIcon, path_to_lexicon: str) ->\
 new row for the Lexicon

   Enum classes: ::

        enum DictRowIcon:
            DictRowIcon.COLLECTION = "collection-symbolic"
            DictRowIcon.LEXICON = "lexicon-symbolic"
"""

from enum import Enum

from gi.repository import GObject, Gtk

from lexi import shared
from lexi.utils import Controllers as Ctrls


class DictRowIcon(Enum):
    COLLECTION: str = "collection-symbolic"
    LEXICON: str = "lexicon-symbolic"


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/DictRow.ui")
class DictRow(Gtk.Box):
    __gtype_name__ = "DictRow"

    gtc = Gtk.Template.Child
    icon: Gtk.Image = gtc()
    label_text: Gtk.Label = gtc()

    def __init__(self, label: str, icon: DictRowIcon) -> None:
        self.icon.set_from_icon_name(icon)
        self._label: str = label

    def invalidate_label(self) -> None:
        self.label_text.set_label(self.label)

    @GObject.Property(type=str)
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str) -> None:
        self._label = label


class CollectionRow(DictRow):
    __gtype_name__ = "collectionRow"

    def __init__(self, label: str, icon: DictRowIcon, path_to_collection: str) -> None:
        super().__init__(label, icon)
        self.collection_controller = Ctrls.CollectionController(path_to_collection)


class LexiconRow(DictRow):
    __gtype_name__ = "LexiconRow"

    def __init__(self, label: str, icon: DictRowIcon, path_to_lexicon: str) -> None:
        super().__init__(label, icon)
        self.lexicon_controller = Ctrls.LexiconController(path_to_lexicon)
