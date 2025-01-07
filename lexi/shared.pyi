from gi.repository import Adw, Gio

APP_ID: str
VERSION: str
PREFIX: str

schema: Gio.Settings
state_schema: Gio.Settings

app: Adw.Application
win: Adw.ApplicationWindow