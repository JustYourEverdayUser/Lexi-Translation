from typing import TextIO
from gi.repository import Adw, Gio

APP_ID: str
VERSION: str
PREFIX: str

data_dir: str

schema: Gio.Settings
state_schema: Gio.Settings

app: Adw.Application
win: Adw.ApplicationWindow
data_file: TextIO
data: dict
