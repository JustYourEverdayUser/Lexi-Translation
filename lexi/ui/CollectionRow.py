from gi.repository import Gtk, GObject

from lexi import shared


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/ui/CollectionRow.ui")
class CollectionRow(Gtk.Box):
    __gtype_name__ = "CollectionRow"

    gtc = Gtk.Template.Child
    expand_button: Gtk.ToggleButton = gtc()
    label: Gtk.Label = gtc()

    def __init__(self, name: str, path: str, expandable: bool = False) -> None:
        self._name: str = name
        self._path: str = path

        self._expanded: bool = False

        if not expandable:
            self.expand_button.set_visible(False)
            self.set_margin_start(4)

    @GObject.Property(type=str)
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @GObject.Property(type=str)
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, path: str) -> None:
        self._path = path

    @GObject.Property(type=bool)
    def expanded(self) -> bool:
        return self._expanded

    @expanded.setter
    def expanded(self, expanded: bool) -> None:
        self._expanded = expanded
