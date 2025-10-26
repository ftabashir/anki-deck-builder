from collections import namedtuple
from enum import Enum


class AnkiDatabase(Enum):
    anki2 = "collection.anki2"
    anki21 = "collection.anki21"


ApkgCollection = namedtuple('ApkgCollection', 'collection_path database_name')

B2_Kontext = ApkgCollection(
    collection_path="data/collections/German_B2_Wordlist_from_Klett_Kontext",
    database_name='collection.anki21'
)

B2_Kontext_Words_Meanings_Examples = ApkgCollection(
    collection_path="data/collections/B2_Kontext_Words|Meanings|Examples",
    database_name='collection.anki2'
)

B1_plus_Kontext = ApkgCollection(
    collection_path="data/collections/b1_plus",
    database_name='collection.anki2'
)
B2 = ApkgCollection(
    collection_path="data/collections/b2",
    database_name='collection.anki2'
)

B2_mitpräpositionen = ApkgCollection(
    collection_path="data/collections/b2_mitpräpositionen",
    database_name='collection.anki2'
)