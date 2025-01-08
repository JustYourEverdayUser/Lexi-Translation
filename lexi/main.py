import os
import sys

from gi.repository import Adw, Gdk, Gio, Gtk

from lexi import shared
from lexi.window import LexiWindow


class LexiApplication(Adw.Application):
    """Application class"""

    win: LexiWindow

    def __init__(self) -> None:
        super().__init__(
            application_id=shared.APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        theme.add_resource_path(shared.PREFIX + "/data/icons")

    def do_activate(self) -> None:  # pylint: disable=arguments-differ
        win = self.props.active_window  # pylint: disable=no-member
        if not win:
            shared.win = win = LexiWindow(application=self)

        shared.win.present()

        self.create_actions(
            {
                ("quit", ("<primary>q","<primary>w",)),
                ("toggle_sidebar", ("F9",), shared.win),
                ("toggle_search", ("<primary>f",), shared.win),
            }
        )

        shared.state_schema.bind(
            "window-width", shared.win, "default-width", Gio.SettingsBindFlags.DEFAULT
        )
        shared.state_schema.bind(
            "window-height", shared.win, "default-height", Gio.SettingsBindFlags.DEFAULT
        )
        shared.state_schema.bind(
            "window-maximized", shared.win, "maximized", Gio.SettingsBindFlags.DEFAULT
        )

    def on_quit_action(self, *_args) -> None:
        self.quit()

    def create_actions(self, actions: set) -> None:
        """Creates actions for provided scope with provided accels

        Args:
            actions (set): Actions in format ("name", ("accels",), scope)

            accels, scope: optional
        """
        for action in actions:
            simple_action = Gio.SimpleAction.new(action[0], None)

            scope = action[2] if action[2:3] else self
            simple_action.connect("activate", getattr(scope, f"on_{action[0]}_action"))

            if action[1:2]:
                self.set_accels_for_action(
                    f"app.{action[0]}" if scope == self else f"win.{action[0]}",
                    action[1],
                )
            scope.add_action(simple_action)


def main(_version):
    """App entrypint"""
    shared.app = app = LexiApplication()
    if not os.path.exists(shared.data_dir + "/collections.yaml"):
        file = open(shared.data_dir + "/collections.yaml", "x+")
        file.write("[]")
        file.close()

    return app.run(sys.argv)
