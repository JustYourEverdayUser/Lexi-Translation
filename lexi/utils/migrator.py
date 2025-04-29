import os
from pathlib import Path

import yaml

from lexi import shared
from lexi.logging.logger import logger


def migrate_v2() -> None:
    # Migrate main app config
    logger.info("Migrating config file to v2")
    config: dict = shared.config
    config.pop("filter-types")
    config["word-types"] = [
        "Noun",
        "Verb",
        "Adjective",
        "Adverb",
        "Pronoun",
        "Preposition",
        "Conjunction",
        "Interjection",
        "Article",
        "Idiom",
        "Clause",
        "Prefix",
        "Suffix",
    ]
    config["enabled-types"] = []
    config["word-types"].sort()

    # Migrate lexicons
    logger.info("Migrating lexicons to v2")
    for file in Path(os.path.join(shared.data_dir, "lexicons")).iterdir():
        lexicon = open(str(file), "r+", encoding="utf-8")
        lexicon_data = yaml.safe_load(lexicon)
        for index, word in enumerate(lexicon_data["words"]):
            existed_types = [key for key, value in word["types"].items() if value]
            lexicon_data["words"][index]["types"] = existed_types
            word["tags"] = []
        lexicon.seek(0)
        lexicon.truncate(0)
        yaml.dump(
            lexicon_data, lexicon, sort_keys=False, encoding=None, allow_unicode=True
        )
        lexicon.close()

    # Bump version of the config file
    config["version"] = 2
    shared.config_file.seek(0)
    shared.config_file.truncate(0)
    yaml.dump(
        config,
        shared.config_file,
        sort_keys=False,
        encoding=None,
        allow_unicode=True,
    )
    logger.info("Migration to v2 completed")
