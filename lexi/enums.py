from enum import Enum

from lexi import shared


class Icon(str, Enum):
    """Enum class with all app icons

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
        FILTER_WORDS
        GENERAL
        BACKUP
        EXPORT
        IMPORT
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
    TIMES_REFERENCED: str = "times-referenced-symbolic"
    FILTER_WORDS: str = "filter-words-symbolic"
    GENERAL: str = "general-symbolic"
    BACKUP: str = "lexi-backup-symbolic"
    EXPORT: str = "export-database-symbolic"
    IMPORT: str = "import-database-symbolic"

    def __str__(self) -> str:
        return self.value


class WordType(str, Enum):
    """Enum class with all word types in i18n format

    ::

        NOUN
        VERB
        ADJECTIVE
        ADVERB
        PRONOUN
        PREPOSITION
        CONJUNCTION
        INTERJECTION
        ARTICLE
        IDIOM
        CLAUSE
        PREFIX
        SUFFIX
    """

    NOUN: str = _("Noun")
    VERB: str = _("Verb")
    ADJECTIVE: str = _("Adjective")
    ADVERB: str = _("Adverb")
    PRONOUN: str = _("Pronoun")
    PREPOSITION: str = _("Preposition")
    CONJUNCTION: str = _("Conjunction")
    INTERJECTION: str = _("Interjection")
    ARTICLE: str = _("Article")
    IDIOM: str = _("Idiom")
    CLAUSE: str = _("Clause")
    PREFIX: str = _("Prefix")
    SUFFIX: str = _("Suffix")

    def __str__(self) -> str:
        return self.value

# pylint: disable=invalid-name
class Schema:
    """Enum for all Lexi gschema values

    ::

        WORD_AUTOSAVE() : bool
    """

    @staticmethod
    def WORD_AUTOSAVE() -> bool:
        return shared.schema.get_boolean("word-autosave")
