from gi.repository import Adw, Gio

from lexi.utils.Controllers import CollectionsController

APP_ID: str
VERSION: str
PREFIX: str

data_dir: str

schema: Gio.Settings
state_schema: Gio.Settings

app: Adw.Application
win: Adw.ApplicationWindow
collection_controller: CollectionsController
