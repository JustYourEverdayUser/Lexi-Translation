import glob
import os
import zipfile

from gi.repository import Adw

from lexi import shared


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
