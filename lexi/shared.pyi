from gi.repository import Gio

from lexi.main import LexiApplication
from lexi.window import LexiWindow

APP_ID: str
VERSION: str
PREFIX: str

data_dir: str

schema: Gio.Settings
state_schema: Gio.Settings

app: LexiApplication
win: LexiWindow
