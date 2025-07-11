from collections import namedtuple
from enum import Enum


class AnkiDatabase(Enum):
    anki2 = "collection.anki2"
    anki21 = "collection.anki21"


ApkgCollection = namedtuple('ApkgCollection', 'collection_path database_name')

B2_Kontext = ApkgCollection(
    collection_path="data/collections/German_B2_Wordlist_from_Klett_Kontext",
    database_name=AnkiDatabase.anki21
)
