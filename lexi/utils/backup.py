"""Methods for Lexi database Export/Import in various formats"""

import glob
import os
import pathlib
import shutil
import sqlite3
import tempfile
import uuid
import zipfile

import yaml
from gi.repository import Adw

from lexi import shared
from lexi.logging.logger import logger


def export_database(path: str) -> None:
    """
    Export the database to a zip file.

    Parameters
    ----------
    path : str
        The file path where the database backup will be saved.
    """
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as zipf:
        if os.path.exists(os.path.join(shared.data_dir, "config.yaml")):
            logger.debug("Exporting config.yaml")
            zipf.write(
                os.path.join(shared.data_dir, "config.yaml"), arcname="config.yaml"
            )

        if os.path.isdir(os.path.join(shared.data_dir, "lexicons")):
            for filename in glob.glob(
                os.path.join(shared.data_dir, "lexicons", "*yaml")
            ):
                logger.debug("Exporting lexicons/%s", pathlib.Path(filename).name)
                arcname = os.path.relpath(filename, shared.data_dir)
                zipf.write(filename, arcname=arcname)

        # pylint: disable=line-too-long
        if os.path.exists(path):
            toast = Adw.Toast(
                # Translators: DO NOT TRANSLATE TEXT WITHIN CURLY BRACKETS AND BRACKETS ITSELF
                title=_(f"Backup exported successfully: {path}"),
                button_label=_("Open"),
            )
            toast.connect("button-clicked", shared.win.open_dir, os.path.dirname(path))
            shared.win.toast_overlay.add_toast(toast)


def import_database(zip_path: str) -> None:
    """
    Import the database from a zip file.

    Parameters
    ----------
    zip_path : str
        The file path of the zip archive containing the database backup.
    """
    path = shared.data_dir
    with zipfile.ZipFile(zip_path, "r") as zipf:
        if proof_of_content(zip_path):
            if os.path.exists(path) and os.path.isdir(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            if os.path.exists(zip_path) and zipfile.is_zipfile(zip_path):
                zipf.extractall(path)
                toast = Adw.Toast(
                    title=_("Database imported successfully"),
                    timeout=10,
                )
                shared.win.loaded_lexicon = None
                shared.win.loaded_word = None
                shared.win.lexicon_scrolled_window.set_child(
                    shared.win.lexicon_not_selected
                )
                shared.win.words_bottom_bar_revealer.set_reveal_child(False)
                shared.win.set_word_rows_sensetiveness(False)
                shared.win.word_entry_row.set_text("")
                shared.win.pronunciation_entry_row.set_text("")
                shared.win.translations_list_box.remove_all()
                shared.win.examples_list_box.remove_all()
                shared.win.references_list_box.remove_all()
                shared.win.build_sidebar()
                shared.config_file = open(
                    os.path.join(shared.data_dir, "config.yaml"),
                    "r+",
                    encoding="utf-8",
                )
                shared.config = yaml.safe_load(shared.config_file)

        else:
            toast = Adw.Toast(
                title=_("Incorrect Archive!"), timeout=10, button_label=_("Why?")
            )
            toast.connect("button-clicked", incorrect_archive_panic)
        shared.win.toast_overlay.add_toast(toast)


def proof_of_content(zip_path: str) -> bool:
    """
    Verify the contents of the zip archive.

    Parameters
    ----------
    zip_path : str
        The file path of the zip archive to verify.

    Returns
    -------
    bool
        True if the archive contains the required files, False otherwise.
    """
    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, "r") as zipf:
            archive_files = zipf.namelist()

            if "config.yaml" not in archive_files:
                return False

            if not any(file.startswith("lexicons/") for file in archive_files):
                return False

            tmp_dir = tempfile.mkdtemp()
            zipf.extract("config.yaml", tmp_dir)
            with open(os.path.join(tmp_dir, "config.yaml"), "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                shutil.rmtree(tmp_dir)
                if cfg["version"] != shared.CACHEV:
                    database_version_mismatch_panic()

            return True
    logger.warning(
        "The archive %s is not a valid zip file or does not exist.", zip_path
    )
    return False


def incorrect_archive_panic(*_args) -> None:
    """Display an alert dialog for an incorrect archive."""
    # pylint: disable=line-too-long
    alert = Adw.AlertDialog(
        heading=_("Incorrect Archive!"),
        body=_(
            "This archive seems to be incorrect, since it wasn't passed proof of content challenge: no config.yaml file and/or lexicons folder inside"
        ),
    )
    alert.add_response("close", label=_("Close"))
    logger.warning("Incorrect archive alert")
    alert.present(shared.win)


def database_version_mismatch_panic() -> None:
    """Display an alert dialog for a database version mismatch."""
    # pylint: disable=line-too-long
    alert = Adw.AlertDialog(
        heading=_("Database Version Mismatch!"),
        body=_(
            "The database version in the archive does not match the current version of Lexi. Please, restart Lexi after importing this database."
        ),
    )
    alert.add_response("exit", label=_("Exit Lexi"))
    alert.set_close_response("exit")
    alert.set_default_response("exit")
    alert.connect("response", lambda *_: shared.app.on_quit_action())
    logger.warning("Database version mismatch alert")
    alert.present(shared.win)


# Memorado Export
def export_memorado_database(path: str) -> None:
    """Export Lexi database as SQLite3 Memorado compatible database

    Parameters
    ----------
    path : str
        path of the exported `.db` file
    """
    if os.path.exists(path):
        logger.debug("Removing %s since it's already exists", path)
        os.remove(path)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    logger.debug("Initializing database at %s", path)
    cursor.execute(
        """CREATE TABLE if not exists cards (
                   deck_id TEXT, front TEXT, back TEXT)"""
    )
    cursor.execute(
        """CREATE TABLE if not exists decks (deck_id TEXT,
                   name TEXT,
                   icon TEXT)"""
    )

    for lexicon in pathlib.Path(os.path.join(shared.data_dir, "lexicons")).iterdir():
        with open(str(lexicon), "r") as file:
            lexicon_data = yaml.safe_load(file)
            logger.debug("Exporting Lexicon “%s”", lexicon_data["name"])
            deck_id = str(uuid.uuid4().hex)
            cursor.execute(
                """INSERT INTO decks VALUES (
                        :deck_id, :name, :icon)""",
                {
                    "deck_id": deck_id,
                    "name": lexicon_data["name"],
                    "icon": "🤖",
                },
            )
            for word in lexicon_data["words"]:
                logger.debug(
                    "Exporting word “%s” from Lexicon “%s”",
                    word["word"],
                    lexicon_data["name"],
                )
                cursor.execute(
                    """INSERT INTO cards VALUES (
                               :deck_id, :front, :back)""",
                    {
                        "deck_id": deck_id,
                        "front": word["word"],
                        "back": ", ".join(word["translations"]),
                    },
                )
            conn.commit()
            logger.debug("Export of “%s” Lexicon completed", lexicon_data["name"])
    conn.commit()
    conn.close()
    if os.path.exists(path):
        # pylint: disable=line-too-long
        toast = Adw.Toast(
            # Translators: DO NOT TRANSLATE TEXT WITHIN CURLY BRACKETS AND BRACKETS ITSELF. Memorado is the name of the other app and SHOULDN'T be translated
            title=_(f"Memorado database exported successfully: {path}"),
            button_label=_("Open"),
        )
        toast.connect("button-clicked", shared.win.open_dir, os.path.dirname(path))
        shared.win.toast_overlay.add_toast(toast)
