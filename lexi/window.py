import os
import random
import string

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from lexi import shared
from lexi.ui import widgets


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "LexiWindow"

    gtc = Gtk.Template.Child

    # Define UI components as class attributes
    toast_overlay: Adw.ToastOverlay = gtc()
    no_lexicons_yet: Adw.StatusPage = gtc()
    no_words_yet: Adw.StatusPage = gtc()
    lexicon_not_selected: Adw.StatusPage = gtc()

    add_lexicon_popover: Gtk.Popover = gtc()
    add_lexicon_popover_entry_row: Adw.EntryRow = gtc()

    lexicons_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicons_list_box: Gtk.ListBox = gtc()
    lexicon_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicon_list_box: Gtk.ListBox = gtc()
    navigation_view: Adw.NavigationView = gtc()
    overlay_split_view: Adw.OverlaySplitView = gtc()
    lexicon_split_view: Adw.NavigationSplitView = gtc()
    search_bar: Gtk.SearchBar = gtc()
    search_entry: Gtk.SearchEntry = gtc()

    lexicon_nav_page: Adw.NavigationPage = gtc()
    word_nav_page: Adw.NavigationPage = gtc()

    word_entry_row: Adw.EntryRow = gtc()
    pronunciation_entry_row: Adw.EntryRow = gtc()
    translations_expander_row: Adw.ExpanderRow = gtc()
    word_type_expander_row: Adw.ExpanderRow = gtc()
    examples_expander_row: Adw.ExpanderRow = gtc()
    references_expander_row: Adw.ExpanderRow = gtc()
    save_word_button: Gtk.Button = gtc()
    selection_mode_toggle_button: Gtk.ToggleButton = gtc()
    delete_selected_words_button: Gtk.Button = gtc()
    delete_selected_words_button_revealer: Gtk.Revealer = gtc()
    words_bottom_bar_revealer: Gtk.Revealer = gtc()
    references_dialog: Adw.Dialog = gtc()
    references_dialog_list_box: Gtk.ListBox = gtc()

    ipa_charset_flow_box: Gtk.FlowBox = gtc()

    translations_list_box: Gtk.ListBox
    examples_list_box: Gtk.ListBox
    references_list_box: Gtk.ListBox

    sort_method: str = shared.state_schema.get_string("sort-method")
    sort_type: str = shared.state_schema.get_string("sort-type")

    # Variables to store the currently loaded lexicon and word
    loaded_lexicon: widgets.LexiconRow = None
    loaded_word: widgets.WordRow = None
    selected_words: list = []

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Add a CSS class for development mode
        if shared.APP_ID.endswith("Devel"):
            self.add_css_class("devel")

        if shared.schema.get_boolean("word-autosave"):
            self.save_word_button.remove_css_class("suggested-action")
            self.save_word_button.set_tooltip_text(_("Word autosave is enabled"))
            self.save_word_button.set_sensitive(False)
        else:
            self.save_word_button.add_css_class("suggested-action")
            self.save_word_button.set_sensitive(True)

        if self.lexicon_list_box.get_selected_row() is None:
            self.lexicon_scrolled_window.set_child(self.lexicon_not_selected)

        key_kapture_controller = Gtk.EventControllerKey()
        self.add_controller(key_kapture_controller)

        # Connections
        self.lexicon_list_box.set_sort_func(self.sort_words)
        self.search_bar.connect_entry(self.search_entry)
        self.add_lexicon_popover_entry_row.connect(
            "changed", self.on_add_lexicon_entry_changed
        )
        self.add_lexicon_popover_entry_row.connect(
            "apply", self.on_add_lexicon_entry_activated
        )
        key_kapture_controller.connect("key-pressed", self.on_key_pressed)

        # Extracts ListBoxes from expander rows
        for epxander_row in (
            (self.translations_expander_row, "translations"),
            (self.examples_expander_row, "examples"),
            (self.references_expander_row, "references"),
        ):
            for item in epxander_row[0].get_child():
                for _item in item:
                    if isinstance(_item, Gtk.ListBox):
                        setattr(self, epxander_row[1] + "_list_box", _item)
                        break

        # Build the sidebar with lexicons
        self.build_sidebar()
        self.set_word_rows_sensetiveness(False)

    def on_key_pressed(
        self, _controller: Gtk.EventControllerKey, keyval: int, *_args
    ) -> None:
        """Emits on any key press

        Parameters
        ----------
        _controller : Gtk.EventControllerKey
            Gtk.EventControllerKey emitted this method
        keyval : int
            pressed key value
        """
        if keyval == Gdk.KEY_Escape:
            # Handle Escape key press
            if self.selection_mode_toggle_button.get_active():
                self.selection_mode_toggle_button.set_active(False)

    def on_sorting_method_changed(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None:
        action.set_state(state)
        self.sort_method = str(state).strip("'")
        self.lexicon_list_box.invalidate_sort()
        shared.state_schema.set_string("sort-method", self.sort_method)

    def on_sorting_type_changed(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None:
        action.set_state(state)
        self.sort_type = str(state).strip("'")
        self.lexicon_list_box.invalidate_sort()
        shared.state_schema.set_string("sort-type", self.sort_type)

    # pylint: disable=no-else-return
    def sort_words(self, row1: widgets.WordRow, row2: widgets.WordRow) -> int:
        """Sorts words in the list box based on the selected method and type"""
        sortable1: str | int
        sortable2: str | int

        if self.sort_type == "word":
            sortable1 = row1.word.lower()
            sortable2 = row2.word.lower()
        elif self.sort_type == "first_trnslt":
            sortable1 = row1.translation.lower()
            sortable2 = row2.translation.lower()
        else:
            sortable1 = row1.ref_count
            sortable2 = row2.ref_count

        if self.sort_method == "up":
            if sortable1 > sortable2:
                return 1
            elif sortable1 < sortable2:
                return -1
            else:
                return 0
        else:
            if sortable1 < sortable2:
                return 1
            elif sortable1 > sortable2:
                return -1
            else:
                return 0

    @Gtk.Template.Callback()
    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggle the visibility of the sidebar."""
        self.overlay_split_view.set_show_sidebar(
            not self.overlay_split_view.get_show_sidebar()
        )

    def on_toggle_search_action(self, *_args) -> None:
        """Toggle the search bar visibility."""
        if self.overlay_split_view.get_show_sidebar():
            search_bar = self.search_bar
            search_entry = self.search_entry
        else:
            return

        # Toggle search mode and focus the search entry if enabled
        search_bar.set_search_mode(not (search_mode := search_bar.get_search_mode()))

        if not search_mode:
            self.set_focus(search_entry)

        search_entry.set_text("")

    def on_add_lexicon_entry_changed(self, row: Adw.EntryRow) -> None:
        """Handle changes in the add lexicon entry row."""
        if row.get_text() == "":
            row.add_css_class("error")
        else:
            if "error" in row.get_css_classes():
                row.remove_css_class("error")

    def on_add_lexicon_entry_activated(self, row: Adw.EntryRow) -> None:
        """Handle activation of the add lexicon entry row."""
        if row.get_text() == "":
            self.add_lexicon_popover.popdown()
            return

        # Generate a unique random ID for the new lexicon
        while True:
            random_id: str = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=16)
            )
            if not os.path.exists(
                os.path.join(shared.data_dir, "lexicons", random_id) + ".yaml"
            ):
                break

        # Create a new lexicon file with the generated ID
        file = open(
            os.path.join(shared.data_dir, "lexicons", random_id) + ".yaml",
            "x+",
            encoding="utf-8",
        )
        file.write(f"name: {row.get_text()}\nid: {random_id}\nwords: []")
        file.flush()

        # Reset the popover and rebuild the sidebar
        self.add_lexicon_popover.popdown()
        self.add_lexicon_popover_entry_row.set_text("")
        self.build_sidebar()

    def build_sidebar(self) -> None:
        """Build the sidebar with a list of lexicons."""
        if os.listdir(os.path.join(shared.data_dir, "lexicons")) != []:
            # Clear the list box and populate it with lexicons
            self.lexicons_list_box.remove_all()
            lexicon_rows: list = []
            for file in os.listdir(os.path.join(shared.data_dir, "lexicons")):
                lexicon_rows.append(
                    widgets.LexiconRow(os.path.join(shared.data_dir, "lexicons", file))
                )
            lexicon_rows.sort(key=lambda row: row.name)
            for row in lexicon_rows:
                self.lexicons_list_box.append(row)
            self.lexicons_scrolled_window.set_child(self.lexicons_list_box)
        else:
            # Show a placeholder if no lexicons are available
            self.lexicons_scrolled_window.set_child(self.no_lexicons_yet)

    @Gtk.Template.Callback()
    def on_lexicon_selected(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        """Handle selection of a lexicon."""
        self.lexicon_list_box.remove_all()
        if len(row.get_child().data["words"]) != 0:
            # Populate the list box with words from the selected lexicon
            for word in row.get_child().data["words"]:
                self.lexicon_list_box.append(widgets.WordRow(word, row.get_child()))
            self.lexicon_scrolled_window.set_child(self.lexicon_list_box)
            self.words_bottom_bar_revealer.set_reveal_child(True)
        else:
            # Show a placeholder if no words are available
            self.lexicon_scrolled_window.set_child(self.no_words_yet)
            self.words_bottom_bar_revealer.set_reveal_child(False)
        self.update_refs_count()
        self.lexicon_nav_page.set_title(row.get_child().name)
        self.loaded_lexicon = row.get_child()

    def update_refs_count(self) -> None:
        """Update the reference count for all words in the lexicon list box"""
        for word_row in self.lexicon_list_box:  # pylint: disable=not-an-iterable
            word_row.get_ref_count()

    @Gtk.Template.Callback()
    def on_word_entry_changed(self, row: Adw.EntryRow) -> None:
        """Emits when the word entry is changed

        Parameters
        ----------
        row : Adw.EntryRow
            Adw.EntryRow emitted this method
        """
        self.loaded_word.word = row.get_text()

    @Gtk.Template.Callback()
    def on_pronunciation_entry_changed(self, row: Adw.EntryRow) -> None:
        """Emits when the pronunciation entry is changed

        Parameters
        ----------
        row : Adw.EntryRow
            Adw.EntryRow emitted this method
        """
        self.loaded_word.pronunciation = row.get_text()

    @Gtk.Template.Callback()
    def on_word_list_prop_button_pressed(self, button: Gtk.Button) -> None:
        """When any of expandable rows "add" buttons pressed

        Parameters
        ----------
        button : Gtk.Button
            Gtk.Button emitted this method
        """
        self.loaded_word.add_list_prop(button)

    @Gtk.Template.Callback()
    def on_references_add_button_pressed(self, *_args) -> None:
        """When the references add button is pressed"""
        if self.loaded_lexicon.data["words"] == [] or len(
            self.loaded_lexicon.data["words"]
        ) - 1 == len(self.loaded_word.word_dict["references"]):
            self.toast_overlay.add_toast(
                Adw.Toast.new(
                    _("You have already referenced all words"),
                )
            )
            return

        self.references_dialog_list_box.remove_all()
        for word_row in self.lexicon_list_box:  # pylint: disable=not-an-iterable
            if (word_row.word_dict["id"] != self.loaded_word.word_dict["id"]) and (
                word_row.word_dict["id"] not in self.loaded_word.word_dict["references"]
            ):
                self.references_dialog_list_box.append(widgets.ReferenceRow(word_row))
        self.references_dialog.present(self)

    @Gtk.Template.Callback()
    def on_add_word_action(self, *_args) -> None:
        """Shows the add word dialog"""
        self.loaded_lexicon.show_add_word_dialog()

    @Gtk.Template.Callback()
    def selection_mode_button_toggled(self, button: Gtk.ToggleButton) -> None:
        """Toggled selection mode

        Parameters
        ----------
        button : Gtk.ToggleButton
            Gtk.ToggleButton emitted this method
        """
        self.set_selection_mode(button.get_active())

    def set_selection_mode(self, enabled: bool) -> None:
        """Set the selection mode of the words list box."""
        # Gratefully "stolen" from
        # https://github.com/flattool/warehouse/blob/0a18e5d81b8b06e45bf493b3ff31c12edbd36869/src/packages_page/packages_page.py#L226
        if enabled:
            self.lexicon_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        else:
            self.lexicon_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.selection_mode_toggle_button.set_active(enabled)

        i = 0
        row: widgets.WordRow
        while row := self.lexicon_list_box.get_row_at_index(i):
            i += 1
            row.check_button.set_active(False)
            row.check_button_revealer.set_reveal_child(enabled)
        self.delete_selected_words_button_revealer.set_reveal_child(enabled)

    @Gtk.Template.Callback()
    def on_delete_selected_words_action(self, *_args) -> None:
        """Delete selected words"""
        for row in self.selected_words:
            self.selected_words.remove(row)
            row.delete()
        self.set_selection_mode(False)
        if self.lexicon_list_box.get_row_at_index(0) is None:
            self.lexicon_scrolled_window.set_child(self.no_words_yet)
            self.words_bottom_bar_revealer.set_reveal_child(False)
            self.set_word_rows_sensetiveness(False)

    def set_word_rows_sensetiveness(self, active: bool) -> None:
        """Set the sensitivity of word entry rows

        Parameters
        ----------
        active : bool
            should the rows be sensetive or not
        """
        self.word_entry_row.set_sensitive(active)
        self.pronunciation_entry_row.set_sensitive(active)
        self.translations_expander_row.set_sensitive(active)
        self.word_type_expander_row.set_sensitive(active)
        self.examples_expander_row.set_sensitive(active)
        self.references_expander_row.set_sensitive(active)
        if not shared.schema.get_boolean("word-autosave"):
            self.save_word_button.set_sensitive(active)
