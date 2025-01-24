import os
import random
import string
import sys

import yaml
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

        self.create_actions(
            {
                # fmt: off
                ("quit",("<primary>q","<primary>w",),),
                ("toggle_sidebar", ("F9",), shared.win),
                ("toggle_search", ("<primary>f",), shared.win),
                ("open_lexicon_actions_menu", ("F10",), shared.win)
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

    def add_lexicon(self, name: str) -> None:
        """Adds new lexicon and saves it to the local storage

        Parameters
        ----------
        name : str
            name of the new lexicon
        """
        while True:
            random_id: str = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=16)
            )
            if not os.path.exists(os.path.join(shared.data_dir, random_id)):
                break

        shared.data["lexicons"].append({"name": name, "id": random_id})
        os.makedirs(
            os.path.join(shared.data_dir, random_id, "resources"), exist_ok=True
        )
        with open(
            os.path.join(shared.data_dir, random_id, "lexicon.yaml"),
            "x+",
            encoding="utf-8",
        ) as file:
            file.write("[]")
        shared.data_file.seek(0)
        shared.data_file.truncate(0)
        yaml.dump(
            shared.data,
            shared.data_file,
            sort_keys=False,
            encoding=None,
            allow_unicode=True,
        )
        shared.win.name_lexicon_entry.set_text("")
        shared.win.name_lexicon_entry_2.set_text("")
        shared.win.add_lexicon_popover.popdown()
        shared.win.add_lexicon_popover_2.popdown()
        shared.win.build_sidebar()

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
    if not os.path.exists(shared.data_dir + "/lexicons.yaml"):
        file = open(shared.data_dir + "/lexicons.yaml", "x+")
        file.write("lexicons: []\nlast-lexicon: null\ndata-version: 1")
        file.close()

    shared.data_file = open(shared.data_dir + "/lexicons.yaml", "r+", encoding="utf-8")
    shared.data = yaml.safe_load(shared.data_file)

    shared.app = app = LexiApplication()

    return app.run(sys.argv)
