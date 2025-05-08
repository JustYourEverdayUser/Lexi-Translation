from typing import TextIO

from gi.repository import Gio

from lexi.main import LexiApplication
from lexi.utils.backend import LexiconController
from lexi.window import LexiWindow

APP_ID: str
VERSION: str
PREFIX: str
CACHEV: int

data_dir: str
cache_dir: str

schema: Gio.Settings
state_schema: Gio.Settings

app: LexiApplication
win: LexiWindow
lexictrl: LexiconController
config_file: TextIO
config: dict[int, list[str]]

# Handler IDs for connections
handler_ids: dict[str, int]
