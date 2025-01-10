"""Module with controller classes for Collections, single collection and Lexicons

   Supported controllers: ::

        CollectionsController(collections_dir: str) -> New controller for all\
 collections
        CollectionController(collection_path: str) -> New controller for single\
 collection
        LexiconController(lexicon_path: str) -> New controller for lexicon
"""

import os
import random
import shutil
import string
from typing import TextIO

import yaml
from gi.repository import GObject

from lexi import shared


class CollectionsController:
    """Controller for creating, removing and saving Collections

    Parameters
    ----------
    collections_dir : str
        /path/to/collections/directory
    """

    __gtype_name__ = "CollectionsController"

    def __init__(self, collections_dir: str) -> None:
        shared.collection_controller = self
        self.collections_dir: str = collections_dir
        self.collections_file_path: str = os.path.join(
            collections_dir, "collections.yaml"
        )

        if not os.path.exists(self.collections_file_path):
            with open(self.collections_file_path, "w", encoding="utf-8") as file:
                file.write("[]")

        self.collections_file: TextIO = open(
            self.collections_file_path, "r+", encoding="utf-8"
        )
        self._collections: list = yaml.safe_load(self.collections_file) or []

    def save_collections(self, *_args) -> None:
        """Saves instace collections to the file"""
        self.collections_file.seek(0)
        self.collections_file.truncate(0)
        yaml.dump(
            self._collections,
            self.collections_file,
            sort_keys=False,
            allow_unicode=True,
        )

    def add_collection(self, collection_name: str) -> None:
        """Adds new collection to the instance collections and saves it to the file

        Parameters
        ----------
        collection_name : str
            The name of the new collection
        """
        while True:
            rnd_id: str = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=16)
            )
            if rnd_id not in os.listdir(self.collections_dir):
                os.mkdir(os.path.join(self.collections_dir, rnd_id))
                break
        collection: dict = {"name": collection_name, "id": rnd_id}
        self._collections.append(collection)
        self.save_collections()

    def remove_collection(self, collection_id: str) -> None:
        """Removes collection by provided `id`.\
           Saves instace collections to the file first to allow 'Undo' action

        Parameters
        ----------
        collection_id : str
            id of the collection to be deleted
        """
        self.save_collections()
        self._collections = [c for c in self._collections if c["id"] != collection_id]

    def undo_remove_collection(self) -> None:
        """Undoing remove action"""
        self._collections = yaml.safe_load(self.collections_file) or []

    def remove_garbage(self) -> None:
        """Removes directories of the deleted collections

        Should be called on app close to provide 'Undo' action work
        """
        collections_dirs: list = [
            d
            for d in os.listdir(self.collections_dir)
            if os.path.isdir(os.path.join(self.collections_dir, d))
        ]
        ids: list = [item.get("id") for item in self._collections]

        for directory in collections_dirs:
            if directory not in ids:
                shutil.rmtree(os.path.join(self.collections_dir, directory))

    @GObject.Property
    def collections(self) -> list:
        return self._collections


class CollectionController:
    """Controller for creating, removing and saving Lexicons

    Parameters
    ----------
    collection_path : str
        /path/to/collection/directory
    """

    __gtype_name__ = "CollectionController"

    def __init__(self, collection_path: str) -> None:
        self.collection_file_path: str = os.path.join(
            collection_path, "collection.yaml"
        )

        if not os.path.exists(self.collection_file_path):
            with open(self.collection_file_path, "w", encoding="utf-8") as file:
                file.write("[]")

        self.collection_file: TextIO = open(
            self.collection_file_path, "r+", encoding="utf-8"
        )
        self._collection: list = yaml.safe_load(self.collection_file) or []

    def save_collection(self) -> None:
        """Saves instance collection to the file"""
        self.collection_file.seek(0)
        self.collection_file.truncate(0)
        yaml.dump(
            self._collection, self.collection_file, sort_keys=False, allow_unicode=True
        )

    def add_lexicon(self, lexicon_name: str) -> None:
        """Adds new lexicon to the instance collection and saves it to the file

        Parameters
        ----------
        lexicon_name : str
            The name of the new lexicon
        """
        lexicon_path: str = os.path.join(
            os.path.dirname(self.collection_file.name), lexicon_name
        )
        if not os.path.exists(lexicon_path):
            os.makedirs(os.path.join(lexicon_path, "resources"))
            with open(
                os.path.join(lexicon_path, "lexicon.yaml"), "w", encoding="utf-8"
            ) as file:
                file.write("[]")
            self._collection.append({"name": lexicon_name, "tags": []})
            self.save_collection()
        else:
            raise AttributeError(
                "This lexicon already exists. All lexicon names must be unique"
            )

    def remove_lexicon(self, lexicon_name: str) -> None:
        """Removes lexicon by provided `name`.\
            Saves instance collection to the file first to allow 'Undo' action

        Parameters
        ----------
        lexicon_name : str
            id of the lexicon to be deleted
        """
        self.save_collection()
        self._collection = [l for l in self._collection if l["name"] != lexicon_name]

    def undo_remove_lexicon(self) -> None:
        """Undoing remove action"""
        self._collection = yaml.safe_load(self.collection_file) or []

    def remove_garbage(self) -> None:
        """Removes directories of the deleted lexicon

        Called on demand, but 'Undo' action is unavailable
        """
        lexicons: list = [
            d
            for d in os.listdir(os.path.dirname(self.collection_file.name))
            if os.path.isdir(
                os.path.join(os.path.dirname(self.collection_file.name), d)
            )
        ]
        names: list = [item.get("name") for item in self._collection]

        for lexicon in lexicons:
            if lexicon not in names:
                shutil.rmtree(
                    os.path.join(os.path.dirname(self.collection_file.name), lexicon)
                )

    @GObject.Property
    def collection(self) -> list:
        return self._collection


class LexiconController:
    """Controller for creating, removing and saving Pairs

    Parameters
    ----------
    lexicon_path : str
        /path/to/lexicon/directory
    """

    __gtype_name__ = "LexiconController"

    def __init__(self, lexicon_path: str) -> None:
        self.resources: str = os.path.join(lexicon_path, "resources")
        self.lexicon_file: TextIO = open(os.path.join(lexicon_path, "lexicon.yaml"))
        self._lexicon: list = yaml.safe_load(self.lexicon_file)

    def save_lexicon(self) -> None:
        """Saves instace lexicon to the file"""
        self.lexicon_file.seek(0)
        self.lexicon_file.truncate(0)
        yaml.dump(self._lexicon, self.lexicon_file, sort_keys=False, allow_unicode=True)

    def add_pair(self, key: str) -> None:
        """Adds new pair to the instance lexicon and saves it to the file

        Parameters
        ----------
        key : str
            The key of the new pair
        """
        while True:
            rnd_id: str = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=16)
            )
            if rnd_id not in os.listdir(self.resources):
                os.mkdir(os.path.join(self.resources, rnd_id))
                break

        self._lexicon.append(
            {"key": key, "value": None, "resources_id": rnd_id, "resources": []}
        )
        self.save_lexicon()

    def remove_pair(self, resources_id: str) -> None:
        """Removes pair by provided `resource_id`.\
           Saves instace collection to the file first to allow 'Undo' action

        Parameters
        ----------
        resources_id : str
            id of the pair resources to be deleted
        """
        self.save_lexicon()
        self._lexicon = [p for p in self._lexicon if p["resources_id"] != resources_id]

    def undo_remove_pair(self) -> None:
        """Undoing remove action"""
        self._lexicon = yaml.safe_load(self.lexicon_file) or []

    def remove_garbage(self) -> None:
        """Removes resources of the deleted pair

        Called on demand, but 'Undo' action is unavailable
        """
        resources: list = [
            d
            for d in os.listdir(self.resources)
            if os.path.isdir(os.path.join(self.resources, d))
        ]
        res_ids: list = [item.get("resources_id") for item in self._lexicon]

        for resource in resources:
            if resource not in res_ids:
                shutil.rmtree(os.path.join(self.resources, resource))

    @GObject.Property
    def lexicon(self) -> list:
        return self._lexicon
