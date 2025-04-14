import glob
import os
import shutil
import zipfile

from gi.repository import Adw

from lexi import shared
from lexi.ui import widgets


def export_database(path: str) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as zipf:
        if os.path.exists(os.path.join(shared.data_dir, "config.yaml")):
            zipf.write(
                os.path.join(shared.data_dir, "config.yaml"), arcname="config.yaml"
            )

        if os.path.isdir(os.path.join(shared.data_dir, "lexicons")):
            for filename in glob.glob(
                os.path.join(shared.data_dir, "lexicons", "*yaml")
            ):
                arcname = os.path.relpath(filename, shared.data_dir)
                zipf.write(filename, arcname=arcname)

        if os.path.exists(path):
            toast = Adw.Toast(
                title=_(f"Backup exported successfully: {path}"), button_label=_("Open")
            )
            toast.connect("button-clicked", shared.win.open_dir, os.path.dirname(path))
            shared.win.toast_overlay.add_toast(toast)


def import_database(zip_path: str) -> None:
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
                    title=_("Database Imported. ALL PREVIOUS FILES WERE DELETED!"),
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

        else:
            toast = Adw.Toast(
                title=_("Incorrect Archive!"), timeout=10, button_label=_("Why?")
            )
            toast.connect("button-clicked", incorrect_archive_panic)
        shared.win.toast_overlay.add_toast(toast)


def proof_of_content(zip_path: str) -> bool:
    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, "r") as zipf:
            archive_files = zipf.namelist()

            if "config.yaml" not in archive_files:
                return False

            for file in archive_files:
                if file != "config.yaml" and not file.startswith("lexicons/"):
                    return False

            return True
    return False


def incorrect_archive_panic(*_args) -> None:
    # pylint: disable=line-too-long
    alert = widgets.InfoAlert(
        heading=_("Incorrect Archive!"),
        body="This archive seems to be incorrect, since it wasn't passed proof of content challenge: no config.yaml file and/or lexicons folder inside",
    )
    alert.present(shared.win)
