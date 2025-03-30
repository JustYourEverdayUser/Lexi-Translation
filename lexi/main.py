import os
import sys

from gi.repository import Adw, Gdk, Gio, Gtk

from lexi import shared
from lexi.ui.IPA import generate_table
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
            shared.win = LexiWindow(application=self)
            generate_table()

        self.create_actions(
            {
                # fmt: off
                ("quit",("<primary>q","<primary>w",),),
                ("toggle_sidebar",("F9",), shared.win),
                # fmt: on
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

        shared.win.present()

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
    if not os.path.exists(os.path.join(shared.data_dir, "lexicons")):
        os.mkdir(os.path.join(shared.data_dir, "lexicons"))

    shared.app = app = LexiApplication()

    return app.run(sys.argv)
