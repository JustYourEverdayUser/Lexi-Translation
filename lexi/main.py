import os
import sys

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

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

    # pylint: disable=unused-variable
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
                ("about", )
                # fmt: on
            }
        )

        sort_method = Gio.SimpleAction.new_stateful(
            "sort_method",
            GLib.VariantType.new("s"),
            sorting_method := GLib.Variant(
                "s", shared.state_schema.get_string("sort-method")
            ),
        )
        sort_method.connect("activate", shared.win.on_sorting_method_changed)
        shared.win.add_action(sort_method)

        sort_type = Gio.SimpleAction.new_stateful(
            "sort_type",
            GLib.VariantType.new("s"),
            sorting_type := GLib.Variant(
                "s", shared.state_schema.get_string("sort-type")
            ),
        )
        sort_type.connect("activate", shared.win.on_sorting_type_changed)
        shared.win.add_action(sort_type)

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

    # pylint: disable=line-too-long
    def on_about_action(self, *_args) -> None:
        dialog = Adw.AboutDialog.new_from_appdata(
            shared.PREFIX + "/" + shared.APP_ID + ".metainfo.xml", shared.VERSION
        )
        dialog.set_developers(("Dzheremi https://github.com/Dzheremi2",))
        dialog.set_designers(("Dzheremi https://github.com/Dzheremi2",))
        # Translators: Add Your Name, Your Name <your.email@example.com>, or Your Name https://your-site.com for it to show up in the About dialog. PLEASE, DON'T DELETE PREVIOUS TRANSLATORS CREDITS AND SEPARATE YOURSELF BY NEWLINE `\n` METASYMBOL
        dialog.set_translator_credits(_("translator-credits"))
        dialog.set_copyright("© 2025 Dzheremi")
        if shared.PREFIX.endswith("Devel"):
            dialog.set_version("Devel")

        dialog.present(shared.win)


def main(_version):
    """App entrypint"""
    if not os.path.exists(os.path.join(shared.data_dir, "lexicons")):
        os.mkdir(os.path.join(shared.data_dir, "lexicons"))

    shared.app = app = LexiApplication()

    return app.run(sys.argv)
