import os
import uuid
from pathlib import Path
from typing import Iterator, Self, Union

import yaml
from gi.repository import GObject

from lexi import shared


class LexiconController:
    __gtype_name__ = "LexiconController"

    def __init__(self) -> None:
        self._lexicons: list[Lexicon] = []

        self.__populate_lexicons()

    def __iter__(self) -> Iterator["Lexicon"]:
        """Iterate over the lexicons"""
        return iter(self._lexicons)

    def __len__(self) -> int:
        """Return the number of lexicons"""
        return len(self._lexicons)

    def __populate_lexicons(self) -> None:
        """Populate the lexicons list with the lexicons from the data directory"""
        for file in os.listdir(os.path.join(shared.data_dir, "lexicons")):
            if file.endswith(".yaml"):
                lexicon = Lexicon.from_str(
                    os.path.join(shared.data_dir, "lexicons", file)
                )
                self._lexicons.append(lexicon)

    def add_lexicon(self, name: str) -> Self:
        """Add a new lexicon to the controller

        Parameters
        ----------
        name : str
            Name of the lexicon to add
        """
        lexicon = Lexicon.for_unexistent(name)
        self._lexicons.append(lexicon)
        return self

    def rm_lexicon(self, id_: str) -> "Lexicon":
        """Remove a Lexicon

        Parameters
        ----------
        id : str
            ID of the lexicon to remove

        Returns
        ----------
        Lexicon
            Lexicon object if found

        Raises
        ----------
        ValueError
            If the lexicon is not found
        """
        for i, lexicon in enumerate(self._lexicons):
            if lexicon.id == id_:
                lexicon._file.close()  # pylint: disable=protected-access
                os.remove(lexicon.path[0])
                self._lexicons.pop(i)
                return lexicon
        raise ValueError("Lexicon not found")

    def get_lexicon(self, id_: str) -> Union["Lexicon", None]:
        """Return the lexicon with the given id

        Parameters
        ----------
        id : str
            ID of the lexicon to return

        Returns
        -------
        Lexicon
            Lexicon object if found, None otherwise
        """
        for lexicon in self._lexicons:
            if lexicon.id == id_:
                return lexicon
        return None


class Lexicon(GObject.Object):
    __gtype_name__ = "Lexicon"

    def __init__(self, path: Path) -> "Lexicon":
        super().__init__()
        self._file = open(path, "r+", encoding="utf-8")
        self._path = path
        self._data = yaml.safe_load(self._file)
        self.id = self._data["id"]
        self.words: list[Word] = []

        self.__populate_words()

    def __iter__(self) -> Iterator["Word"]:
        """Iterate over the words in the lexicon"""
        return iter(self.words)

    def __len__(self) -> int:
        """Return the number of words in the lexicon"""
        return len(self.words)

    def __populate_words(self) -> None:
        """Populate the words list with the words from the lexicon"""
        for word in self._data["words"]:
            self.words.append(Word(word, self))

    def get_word(self, word_id: int) -> Union["Word", None]:
        """Return the word with the given id from the lexicon

        Parameters
        ----------
        word_id : int
            ID of the word to return

        Returns
        -------
        Word
            Word object if found, None otherwise
        """
        for word in self.words:
            if word.id == word_id:
                return word
        return None

    def add_word(self, word: dict) -> Self:
        """Adds a new word to the lexicon

        Parameters
        ----------
        word : dict
            Dict containing the word data
        """
        self.words.append(Word(word, self))
        self._data["words"].append(word)
        return self

    def rm_word(self, id_: int) -> Self:
        """Removes a word from the lexicon

        Parameters
        ----------
        id : int
            ID of the word to remove
        """
        for i, word in enumerate(self.words):
            if word.id == id_:
                self._data["words"].remove(word._word) # pylint: disable=protected-access
                self.words.pop(i)
                break
        else:
            raise ValueError("Word not found")
        return self

    def save(self) -> None:
        """Save the lexicon to the file"""
        words = []
        for word in self.words:
            words.append(word._word)  # pylint: disable=protected-access
        self._data["words"] = words
        self._file.seek(0)
        self._file.truncate(0)
        yaml.dump(
            self._data,
            self._file,
            sort_keys=False,
            encoding=None,
            allow_unicode=True,
        )

    @classmethod
    def from_str(cls, path: str) -> "Lexicon":
        """Create a Lexicon object from a string"""
        return cls(Path(path))

    @classmethod
    def for_unexistent(cls, name: str) -> "Lexicon":
        """Create a Lexicon object for a new lexicon"""
        while True:
            lexicon_id = str(uuid.uuid4().hex)
            lexicon_path = os.path.join(
                shared.data_dir, "lexicons", lexicon_id + ".yaml"
            )
            if not os.path.exists(lexicon_path):
                break

        with open(lexicon_path, "w", encoding="utf-8") as file:
            yaml.dump(
                {
                    "id": lexicon_id,
                    "name": name,
                    "words": [],
                },
                file,
                sort_keys=False,
                encoding=None,
                allow_unicode=True,
            )
        return cls(Path(lexicon_path))

    @property
    def path(self) -> tuple[Path, str]:
        """Get the path of the lexicon as a list of Path and str"""
        return (self._path, str(self._path))

    @GObject.Property(type=str)
    def name(self) -> str:
        """The name of the lexicon"""
        return self._data["name"]

    @name.setter
    def name(self, name: str) -> None:
        """The name of the lexicon"""
        self._data["name"] = name
        with open(self._path, "w", encoding="utf-8") as file:
            yaml.dump(
                self._data,
                file,
                sort_keys=False,
                encoding=None,
                allow_unicode=True,
            )


# pylint: disable=too-many-public-methods
class Word(GObject.Object):
    __gtype_name__ = "Word"

    __gsignals__ = {
        "tags-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "translations-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "examples-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "references-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
        "types-changed": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, word: dict, parent_lexicon: Lexicon) -> "Word":
        super().__init__()
        self._word = word
        self.parent_lexicon = parent_lexicon

        self.connect("notify::word", lambda *_: self.parent_lexicon.save())
        self.connect("notify::pronunciation", lambda *_: self.parent_lexicon.save())
        self.connect("tags-changed", lambda *_: self.parent_lexicon.save())
        self.connect("translations-changed", lambda *_: self.parent_lexicon.save())
        self.connect("examples-changed", lambda *_: self.parent_lexicon.save())
        self.connect("references-changed", lambda *_: self.parent_lexicon.save())
        self.connect("types-changed", lambda *_: self.parent_lexicon.save())

    def add_translation(self, translation: str) -> Self:
        """Add a translation to the word"""
        self._word["translations"].append(translation)
        self.emit("translations-changed")
        return self

    def set_translation(self, index: int, translation: str) -> Self:
        """Set a translation for the word"""
        if index < len(self.translations):
            self._word["translations"][index] = translation
        else:
            raise IndexError("Index out of range")
        self.emit("translations-changed")
        return self

    def rm_translation(self, index: int) -> Self:
        """Remove a translation from the word"""
        if index < len(self.translations):
            self._word["translations"].pop(index)
        else:
            raise IndexError("Index out of range")
        self.emit("translations-changed")
        return self

    def add_type(self, type_: str) -> Self:
        """Add a type to the word"""
        if type_ not in self.types:
            self._word["types"].append(type_)
        else:
            raise ValueError("Type already exists")
        self.emit("types-changed")
        return self

    def rm_type(self, type_: str) -> Self:
        """Remove a type from the word"""
        if type_ in self.types:
            self._word["types"].remove(type_)
        else:
            raise ValueError("Type not found")
        self.emit("types-changed")
        return self

    def add_example(self, example: str) -> Self:
        """Add an example to the word"""
        self._word["examples"].append(example)
        self.emit("examples-changed")
        return self

    def set_example(self, index: int, example: str) -> Self:
        """Set an example for the word"""
        if index < len(self.examples):
            self._word["examples"][index] = example
        else:
            raise IndexError("Index out of range")
        self.emit("examples-changed")
        return self

    def rm_example(self, index: int) -> Self:
        """Remove an example from the word"""
        if index < len(self.examples):
            self._word["examples"].pop(index)
        else:
            raise IndexError("Index out of range")
        self.emit("examples-changed")
        return self

    def add_reference(self, reference: int) -> Self:
        """Add a reference to the word"""
        if reference not in self.references:
            self._word["references"].append(reference)
        else:
            raise ValueError("Reference already exists")
        self.emit("references-changed")
        return self

    def rm_reference(self, reference: int) -> Self:
        """Remove a reference from the word"""
        if reference in self.references:
            self._word["references"].remove(reference)
        else:
            raise ValueError("Reference not found")
        self.emit("references-changed")
        return self

    def add_tag(self, tag: str) -> Self:
        """Add a tag to the word"""
        if tag not in self.tags:
            self._word["tags"].append(tag)
        else:
            raise ValueError("Tag already exists")
        self.emit("tags-changed")
        return self

    def rm_tag(self, tag: str) -> Self:
        """Remove a tag from the word"""
        if tag in self.tags:
            self._word["tags"].remove(tag)
        else:
            raise ValueError("Tag not found")
        self.emit("tags-changed")
        return self

    # Plain properties
    @property
    def id(self) -> int:
        """ID of the word"""
        return self._word["id"]

    @property
    def translations(self) -> list[str]:
        """Translations of the word"""
        return self._word["translations"]

    @property
    def types(self) -> list[str]:
        """Types of the word"""
        return self._word["types"]

    @property
    def examples(self) -> list[str]:
        """Examples of the word"""
        return self._word["examples"]

    @property
    def references(self) -> list[str]:
        """References of the word"""
        return self._word["references"]

    @property
    def tags(self) -> list[str]:
        """Tags of the word"""
        return self._word["tags"]

    # GObject properties
    @GObject.Property(type=str)
    def word(self) -> str:
        """The word itself"""
        return self._word["word"]

    @word.setter
    def word(self, word: str) -> None:
        """The word itself"""
        self._word["word"] = word

    @GObject.Property(type=str)
    def pronunciation(self) -> str:
        """The pronunciation of the word"""
        return self._word["pronunciation"]

    @pronunciation.setter
    def pronunciation(self, pronunciation: str) -> None:
        """The pronunciation of the word"""
        self._word["pronunciation"] = pronunciation
