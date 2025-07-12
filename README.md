## Steps
- Download .apkg file
- Rename it as a .zip file
- Extract zip file
- Modify content as you wish
- Zip content by this commands:

`cd folder_name`

`zip -r ../my_new_deck.apkg *`

## TODOs
- Improve README file
- TTS options
  - Use Piper for TTS, FREE, Local on your machine
    - https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_HTTP.md
  - Amazon, 12 MONTHS FREE, 5M characters per month
    - https://aws.amazon.com/free/machine-learning/?trk=23ccddbd-d7fb-40a8-9906-df8c7c4ad8c0&sc_channel=ps&ef_id=EAIaIQobChMI3K-zv5S3jgMVibKDBx2R8jcGEAAYAiAAEgIPK_D_BwE:G:s&s_kwcid=AL!4422!3!645251324771!p!!g!!text%20to%20voice%20software!19579658393!146073071220&gad_campaignid=19579658393&gbraid=0AAAAADjHtp8uI4-H67-UagyHfOKT-hPdL&gclid=EAIaIQobChMI3K-zv5S3jgMVibKDBx2R8jcGEAAYAiAAEgIPK_D_BwE
  - Speechify, Simba: Text to Speech API
    - 300ms latency, human quality, $10 per 1M chars, every language you need.
    - https://speechify.com/text-to-speech-api/?utm_campaign=search-gamma-USD&utm_content=reader&utm_source=google&utm_medium=cpc&utm_term=text+reader&gc_id=21365183410&h_ad_id=701683193405&gad_source=1&gad_campaignid=21365183410&gbraid=0AAAAAogD2qCGb8We3rcXI7Sxnp82smNCg&gclid=EAIaIQobChMI3K-zv5S3jgMVibKDBx2R8jcGEAAYBCAAEgI6VPD_BwE
- Download a wiktionary dump
  - https://dumps.wikimedia.org/backup-index-bydb.html
    - E.g. https://dumps.wikimedia.org/dewiktionary/20250701/
- Download https://www.dwds.de/
  - https://www.dwds.de/d/api#wb-list
- Generate image with
  - https://github.com/thiswillbeyourgithub/AnkiAIUtils

## Resources
- Extracting data from Goethe Zertifikat B1 Wortliste pdf
    - https://github.com/aringq10/b1-goethe-anki-deck
    - https://wejn.org/2023/12/extracting-data-from-goethe-zertifikat-b1-wortliste


## Stats for B2_Kontext
```
words per minute: 4.8
estimated time: ~8h
----------------------------------------
en_meaning           1223.0 9.2 % =
frequency            797.0 6.0 % =
cefr_level           751.0 5.6 % =
part_of_speech       468.0 3.5 % 
de_meaning           1821.0 13.7% ==
de_synonyms          2841.0 21.4% ====
fa_meaning           1562.0 11.7% ==
de_example_sentence  3072.0 23.1% ====
perfekt_präteritum   766.0 5.8 % =
```

```
total time: 5h 19m 33s
words per minute: 7.3
----------------------------------------
de_example_sentence_fa 14573.0 76.0% ===============
de_meaning_fa        4601.0 24.0% ====
----------------------------------------

```