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
        self.collections_file: TextIO = open(
            collections_dir + "/collections.yaml", "r+", encoding="utf-8"
        )
        self.collections: list = yaml.safe_load(self.collections_file)

    def save_collections(self, *_args) -> None:
        """Saves instace collections to the file"""
        self.collections_file.seek(0)
        self.collections_file.truncate(0)
        yaml.dump(
            self.collections,
            self.collections_file,
            sort_keys=False,
            encoding=None,
            allow_unicode=True,
        )

    def add_collection(self, collection_name: str) -> None:
        """Adds new collection to the instance collections and saves it to the file

        Parameters
        ----------
        collection_name : str
            The name of the new collection
        """
        while (
            rnd_id := "".join(
                random.choices(string.ascii_lowercase + string.digits, k=16)
            )
        ) not in os.listdir(self.collections_dir):
            os.mkdir(self.collections_dir + f"/{rnd_id}/")
            break
        collection = {"name": collection_name, "id": rnd_id}
        self.collections.append(collection)
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
        for collection in self.collections:
            if collection["id"] == collection_id:
                self.collections.remove(collection)
                return

    def undo_remove_collection(self) -> None:
        """Undoing remove action"""
        self.collections: list = yaml.safe_load(self.collections_file)

    def remove_garbage(self) -> None:
        """Removes directories of the deleted collections

        Should be called on app close to provide 'Undo' action work
        """
        collections_dirs = [
            d
            for d in os.listdir(self.collections_dir)
            if os.path.isdir(os.path.join(self.collections_dir, d))
        ]
        ids = [item.get("id") for item in self.collections]

        for directory in collections_dirs:
            if directory not in ids:
                shutil.rmtree(self.collections_dir + f"/{directory}")


class CollectionController:
    """Controller for creating, removing and saving Lexicons

    Parameters
    ----------
    collection_dir : str
        /path/to/collection/directory
    """

    __gtype_name__ = "CollectionController"

    def __init__(self, collection_path: str) -> None:
        if not os.path.exists(collection_path + "/collection.yaml"):
            file = open(collection_path + "/collection.yaml", "x+", encoding="utf-8")
            file.write("[]")
            file.close()

        self.collection_file: TextIO = open(
            collection_path + "/collection.yaml", "r+", encoding="utf-8"
        )
        self._collection: list = yaml.safe_load(self.collection_file)

    def save_collection(self) -> None:
        """Saves instace collection to the file"""
        self.collection_file.seek(0)
        self.collection_file.truncate(0)
        yaml.dump(
            self._collection,
            self.collection_file,
            sort_keys=False,
            encoding=None,
            allow_unicode=True,
        )

    def add_lexicon(self, lexicon_name: str) -> None:
        """Adds new lexicon to the instance collection and saves it to the file

        Parameters
        ----------
        lexicon_name : str
            The name of the new lexicon
        """
        if lexicon_name not in os.listdir(os.path.dirname(self.collection_file.name)):
            os.makedirs(
                os.path.dirname(self.collection_file.name)
                + f"/{lexicon_name}/resources"
            )
            open(
                os.path.dirname(self.collection_file.name)
                + f"/{lexicon_name}/lexicon.yaml",
                "w",
                encoding="utf-8",
            ).write("[]")
            self._collection.append({"name": lexicon_name, "tags": []})
            self.save_collection()
        else:
            raise AttributeError(
                "This lexicon already exists. All lexicon names must be unique"
            )

    def remove_lexicon(self, lexicon_name: str) -> None:
        """Removes lexicon by provided `name`.\
           Saves instace collection to the file first to allow 'Undo' action

        Parameters
        ----------
        lexicon_name : str
            id of the lexicon to be deleted
        """
        self.save_collection()
        for lexicon in self._collection:
            if lexicon["name"] == lexicon_name:
                self._collection.remove(lexicon)
                return

    def undo_remove_lexicon(self) -> None:
        """Undoing remove action"""
        self._collection: list = yaml.safe_load(self.collection_file)

    def remove_garbage(self) -> None:
        """Removes directories of the deleted lexicon

        Called on demand, but 'Undo' action is unavailable
        """
        lexicons = [
            d
            for d in os.listdir(os.path.dirname(self.collection_file.name))
            if os.path.isdir(
                os.path.join(os.path.dirname(self.collection_file.name), d)
            )
        ]
        names = [item.get("name") for item in self._collection]

        for lexicon in lexicons:
            if lexicons not in names:
                shutil.rmtree(
                    os.path.dirname(self.collection_file.name) + f"/{lexicon}"
                )

    @GObject.Property
    def collection(self) -> list:
        return self._collection


class LexiconController:
    """Controller for creating, removing and saving Pairs

    Parameters
    ----------
    lexicon_path : str
        /path/to/lexicon/file
    """

    __gtype_name__ = "LexiconController"

    def __init__(self, lexicon_path: str) -> None:
        self.lexicon_path: str = lexicon_path
        self.resources: str = os.path.dirname(lexicon_path) + "/resources"
        self.lexicon_file: TextIO = open(lexicon_path, "r+", encoding="utf-8")
        self._lexicon: list = yaml.safe_load(self.lexicon_file)

    def save_lexicon(self) -> None:
        """Saves instace lexicon to the file"""
        self.lexicon_file.seek(0)
        self.lexicon_file.truncate(0)
        yaml.dump(
            self._lexicon,
            self.lexicon_file,
            sort_keys=False,
            encoding=None,
            allow_unicode=True,
        )

    def add_pair(self, key: str) -> None:
        """Adds new pair to the instance lexicon and saves it to the file

        Parameters
        ----------
        key : str
            The key of the new pair
        """
        while (
            rnd_id := "".join(
                random.choices(string.ascii_lowercase + string.digits, k=16)
            )
        ) not in os.listdir(self.resources):
            os.mkdir(
                self.resources + f"/{rnd_id}",
            )
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
        resource_id : str
            id of the pair resources to be deleted
        """
        self.save_lexicon()
        for pair in self._lexicon:
            if pair["resources_id"] == resources_id:
                self._lexicon.remove(pair)
                return

    def undo_remove_pair(self) -> None:
        """Undoing remove action"""
        self._lexicon = yaml.safe_load(self.lexicon_file)

    def remove_garbage(self) -> None:
        """Removes resources of the deleted pair

        Called on demand, but 'Undo' action is unavailable
        """
        resources = [
            d
            for d in os.listdir(
                os.path.join(os.path.dirname(self.lexicon_path), "resources")
            )
            if os.path.isdir(
                os.path.join(os.path.dirname(self.lexicon_path), "resources", d)
            )
        ]
        res_ids = [item.get("resources_id") for item in self._lexicon]

        for resource in resources:
            if resource not in res_ids:
                shutil.rmtree(
                    os.path.dirname(self.lexicon_path) + f"/resources/{resource}"
                )
