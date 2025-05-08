from gi.repository import Adw, GObject, Gtk

from lexi import enums, shared
from lexi.logging.logger import logger
from lexi.ui.LexiconRow import LexiconRow
from lexi.ui.WordRow import WordRow
from lexi.utils.backend import Lexicon, Word


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
        # self.lexicons_list_box.set_filter_func(self.filter_lexicons)
        # self.lexicon_list_box.set_sort_func(self.sort_words)
        # self.lexicon_list_box.set_filter_func(self.filter_words)
        self.search_bar.connect_entry(self.search_entry)
        # key_kapture_controller.connect("key-pressed", self.on_key_pressed)
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

    @Gtk.Template.Callback()
    def on_toggle_sidebar_action(self, *_args) -> None:
        """Toggles the sidebar visibility"""
        logger.debug(
            "Sidebar toggled: %s", not self.overlay_split_view.get_show_sidebar()
        )
        self.overlay_split_view.set_show_sidebar(
            not self.overlay_split_view.get_show_sidebar()
        )

    @Gtk.Template.Callback()
    def on_toggle_search_action(self, *_args) -> None:
        """Toggle the visibility of the search bar"""
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
                        row.get_gtk_text().get_direction(Gtk.TextDirection.RTL)
                    row.get_gtk_text().connect("changed", self.__update_word)
                    row.get_gtk_text().connect("backspace", self.__remove_list_prop)
                    row.get_gtk_text().connect(
                        "direction-changed", self.__list_prop_dir_changed
                    )
                    expander_row[0].add_row(row)
            self.__set_row_sensitiveness(True)

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
        except AttributeError:
            pass

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
