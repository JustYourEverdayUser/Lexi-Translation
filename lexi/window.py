from gi.repository import Adw, Gdk, Gio, GLib, GObject, Gtk

from lexi import enums, shared
from lexi.logging.logger import logger
from lexi.ui.LexiconRow import LexiconRow
from lexi.ui.Preferences import LexiPreferences
from lexi.ui.ReferenceRow import ReferenceRow
from lexi.ui.TypeRow import TypeRow
from lexi.ui.WordRow import WordRow
from lexi.utils.backend import Lexicon, Word
from lexi.utils.sort_filter import filter_lexicons, filter_words, sort_words


@Gtk.Template(resource_path=shared.PREFIX + "/gtk/window.ui")
class LexiWindow(Adw.ApplicationWindow):
    """App window class"""

    __gtype_name__ = "LexiWindow"

    gtc = Gtk.Template.Child

    # Status pages
    no_lexicons_yet: Adw.StatusPage = gtc()
    no_words_yet: Adw.StatusPage = gtc()
    status_page_add_word_button: Gtk.Button = gtc()
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
    add_lexicon_alert_dialog: Adw.AlertDialog = gtc()
    add_lexicon_entry: Gtk.Entry = gtc()
    search_bar: Gtk.SearchBar = gtc()
    search_entry: Gtk.SearchEntry = gtc()

    # Lexicon-related components
    lexicon_scrolled_window: Gtk.ScrolledWindow = gtc()
    lexicon_list_box: Gtk.ListBox = gtc()
    lexicon_search_entry: Gtk.Entry = gtc()

    # Word-related components
    sort_menu_button: Gtk.MenuButton = gtc()
    word_entry_row: Adw.EntryRow = gtc()
    pronunciation_entry_row: Adw.EntryRow = gtc()
    translations_expander_row: Adw.ExpanderRow = gtc()
    word_type_expander_row: Adw.ExpanderRow = gtc()
    examples_expander_row: Adw.ExpanderRow = gtc()
    references_expander_row: Adw.ExpanderRow = gtc()
    selection_mode_toggle_button: Gtk.ToggleButton = gtc()
    delete_selected_words_button: Gtk.Button = gtc()
    delete_selected_words_button_revealer: Gtk.Revealer = gtc()
    words_bottom_bar_revealer: Gtk.Revealer = gtc()
    add_word_button: Gtk.Button = gtc()
    assign_word_type_dialog: Adw.Dialog = gtc()
    assign_word_type_dialog_list_box: Gtk.ListBox = gtc()
    filter_button: Gtk.Button = gtc()
    filter_dialog: Adw.Dialog = gtc()
    filter_dialog_list_box: Gtk.ListBox = gtc()

    # References dialog
    references_dialog: Adw.Dialog = gtc()
    references_dialog_list_box: Gtk.ListBox = gtc()

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
    _loaded_lexicon: Lexicon = None
    _loaded_word: Word = None
    selected_words: list = []

    _state: enums.WindowState = None

    def __init__(self, **kwargs) -> "LexiWindow":
        super().__init__(**kwargs)
        # Add a CSS class for development mode
        if shared.APP_ID.endswith("Devel"):
            logger.debug("Enabling development mode decorations")
            self.add_css_class("devel")

        logger.debug("Setting keybinding window")
        self.set_help_overlay(self.help_overlay)

        if self.lexicon_list_box.get_selected_row() is None:
            self.lexicon_scrolled_window.set_child(self.lexicon_not_selected)

        key_kapture_controller = Gtk.EventControllerKey()
        self.add_controller(key_kapture_controller)

        # Connections
        self.lexicons_list_box.set_filter_func(filter_lexicons)
        self.lexicon_list_box.set_sort_func(sort_words)
        self.lexicon_list_box.set_filter_func(filter_words)
        self.search_bar.connect_entry(self.search_entry)
        key_kapture_controller.connect("key-pressed", self.__on_key_pressed)
        self.connect("notify::loaded-lexicon", self.__on_lexicon_changed)
        self.connect("notify::loaded-word", self.__on_word_changed)
        self.connect("notify::state", self.__on_state_change)

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

        # Extract `Gtk.Text`s from various entry rows
        for child in self.word_entry_row.get_child():
            for _item in child:
                if isinstance(_item, Gtk.Text):
                    self.word_entry_row_text = _item
                    self.word_entry_row_text.connect(
                        "direction-changed", self.__on_word_direction_changed
                    )

        for child in self.pronunciation_entry_row.get_child():
            for _item in child:
                if isinstance(_item, Gtk.Text):
                    self.pronunciation_entry_row_text = _item

        self.__on_state_change(state_=enums.WindowState.EMPTY)
        self.build_sidebar()

    def build_sidebar(self) -> None:
        """Builds the sidebar with lexicons"""
        logger.debug("Building sidebar")
        self.lexicons_list_box.remove_all()
        # pylint: disable=protected-access
        if len(shared.lexictrl) != 0:
            for lexicon in sorted(shared.lexictrl, key=lambda x: x.name):
                lexicon_row = LexiconRow(lexicon=lexicon)
                self.lexicons_list_box.append(lexicon_row)
            self.lexicons_scrolled_window.set_child(self.lexicons_list_box)
        else:
            self.lexicons_scrolled_window.set_child(self.no_lexicons_yet)

    def __on_key_pressed(
        self, _controller: Gtk.EventControllerKey, keyval: int, *_args
    ) -> None:
        """
        Handle key press events

        Parameters
        ----------
        _controller : Gtk.EventControllerKey
            The key event controller that emitted this method
        keyval : int
            The value of the pressed key
        """
        if keyval == Gdk.KEY_Escape:
            # Handle Escape key press
            if self.selection_mode_toggle_button.get_active():
                logger.debug("Escape pressed, disabling selection mode")
                self.selection_mode_toggle_button.set_active(False)

    def on_sorting_method_changed(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None:
        """
        Handle changes to the sorting method

        Parameters
        ----------
        action : Gio.SimpleAction
            The action that triggered the change
        state : GLib.Variant
            The new state of the sorting method
        """
        action.set_state(state)
        self.sort_method = str(state).strip("'")
        logger.info("Sorting method changed to “%s”, resorting", self.sort_method)
        self.lexicon_list_box.invalidate_sort()
        shared.state_schema.set_string("sort-method", self.sort_method)

    def on_sorting_type_changed(
        self, action: Gio.SimpleAction, state: GLib.Variant
    ) -> None:
        """
        Handle changes to the sorting type

        Parameters
        ----------
        action : Gio.SimpleAction
            The action that triggered the change
        state : GLib.Variant
            The new state of the sorting type
        """
        action.set_state(state)
        self.sort_type = str(state).strip("'")
        logger.info("Sorting type changed to “%s”, resorting", self.sort_type)
        self.lexicon_list_box.invalidate_sort()
        shared.state_schema.set_string("sort-type", self.sort_type)

    @Gtk.Template.Callback()
    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggles the sidebar visibility"""
        logger.debug(
            "Sidebar toggled: %s", not self.overlay_split_view.get_show_sidebar()
        )
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
        logger.debug("Search Lexicons mode: %s", not search_mode)

        if not search_mode:
            self.set_focus(search_entry)

        search_entry.set_text("")

    @Gtk.Template.Callback()
    def on_add_lexicon_button_clicked(self, *_args) -> None:
        """Present an Add Lexicon alert dialog"""
        logger.debug("Performing lexicon addition")
        self.add_lexicon_alert_dialog.present(self)
        self.add_lexicon_entry.set_buffer(Gtk.EntryBuffer())
        self.add_lexicon_entry.grab_focus()

    @Gtk.Template.Callback()
    def on_lexicon_search_entry_changed(self, *_args) -> None:
        """
        Invalidate the filter for the lexicons list box when the lexicons search entry changes
        """
        self.lexicons_list_box.invalidate_filter()

    @Gtk.Template.Callback()
    def on_add_lexicon_entry_changed(self, text: Gtk.Text) -> None:
        """
        Handle changes in the add lexicon entry row.

        Parameters
        ----------
        text : Gtk.Text
            The text widget that emitted this method.
        """
        if text.get_text() == "":
            self.add_lexicon_alert_dialog.add_css_class("error")
        else:
            if "error" in self.add_lexicon_alert_dialog.get_css_classes():
                self.add_lexicon_alert_dialog.remove_css_class("error")

    @Gtk.Template.Callback()
    def on_add_lexicon(self, alert_dialog: Adw.AlertDialog, response: str) -> None:
        """
        Handle the add lexicon action.

        Parameters
        ----------
        alert_dialog : Adw.AlertDialog
            The alert dialog that was used to add the lexicon.
        response : str
            The response from the alert dialog.
        """
        if response == "add":
            if alert_dialog.get_extra_child().get_text_length() != 0:
                logger.info(
                    "Adding lexicon “%s”",
                    alert_dialog.get_extra_child().get_buffer().get_text(),
                )
                shared.lexictrl.add_lexicon(
                    alert_dialog.get_extra_child().get_buffer().get_text()
                )
                self.build_sidebar()
            else:
                logger.warning("Lexicon name is empty")

    def __on_lexicon_changed(self, *_args) -> None:
        """Handle the lexicon change event"""
        if self.loaded_lexicon is not None:
            self.lexicon_list_box.remove_all()
            if len(self.loaded_lexicon) == 0:
                self.set_property("state", enums.WindowState.EMPTY_WORDS)
                return
            for word in self.loaded_lexicon:  # pylint: disable=not-an-iterable
                word_row = WordRow(word)
                self.lexicon_list_box.append(word_row)
            self.lexicon_scrolled_window.set_child(self.lexicon_list_box)
            self.lexicon_nav_page.set_title(self.loaded_lexicon.name)
            self.set_property("state", enums.WindowState.WORDS)
            self.update_refs_count()
        else:
            self.set_property("state", enums.WindowState.EMPTY)

    def __on_word_changed(self, *_args) -> None:
        """Handle the word change event"""
        if self.loaded_word is not None:
            # Clearing listable props list boxes
            self.translations_list_box.remove_all()
            self.examples_list_box.remove_all()
            self.word_types_list_box.remove_all()
            self.references_list_box.remove_all()

            # Loading word itself
            if self.loaded_word.word.startswith("&rtl"):
                self.word_entry_row_text.set_direction(Gtk.TextDirection.RTL)
            else:
                self.word_entry_row_text.set_direction(Gtk.TextDirection.LTR)
            self.word_entry_row.set_text(self.loaded_word.word.replace("&rtl", ""))

            # Loading pronunciation
            self.pronunciation_entry_row.set_text(self.loaded_word.pronunciation)

            # Loading listable props
            for expander_row in (
                (self.translations_expander_row, "translations", _("Translation")),
                (self.examples_expander_row, "examples", _("Example")),
            ):
                for item in getattr(self.loaded_word, expander_row[1]):
                    row: EntryRow = EntryRow(
                        expander_row[1], expander_row[2], item.replace("&rtl", "")
                    )
                    if item.startswith("&rtl"):
                        row.get_gtk_text().set_direction(Gtk.TextDirection.RTL)
                    row.get_gtk_text().connect("changed", self.__update_word)
                    row.get_gtk_text().connect("backspace", self.__remove_list_prop)
                    row.get_gtk_text().connect(
                        "direction-changed", self.__list_prop_dir_changed
                    )
                    expander_row[0].add_row(row)

            # Loading references
            for reference in self.loaded_word.references:
                word = self.loaded_lexicon.get_word(reference)
                self.references_list_box.append(ReferenceRow(word))

            # Loading types
            for type_ in self.loaded_word.types:
                typerow = TypeRow(type_)
                self.word_types_list_box.append(typerow)

            self.__set_row_sensitiveness(True)
            self.word_nav_page.set_title(self.loaded_word.word.replace("&rtl", ""))

    @Gtk.Template.Callback()
    def on_word_entry_changed(self, text: Gtk.Text) -> None:
        try:
            self.loaded_word.set_property("word", text.get_text())
        except AttributeError:
            logger.debug("Failed to set the “word” property of the loaded_word")

    @Gtk.Template.Callback()
    def on_pronunciation_entry_changed(self, text: Gtk.Text) -> None:
        self.loaded_word.set_property("pronunciation", text.get_text())

    def __update_word(self, text: Gtk.Text) -> None:
        row: EntryRow = text.get_ancestor(EntryRow)
        list_box: Gtk.ListBox = row.get_ancestor(Gtk.ListBox)
        for i, _row in enumerate(list_box):
            if _row == row:
                __callable = getattr(self.loaded_word, f"set_{row.id[:-1]}")
                __callable(
                    i,
                    (
                        f"&rtl{row.get_text()}"
                        if text.get_direction() == Gtk.TextDirection.RTL
                        else row.get_text()
                    ),
                )
                break

    def __remove_list_prop(self, text: Gtk.Text) -> None:
        if text.get_text_length() == 0:
            row: EntryRow = text.get_ancestor(EntryRow)
            list_box: Gtk.ListBox = text.get_ancestor(Gtk.ListBox)
            for i, _row in enumerate(list_box):
                if _row == row:
                    __callable = getattr(self.loaded_word, f"rm_{row.id[:-1]}")
                    __callable(i)
                    list_box.remove(row)
                    break

    def __list_prop_dir_changed(
        self, text: Gtk.Text, prev_dir: Gtk.TextDirection
    ) -> None:
        row: EntryRow = text.get_ancestor(EntryRow)
        list_box: Gtk.ListBox = row.get_ancestor(Gtk.ListBox)
        for i, _row in enumerate(list_box):
            if _row == row:
                __callable = getattr(self.loaded_word, f"set_{row.id[:-1]}")
                __callable(
                    i,
                    (
                        text.get_text()
                        if prev_dir == Gtk.TextDirection.RTL
                        else f"&rtl{text.get_text()}"
                    ),
                )
                break

    def __set_row_sensitiveness(self, sensitive: bool) -> None:
        self.word_entry_row.set_sensitive(sensitive)
        self.pronunciation_entry_row.set_sensitive(sensitive)
        self.translations_expander_row.set_sensitive(sensitive)
        self.word_type_expander_row.set_sensitive(sensitive)
        self.examples_expander_row.set_sensitive(sensitive)
        self.references_expander_row.set_sensitive(sensitive)
        if not sensitive:
            self.set_property("loaded-word", None)
            self.word_entry_row.set_text("")
            self.pronunciation_entry_row.set_text("")
            self.translations_expander_row.set_expanded(sensitive)
            self.word_type_expander_row.set_expanded(sensitive)
            self.examples_expander_row.set_expanded(sensitive)
            self.references_expander_row.set_expanded(sensitive)

    @Gtk.Template.Callback()
    def load_lexicon(self, _list_box: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        row: LexiconRow = row.get_child()
        logger.info("Loading “%s” lexicon into the UI", row.lexicon.name)
        if (
            shared.handler_ids["win.add_word_button"] is not None
            and shared.handler_ids["win.status_page_add_word_button"] is not None
        ):
            self.add_word_button.disconnect(shared.handler_ids["win.add_word_button"])
            self.status_page_add_word_button.disconnect(
                shared.handler_ids["win.status_page_add_word_button"]
            )
        shared.handler_ids["win.add_word_button"] = self.add_word_button.connect(
            "clicked", row.show_add_word_dialog
        )
        shared.handler_ids["win.status_page_add_word_button"] = (
            self.status_page_add_word_button.connect(
                "clicked", row.show_add_word_dialog
            )
        )
        self.set_property("loaded-lexicon", row.lexicon)

    @Gtk.Template.Callback()
    def load_word(self, _list_box: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
        try:
            logger.info("Loading “%s” word into the UI", row.word.word)
            self.set_property("loaded-word", row.word)
            if self.lexicon_split_view.get_collapsed():
                self.lexicon_split_view.set_show_content(True)
        except AttributeError:
            pass

    @Gtk.Template.Callback()
    def on_add_reference_button_clicked(self, *_args) -> None:
        self.references_dialog_list_box.remove_all()
        if len(self.loaded_lexicon) == 0:
            self.toast_overlay.add_toast(
                Adw.Toast(title=_("You have already referenced all words"))
            )
            logger.debug("Rejecting adding a reference: All words are referenced")
            return
        for word in self.loaded_lexicon:  # pylint: disable=not-an-iterable
            if word.id != self.loaded_word.id:
                self.references_dialog_list_box.append(ReferenceRow(word, False))
        self.references_dialog.present(self)

    @Gtk.Template.Callback()
    def on_add_type_button_clicked(self, *_args) -> None:
        self.assign_word_type_dialog_list_box.remove_all()
        if len(shared.config["word-types"]) == 0:
            toast = Adw.Toast(
                title=_("No word types available"), button_label=_("Configure")
            )
            toast.connect(
                "button-clicked",
                lambda *_: (
                    LexiPreferences().present(self)
                    if not LexiPreferences.opened
                    else None
                ),
            )
            self.toast_overlay.add_toast(toast)
            logger.debug("Rejecting adding a type: No types available")
            return
        for type_ in shared.config["word-types"]:
            if type_ not in self.loaded_word.types:
                typerow = TypeRow(type_, has_suffix=False)
                self.assign_word_type_dialog_list_box.append(typerow)
        self.assign_word_type_dialog.present(self)

    @Gtk.Template.Callback()
    def on_add_translation_button_clicked(self, *_args) -> None:
        self.loaded_word.add_translation("")
        self.__add_prop_entryrow(
            self.translations_list_box, "translations", _("Translation")
        )

    @Gtk.Template.Callback()
    def on_add_example_button_clicked(self, *_args) -> None:
        self.loaded_word.add_example("")
        self.__add_prop_entryrow(self.examples_list_box, "examples", _("Example"))

    def __add_prop_entryrow(
        self, listbox: Gtk.ListBox, id_: str, title: str = ""
    ) -> None:
        row = EntryRow(id_, title=title, text="")
        row.get_gtk_text().connect("changed", self.__update_word)
        row.get_gtk_text().connect("backspace", self.__remove_list_prop)
        row.get_gtk_text().connect("direction-changed", self.__list_prop_dir_changed)
        listbox.append(row)

    def __on_word_direction_changed(
        self, _text: Gtk.Text, prev_dir: Gtk.TextDirection
    ) -> None:
        self.loaded_word.set_property(
            "word",
            (
                "&rtl" + self.word_entry_row.get_text()
                if prev_dir != Gtk.TextDirection.RTL
                else self.word_entry_row.get_text()
            ),
        )

    @Gtk.Template.Callback()
    def open_filer_dialog(self, *_args) -> None:
        def __on_toggled(_check_button: Gtk.CheckButton) -> None:
            for row in self.filter_dialog_list_box:  # pylint: disable=not-an-iterable
                is_toggled = row.get_activatable_widget().get_active()
                word_type = row.get_title()

                if is_toggled:
                    if word_type not in shared.config["enabled-types"]:
                        logger.debug("Adding word type to filter: %s", word_type)
                        shared.config["enabled-types"].append(word_type)
                        shared.config["enabled-types"].sort()
                else:
                    if word_type in shared.config["enabled-types"]:
                        logger.debug("Removing word type from filter: %s", word_type)
                        shared.config["enabled-types"].remove(word_type)

            self.lexicon_list_box.invalidate_filter()

        def __populate_filter_dialog() -> None:
            for word_type in shared.config["word-types"]:
                logger.debug("Adding filter for word type: %s", word_type)
                action_row = Adw.ActionRow(title=word_type, activatable=False)
                check_button = Gtk.CheckButton()
                check_button.connect("toggled", __on_toggled)
                check_button.set_active(word_type in shared.config["enabled-types"])
                action_row.set_activatable_widget(check_button)
                action_row.add_suffix(check_button)
                self.filter_dialog_list_box.append(action_row)

        self.filter_dialog_list_box.remove_all()
        __populate_filter_dialog()
        logger.debug("Showing filter dialog")
        self.filter_dialog.present(self)

    def on_show_preferences_action(self, *_args) -> None:
        """Present the Preferences dialog to the user"""
        if LexiPreferences.opened:
            return
        preferences = LexiPreferences()
        logger.debug("Showing preferences")
        preferences.present(self)

    def on_add_word_action(self, *_args) -> None:
        if isinstance(self.loaded_lexicon, Lexicon):
            self.status_page_add_word_button.emit("clicked")

    def on_search_action(self, *_args) -> None:
        """
        Focus the words search entry when the search action is triggered (e.g., via `Ctrl+F`)
        """
        if self.words_bottom_bar_revealer.get_reveal_child():
            self.lexicon_search_entry.grab_focus()

    def open_dir(self, _toast: Adw.Toast, path: str) -> None:
        """Opens the given path in the file manager

        Parameters
        ----------
        _toast : Adw.Toast
            toast which emitted this method
        path : str
            path to open
        """
        logger.info("Opening: “%s”", path)
        Gio.AppInfo.launch_default_for_uri(f"file://{path}")

    @Gtk.Template.Callback()
    def selection_mode_button_toggled(self, button: Gtk.ToggleButton) -> None:
        """
        Toggle selection mode

        Parameters
        ----------
        button : Gtk.ToggleButton
            The toggle button that emitted this method
        """
        self.set_selection_mode(button.get_active())
        logger.debug("Selection mode toggled: %s", button.get_active())

    def set_selection_mode(self, enabled: bool) -> None:
        """
        Enable or disable selection mode for the words list box

        Parameters
        ----------
        enabled : bool
            Whether to enable or disable selection mode
        """
        # Gratefully "stolen" from
        # https://github.com/flattool/warehouse/blob/0a18e5d81b8b06e45bf493b3ff31c12edbd36869/src/packages_page/packages_page.py#L226
        if enabled:
            self.lexicon_list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        else:
            self.lexicon_list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.selection_mode_toggle_button.set_active(enabled)

        i = 0
        row: WordRow
        while row := self.lexicon_list_box.get_row_at_index(i):
            i += 1
            row.check_button.set_active(False)
            row.check_button_revealer.set_reveal_child(enabled)
            if enabled:
                row.set_activatable_widget(row.check_button)
                row.refs_count_label_box.set_visible(False)
            else:
                row.set_activatable_widget(None)
                if row.word.ref_count > 0:
                    row.refs_count_label_box.set_visible(True)
        self.delete_selected_words_button_revealer.set_reveal_child(enabled)

    @Gtk.Template.Callback()
    def on_delete_selected_words_action(self, *_args) -> None:
        """Delete selected words"""
        logger.info("Deleting selected words: %s", len(self.selected_words))
        for row in self.selected_words.copy():
            logger.info("Deleting word: “%s”", row.word.word)
            self.selected_words.remove(row)
            row.delete()
        self.set_selection_mode(False)
        if self.lexicon_list_box.get_row_at_index(0) is None:
            self.lexicon_scrolled_window.set_child(self.no_words_yet)
            self.words_bottom_bar_revealer.set_reveal_child(False)
            self.__set_row_sensitiveness(False)

    @Gtk.Template.Callback()
    def on_search_entry_changed(self, *_args) -> None:
        """
        Invalidate the filter for the lexicon list box when the search entry changes
        """
        self.lexicon_list_box.invalidate_filter()

    @Gtk.Template.Callback()
    def reset_filters(self, *_args) -> None:
        """Reset all filters in the filter dialog"""
        logger.debug("Resetting filters")
        for row in self.filter_dialog_list_box:  # pylint: disable=not-an-iterable
            row.get_activatable_widget().set_active(False)
        self.filter_dialog.close()

    def update_refs_count(self) -> None:
        """Update the reference count for all words in the lexicon list box"""
        logger.debug("Updating references count")
        for word_row in self.lexicon_list_box:  # pylint: disable=not-an-iterable
            word_row.get_ref_count()

    def on_reload_words_list_action(self, *_args) -> None:
        # pylint: disable=comparison-with-callable
        if self.state == enums.WindowState.WORDS:
            self.lexicon_list_box.invalidate_sort()

    @GObject.Property(nick="loaded-lexicon")
    def loaded_lexicon(self) -> Lexicon:
        """The currently loaded lexicon"""
        return self._loaded_lexicon

    @loaded_lexicon.setter
    def loaded_lexicon(self, lexicon: Lexicon) -> None:
        """The currently loaded lexicon"""
        self._loaded_lexicon = lexicon

    @GObject.Property(nick="loaded-word")
    def loaded_word(self) -> Word:
        """The currently loaded word"""
        return self._loaded_word

    @loaded_word.setter
    def loaded_word(self, word: Word) -> None:
        """The currently loaded word"""
        self._loaded_word = word

    @GObject.Property()
    def state(self) -> enums.WindowState:
        return self._state

    @state.setter
    def state(self, state: enums.WindowState) -> None:
        self._state = state

    def __on_state_change(self, *_args, state_: enums.WindowState = None) -> None:
        state = self.state if not state_ else state_
        match state:
            case enums.WindowState.EMPTY:
                self.words_bottom_bar_revealer.set_reveal_child(False)
                self.lexicon_scrolled_window.set_child(self.lexicon_not_selected)
                self.sort_menu_button.set_sensitive(False)
                self.filter_button.set_sensitive(False)
                self.word_nav_page.set_title(_("Word"))
                self.lexicon_nav_page.set_title("Lexi")
                self.__set_row_sensitiveness(False)
            case enums.WindowState.EMPTY_WORDS:
                self.__on_state_change(state_=enums.WindowState.EMPTY)
                self.lexicon_scrolled_window.set_child(self.no_words_yet)
            case enums.WindowState.WORDS:
                self.lexicon_scrolled_window.set_child(self.lexicon_list_box)
                self.words_bottom_bar_revealer.set_reveal_child(True)
                self.sort_menu_button.set_sensitive(True)
                self.filter_button.set_sensitive(True)


class EntryRow(Adw.EntryRow):
    """Custom entry row widget.

    Used for displaying and editing text entries with a title.

    Parameters
    ----------
    title : str, optional
        The title of the entry row, by default "".
    text : str, optional
        The initial text of the entry row, by default "".
    """

    __gtype_name__ = "LexiEntryRow"

    def __init__(self, id_: str, title: str = "", text: str = "") -> "EntryRow":
        super().__init__(title=title, text=text)
        self.id = id_

    def get_gtk_text(self) -> Gtk.Text:
        """Retrieve the Gtk.Text widget from the entry row.

        Returns
        -------
        Gtk.Text
            The Gtk.Text widget contained in the entry row.
        """
        for item in self.get_child():
            for _item in item:
                if isinstance(_item, Gtk.Text):
                    return _item
