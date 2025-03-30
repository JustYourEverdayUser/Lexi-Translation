from gi.repository import Gtk

from .. import shared

charset = {
    "consonants": (
        "p",
        "b",
        "t",
        "d",
        "ʈ",
        "ɖ",
        "c",
        "ɟ",
        "k",
        "ɡ",
        "q",
        "ɢ",
        "ʔ",
        "m",
        "ɱ",
        "n",
        "ɳ",
        "ɲ",
        "ŋ",
        "ɴ",
        "ʙ",
        "r",
        "ʀ",
        "ⱱ",
        "ɾ",
        "ɽ",
        "ɸ",
        "β",
        "f",
        "v",
        "θ",
        "ð",
        "s",
        "z",
        "ʃ",
        "ʒ",
        "ʂ",
        "ʐ",
        "ç",
        "ʝ",
        "x",
        "ɣ",
        "χ",
        "ʁ",
        "ħ",
        "ʕ",
        "h",
        "ɦ",
        "ɬ",
        "ɮ",
        "ʋ",
        "l",
        "ɭ",
        "ʎ",
        "ʟ",
        "j",
        "w",
        "ʍ",
        "ɰ",
        "ʔ",
    ),
    "vowels": (
        "i",
        "ɪ",
        "e",
        "ɛ",
        "æ",
        "ɑ",
        "ɒ",
        "ʌ",
        "ə",
        "ɚ",
        "ɜ",
        "ɝ",
        "ɨ",
        "ʉ",
        "ɯ",
        "ʊ",
        "u",
        "ʏ",
        "ø",
        "œ",
        "ɵ",
        "ɤ",
        "ɯ",
        "ɤ",
        "ʊ",
        "o",
        "ɔ",
        "ɑ",
        "ɒ",
    ),
    "non-pulmonic-consonants": (
        "ʘ",
        "ǀ",
        "ǃ",
        "ǂ",
        "ǁ",
        "ɓ",
        "ɗ",
        "ʄ",
        "ɠ",
        "ʛ",
        "ƥ",
        "ƭ",
        "ƈ",
        "ƙ",
        "ʠ",
    ),
    "affricates": ("t͡s", "t͡ʃ", "d͡ʒ", "t͡ɕ", "d͡ʑ", "t͡ɬ", "d͡ɮ"),
    "co-articulated-consonants": ("k͡p", "ɡ͡b", "ŋ͡m", "w"),
}


class IPAButton(Gtk.Button):
    __gtype_name__ = "IPAButton"

    def __init__(self, char: str) -> None:
        super().__init__()
        self.set_label(char)
        self.props.height_request = 50
        self.add_css_class("pill")
        self.add_css_class("image-button")


def generate_table():
    for key in charset:  # pylint: disable=consider-using-dict-items
        for symbol in charset[key]:
            button = IPAButton(symbol)
            shared.win.ipa_charset_flow_box.append(button)
            button.get_parent().set_focusable(False)
