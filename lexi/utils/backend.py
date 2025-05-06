import os
import uuid
from pathlib import Path
from typing import Self

import yaml
from gi.repository import GObject

from lexi import shared


class Lexicon:
    __gtype_name__ = "Lexicon"

    def __init__(self, path: Path) -> "Lexicon":
        self._file = open(path, "r", encoding="utf-8")
        self._path = path
        self._data = yaml.safe_load(self._file)
        self.id = self._data["id"]
        self.words: list[Word] = []

        self.__populate_words()

    def __populate_words(self) -> None:
        """Populate the words list with the words from the lexicon"""
        for word in self._data["words"]:
            self.words.append(Word(word, self))

    def get_word(self, word_id: int) -> "Word" | None:
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
                self.words.pop(i)
                for _word in self._data["words"]:
                    if _word["id"] == id_:
                        self._data["words"].remove(_word)
                        break
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
        lexicon_id = str(uuid.uuid4().hex)
        lexicon_path = os.path.join(shared.data_dir, "lexicons", lexicon_id + ".yaml")
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
    def path(self) -> list[Path, str]:
        """Get the path of the lexicon as a list of Path and str"""
        return [self._path, str(self._path)]

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


class Word:
    __gtype_name__ = "Word"

    def __init__(self, word: dict, parent_lexicon: Lexicon) -> "Word":
        self._word = word
        self.parent_lexicon = parent_lexicon

    def add_translation(self, translation: str) -> Self:
        """Add a translation to the word"""
        self._word["translations"].append(translation)
        return self

    def set_translation(self, index: int, translation: str) -> Self:
        """Set a translation for the word"""
        if index < len(self.translations):
            self._word["translations"][index] = translation
        else:
            raise IndexError("Index out of range")
        return self

    def rm_translation(self, index: int) -> Self:
        """Remove a translation from the word"""
        if index < len(self.translations):
            self._word["translations"].pop(index)
        else:
            raise IndexError("Index out of range")
        return self

    def add_type(self, type_: str) -> Self:
        """Add a type to the word"""
        if type_ not in self.types:
            self._word["types"].append(type_)
        else:
            raise ValueError("Type already exists")
        return self

    def rm_type(self, type_: str) -> Self:
        """Remove a type from the word"""
        if type_ in self.types:
            self._word["types"].remove(type_)
        else:
            raise ValueError("Type not found")
        return self

    def add_example(self, example: str) -> Self:
        """Add an example to the word"""
        self._word["examples"].append(example)
        return self

    def set_example(self, index: int, example: str) -> Self:
        """Set an example for the word"""
        if index < len(self.examples):
            self._word["examples"][index] = example
        else:
            raise IndexError("Index out of range")
        return self

    def rm_example(self, index: int) -> Self:
        """Remove an example from the word"""
        if index < len(self.examples):
            self._word["examples"].pop(index)
        else:
            raise IndexError("Index out of range")
        return self

    def add_reference(self, reference: int) -> Self:
        """Add a reference to the word"""
        if reference not in self.references:
            self._word["references"].append(reference)
        else:
            raise ValueError("Reference already exists")
        return self

    def rm_reference(self, reference: int) -> Self:
        """Remove a reference from the word"""
        if reference in self.references:
            self._word["references"].remove(reference)
        else:
            raise ValueError("Reference not found")
        return self

    def add_tag(self, tag: str) -> Self:
        """Add a tag to the word"""
        if tag not in self.tags:
            self._word["tags"].append(tag)
        else:
            raise ValueError("Tag already exists")
        return self

    def rm_tag(self, tag: str) -> Self:
        """Remove a tag from the word"""
        if tag in self.tags:
            self._word["tags"].remove(tag)
        else:
            raise ValueError("Tag not found")
        return self

    # Immutable properties
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

    # Mutable properties
    @GObject.Property(type=str)
    def word(self) -> str:
        """The name of the word"""
        return self._word["word"]

    @word.setter
    def word(self, word: str) -> None:
        """The name of the word"""
        self._word["word"] = word

    @GObject.Property(type=str)
    def pronunciation(self) -> str:
        """The pronunciation of the word"""
        return self._word["pronunciation"]

    @pronunciation.setter
    def pronunciation(self, pronunciation: str) -> None:
        """The pronunciation of the word"""
        self._word["pronunciation"] = pronunciation
