from enum import Enum


class Icon(str, Enum):
    """Enum class with all app's icons

    ::

        TOGGLE_SIDEBAR
        ADD_PAIR
        TOGGLE_SEARCH
        SORT
        APP_MENU
        TOGGLE_SELECTION
        LIST_EXPANDER_RIGHT
        LEXICON
        NO_FOUND
        DELETE
    """

    TOGGLE_SIDEBAR: str = "toggle-sidebar-symbolic"
    ADD_PAIR: str = "add-symbolic"
    TOGGLE_SEARCH: str = "toggle-search-symbolic"
    SORT: str = "sort-symbolic"
    APP_MENU: str = "app-menu-symbolic"
    TOGGLE_SELECTION: str = "toggle-selection-symbolic"
    LEXICON: str = "lexicon-symbolic"
    NO_FOUND: str = "no-found-symbolic"
    DELETE: str = "delete-symbolic"

    def __str__(self) -> str:
        return self.value
