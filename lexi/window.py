import os
import random
import string

from gi.repository import Adw, Gdk, Gio, GLib, Gtk

from lexi import enums, shared
from lexi.ui import widgets
from lexi.ui.Preferences import LexiPreferences


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "LexiWindow"

    gtc = Gtk.Template.Child

    # Status pages
    no_lexicons_yet: Adw.StatusPage = gtc()
    no_words_yet: Adw.StatusPage = gtc()
    lexicon_not_selected: Adw.StatusPage = gtc()

    # Toast overlay
    toast_overlay: Adw.ToastOverlay = gtc()

    # Navigation view and pages
    navigation_view: Adw.NavigationView = gtc()
    lexicon_nav_page: Adw.NavigationPage = gtc()
    word_nav_page: Adw.NavigationPage = gtc()

    # Overlay and split views
    overlay_split_view: Adw.OverlaySplitView = gtc()
    lexicon_split_view: Adw.NavigationSplitView = gtc()

    # Sidebar components
    lexicons_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicons_list_box: Gtk.ListBox = gtc()
    add_lexicon_popover: Gtk.Popover = gtc()
    add_lexicon_popover_entry_row: Adw.EntryRow = gtc()
    search_bar: Gtk.SearchBar = gtc()
    search_entry: Gtk.SearchEntry = gtc()

    # Lexicon-related components
    lexicon_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicon_list_box: Gtk.ListBox = gtc()
    lexicon_search_entry: Gtk.Entry = gtc()

    # Word-related components
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

    # References dialog
    references_dialog: Adw.Dialog = gtc()
    references_dialog_list_box: Gtk.ListBox = gtc()

    # Word Type filter dialog
    word_types_filter_dialog: Adw.Dialog = gtc()
    filter_dialog_list_box: Gtk.ListBox = gtc()
    noun_check_button_filter_dialog: Gtk.CheckButton = gtc()
    verb_check_button_filter_dialog: Gtk.CheckButton = gtc()
    adjective_check_button_filter_dialog: Gtk.CheckButton = gtc()
    adverb_check_button_filter_dialog: Gtk.CheckButton = gtc()
    pronoun_check_button_filter_dialog: Gtk.CheckButton = gtc()
    preposition_check_button_filter_dialog: Gtk.CheckButton = gtc()
    conjunction_check_button_filter_dialog: Gtk.CheckButton = gtc()
    interjection_check_button_filter_dialog: Gtk.CheckButton = gtc()
    article_check_button_filter_dialog: Gtk.CheckButton = gtc()
    idiom_check_button_filter_dialog: Gtk.CheckButton = gtc()
    clause_check_button_filter_dialog: Gtk.CheckButton = gtc()
    prefix_check_button_filter_dialog: Gtk.CheckButton = gtc()
    suffix_check_button_filter_dialog: Gtk.CheckButton = gtc()

    # Word type check buttons
    noun_check_button: Gtk.CheckButton = gtc()
    verb_check_button: Gtk.CheckButton = gtc()
    adjective_check_button: Gtk.CheckButton = gtc()
    adverb_check_button: Gtk.CheckButton = gtc()
    pronoun_check_button: Gtk.CheckButton = gtc()
    preposition_check_button: Gtk.CheckButton = gtc()
    conjunction_check_button: Gtk.CheckButton = gtc()
    interjection_check_button: Gtk.CheckButton = gtc()
    article_check_button: Gtk.CheckButton = gtc()
    idiom_check_button: Gtk.CheckButton = gtc()
    clause_check_button: Gtk.CheckButton = gtc()
    prefix_check_button: Gtk.CheckButton = gtc()
    suffix_check_button: Gtk.CheckButton = gtc()

    # IPA charset flow box
    # ipa_charset_flow_box: Gtk.FlowBox = gtc()

    # Keybindings overlay
    help_overlay: Gtk.ShortcutsWindow = gtc()

    translations_list_box: Gtk.ListBox
    examples_list_box: Gtk.ListBox
    word_types_list_box: Gtk.ListBox
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

        self.set_help_overlay(self.help_overlay)

        if enums.Schema.WORD_AUTOSAVE():
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
        self.lexicons_list_box.set_filter_func(self.filter_lexicons)
        self.lexicon_list_box.set_sort_func(self.sort_words)
        self.lexicon_list_box.set_filter_func(self.filter_words)
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
            (self.word_type_expander_row, "word_types"),
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
        """
        Handle key press events.

        Parameters
        ----------
        _controller : Gtk.EventControllerKey
            The key event controller that emitted this method.
        keyval : int
            The value of the pressed key.
        """
        if keyval == Gdk.KEY_Escape:
            # Handle Escape key press
            if self.selection_mode_toggle_button.get_active():
                self.selection_mode_toggle_button.set_active(False)

    def on_sorting_method_changed(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None:
        """
        Handle changes to the sorting method.

        Parameters
        ----------
        action : Gio.SimpleAction
            The action that triggered the change.
        state : GLib.Variant
            The new state of the sorting method.
        """
        action.set_state(state)
        self.sort_method = str(state).strip("'")
        self.lexicon_list_box.invalidate_sort()
        shared.state_schema.set_string("sort-method", self.sort_method)

    def on_sorting_type_changed(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None:
        """
        Handle changes to the sorting type.

        Parameters
        ----------
        action : Gio.SimpleAction
            The action that triggered the change.
        state : GLib.Variant
            The new state of the sorting type.
        """
        action.set_state(state)
        self.sort_type = str(state).strip("'")
        self.lexicon_list_box.invalidate_sort()
        shared.state_schema.set_string("sort-type", self.sort_type)

    # pylint: disable=no-else-return
    def sort_words(self, row1: widgets.WordRow, row2: widgets.WordRow) -> int:
        """
        Sort words in the list box based on the selected method and type.

        Parameters
        ----------
        row1 : widgets.WordRow
            The first word row to compare.
        row2 : widgets.WordRow
            The second word row to compare.

        Returns
        -------
        int
            -1 if row1 < row2, 1 if row1 > row2, 0 if they are equal.
        """
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

    def filter_lexicons(self, row: Gtk.ListBoxRow) -> bool:
        """
        Filter lexicons in the list box based on their names.

        Parameters
        ----------
        row : Gtk.ListBoxRow
            The row to filter.

        Returns
        -------
        bool
            True if the row matches the filter, False otherwise.
        """
        try:
            text: str = self.search_entry.get_text().lower()
            filtered: bool = text != "" and not (
                text in row.get_child().name.lower()
            )  # pylint: disable=superfluous-parens
            return not filtered
        except AttributeError:
            return True

    # pylint: disable=line-too-long
    def filter_words(self, row: widgets.WordRow) -> bool:
        """
        Filter words in the list box based on the search entry text and strict type filters.

        Parameters
        ----------
        row : widgets.WordRow
            a sortable WordRow

        Returns
        -------
        bool
            True if the word matches both the text and type filters, False otherwise.
        """
        try:
            # Get the search text
            text: str = self.lexicon_search_entry.get_text().lower()

            # Check if the search text matches the word or its translation
            matches_text = (
                text == ""
                or text in row.word.lower()
                or text in row.translation.lower()
            )

            # Get the filter types and check if any are enabled
            filter_types: dict = shared.config.get("filter-types", {})
            enabled_filters = {key for key, value in filter_types.items() if value}
            any_type_enabled = bool(enabled_filters)

            # Get the word's types
            word_types = {
                key for key, value in row.word_dict.get("types", {}).items() if value
            }

            # Check if the word's types strictly match the enabled filters
            matches_type = word_types == enabled_filters if any_type_enabled else True

            # Return True if the word matches both the text and type filters
            return matches_text and matches_type

        except (AttributeError, KeyError):
            return True  # Default to showing the word if there's an error

    @Gtk.Template.Callback()
    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggle the visibility of the sidebar."""
        self.overlay_split_view.set_show_sidebar(
            not self.overlay_split_view.get_show_sidebar()
        )

    def on_toggle_search_action(self, *_args) -> None:
        """
        Toggle the visibility of the search bar.
        """
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
        """
        Handle changes in the add lexicon entry row.

        Parameters
        ----------
        row : Adw.EntryRow
            The entry row that emitted this method.
        """
        if row.get_text() == "":
            row.add_css_class("error")
        else:
            if "error" in row.get_css_classes():
                row.remove_css_class("error")

    def on_add_lexicon_entry_activated(self, row: Adw.EntryRow) -> None:
        """
        Handle activation of the add lexicon entry row.

        Parameters
        ----------
        row : Adw.EntryRow
            The entry row that emitted this method.
        """
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
        """
        Build the sidebar with a list of lexicons.
        """
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
        """
        Handle selection of a lexicon.

        Parameters
        ----------
        _listbox : Gtk.ListBox
            The list box that emitted this method.
        row : Gtk.ListBoxRow
            The selected row.
        """
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
        """
        Update the reference count for all words in the lexicon list box.
        """
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
        """
        Handle the press of expandable rows' "add" buttons.

        Parameters
        ----------
        button : Gtk.Button
            The button that emitted this method.
        """
        self.loaded_word.add_list_prop(button)

    @Gtk.Template.Callback()
    def on_references_add_button_pressed(self, *_args) -> None:
        """
        Handle the press of the references add button.
        """
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
        """
        Show the add word dialog.
        """
        if self.loaded_lexicon is not None:
            self.loaded_lexicon.show_add_word_dialog()

    @Gtk.Template.Callback()
    def selection_mode_button_toggled(self, button: Gtk.ToggleButton) -> None:
        """
        Toggle selection mode.

        Parameters
        ----------
        button : Gtk.ToggleButton
            The toggle button that emitted this method.
        """
        self.set_selection_mode(button.get_active())

    def set_selection_mode(self, enabled: bool) -> None:
        """
        Set the selection mode of the words list box.

        Parameters
        ----------
        enabled : bool
            Whether to enable or disable selection mode.
        """
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
        """Delete selected words."""
        for row in self.selected_words.copy():
            self.selected_words.remove(row)
            row.delete()
        self.set_selection_mode(False)
        if self.lexicon_list_box.get_row_at_index(0) is None:
            self.lexicon_scrolled_window.set_child(self.no_words_yet)
            self.words_bottom_bar_revealer.set_reveal_child(False)
            self.set_word_rows_sensetiveness(False)

    def set_word_rows_sensetiveness(self, active: bool) -> None:
        """
        Set the sensitivity of word entry rows.

        Parameters
        ----------
        active : bool
            Whether the rows should be sensitive or not.
        """
        self.word_entry_row.set_sensitive(active)
        self.pronunciation_entry_row.set_sensitive(active)
        self.translations_expander_row.set_sensitive(active)
        self.word_type_expander_row.set_sensitive(active)
        self.examples_expander_row.set_sensitive(active)
        self.references_expander_row.set_sensitive(active)
        if not shared.schema.get_boolean("word-autosave"):
            self.save_word_button.set_sensitive(active)

    @Gtk.Template.Callback()
    def on_search_entry_changed(self, *_args) -> None:
        """
        Handle changes in the search entry.
        """
        self.lexicon_list_box.invalidate_filter()

    @Gtk.Template.Callback()
    def on_word_type_check_button_toggled(self, *_args) -> None:
        """
        Handle toggling of word type check buttons for the currently loaded word.
        """
        if not self.loaded_word:
            return  # Ensure a word is loaded before proceeding

        for attr in dir(self):
            if attr.endswith("_check_button"):
                button = getattr(self, attr)
                word_type = attr.replace("_check_button", "")
                if button.get_active():
                    self.loaded_word.word_dict["types"][word_type] = True
                else:
                    self.loaded_word.word_dict["types"][word_type] = False

        if enums.Schema.WORD_AUTOSAVE():
            self.loaded_lexicon.save_lexicon()

        self.loaded_word.generate_word_type()

    @Gtk.Template.Callback()
    def on_lexicon_search_entry_changed(self, *_args) -> None:
        """
        Handle changes in the lexicon search entry.
        """
        self.lexicons_list_box.invalidate_filter()

    @Gtk.Template.Callback()
    def on_filter_button_clicked(self, *_args) -> None:
        """
        Handle the click of the filter button.
        """
        for word_type, value in shared.config["filter-types"].items():
            getattr(self, word_type + "_check_button_filter_dialog").set_active(value)

        self.word_types_filter_dialog.present(self)

    # pylint: disable=no-member
    @Gtk.Template.Callback()
    def on_filter_check_button_toggled(self, *_args) -> None:
        """
        Handle toggling of filter check buttons.
        """
        if self.props.visible_dialog == self.word_types_filter_dialog:
            for (
                type_row
            ) in self.filter_dialog_list_box:  # pylint: disable=not-an-iterable
                for item in type_row:
                    for _item in item:
                        for __item in _item:
                            if isinstance(__item, Gtk.CheckButton):
                                button = __item
                                break
                for attr in dir(self):
                    if attr.endswith("_check_button_filter_dialog"):
                        if getattr(self, attr) == button:
                            word_type = attr.replace("_check_button_filter_dialog", "")
                            break
                if button.get_active():
                    shared.config["filter-types"][word_type] = True
                else:
                    shared.config["filter-types"][word_type] = False

            self.lexicon_list_box.invalidate_filter()

    @Gtk.Template.Callback()
    def on_reset_filter_button_clicked(self, *_args) -> None:
        """
        Handle the click of the reset filter button.
        """
        for attr in dir(self):
            if attr.endswith("_check_button_filter_dialog"):
                getattr(self, attr).set_active(False)

    def on_show_preferences_action(self, *_args) -> None:
        """Presents Preferences dialog to user"""
        if LexiPreferences.opened:
            return
        preferences = LexiPreferences()
        preferences.present(self)

    @Gtk.Template.Callback()
    def on_save_word_button_clicked(self, *_args) -> None:
        """Perform loaded lexicon save and inform user"""
        self.loaded_word.lexicon.save_lexicon()
        self.toast_overlay.add_toast(Adw.Toast(title=_("Word saved"), timeout=2))
