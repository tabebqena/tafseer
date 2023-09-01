import re
import sys
from sql30 import db

import csv
from pyarabic.araby import strip_diacritics


# Constrants
SHEET_PATH = "replacement.csv"


# The writer class, used for writing the replacemnet CSV sheet
class Writer:
    def __init__(self) -> None:
        self.path = SHEET_PATH
        self.header = [
            "sura",
            "aya",
            "sentence",
            "replace_string",
            "found",
            "equal_length",
            "approved",
            "imlai_no_sign",
            "imlai_sign",
            "uthmani",
        ]
        self.writer = csv.writer(open(self.path, "w"))
        self.writer.writerow(self.header)

    def write_row(
        self,
        sura,
        aya,
        sentence,
        replace_string,
        found,
        equal_length,
        approved,
        imlai_no_sign,
        imlai_sign,
        uthmani,
    ):
        self.writer.writerow(
            [
                sura,
                aya,
                sentence,
                replace_string,
                found,
                equal_length,
                approved,
                imlai_no_sign,
                imlai_sign,
                uthmani,
            ]
        )


# End of the writer class


# The method used for searchinng for a sentense in another
def find(sentense, text):
    """a special search method, used for finding the first match of a sentense in text
    returns list of two items:
    - The first item is the start of the match.
    - The last item : is the end of the match."""
    text_words = text.split()
    text_word_count = len(text_words)
    sentense_words = sentense.split()
    sentense_word_count = len(sentense_words)

    for x, word1 in enumerate(sentense_words):
        # print("x ", x, word1)
        for z, word2 in enumerate(text_words):
            if word1 == word2:
                # check the rest of the substring
                if (
                    sentense_words[1:]
                    == text_words[z + 1 : z + 1 + (sentense_word_count - 1)]
                ):
                    indexes = [z, z + sentense_word_count - 1]
                    return indexes


# Db models ,
# Each model resemle table in database,
# the table name is the `TABLE` property of  the calss
# The database name & path is the `db_name` of the DB_SCHEMA property.


class ImlaiVersesNoSigns(db.Model):
    """All quran ayas on imlai with no signs
    example: الحمد لله رب العالمين
    """

    TABLE = "verses"
    # PKEY =
    DB_SCHEMA = {
        "db_name": "./uthmani.v2.db",
        "tables": [
            {
                "name": TABLE,
                "fields": {
                    "sura": "int",
                    "ayah": "int",
                    "text": "text",
                    "primary": "int",
                },
            }
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = self.TABLE


class ImlaiVersesWithSigns(db.Model):
    """All quran ayas on imlai with signs
    example: مَالِكِ يَوْمِ الدِّينِ
    """

    TABLE = "arabic_text"
    # PKEY =
    DB_SCHEMA = {
        "db_name": "./quran.ar.db",
        "tables": [
            {
                "name": TABLE,
                "fields": {
                    "sura": "int",
                    "ayah": "int",
                    "text": "text",
                },
            }
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = self.TABLE


class UthmaniVersesWithSigns(db.Model):
    """All quran ayas Uthmani  with signs
    example: مَٰلِكِ يَوۡمِ ٱلدِّينِ
    """

    TABLE = "arabic_text"
    # PKEY =
    DB_SCHEMA = {
        "db_name": "./uthmani.v2.db",
        "tables": [
            {
                "name": TABLE,
                "fields": {
                    "sura": "int",
                    "ayah": "int",
                    "text": "text",
                },
            }
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = self.TABLE


class ImlaiUthmaniAya(db.Model):
    """New table include the imlai to uthmani aya"""

    TABLE = "imlai_uthmani_aya"
    DB_SCHEMA = {
        "db_name": "./alsa3dy_v2.db",
        "tables": [
            {
                "name": TABLE,
                "fields": {
                    "sura": "int",
                    "ayah": "int",
                    "imlai_sign": "text",
                    "imlai_no_sign": "text",
                    "uthmani_sign": "text",
                },
            }
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = self.TABLE

    def create(self, tbl=None, **kwargs):
        return super().create(tbl, **kwargs)

    def create_table(self, schema):
        rv = super().create_table(schema)
        self.commit()
        return rv

    # def create_table(self, ):
    #     return super().create_table(self.DB_SCHEMA['tables'][0])


class Tafseer(db.Model):
    """Tafseer alsaady of each aya
    The aya words is enclosed in {}
    mostly the aya words are with signs
    """

    TABLE = "contents_api"
    DB_SCHEMA = {
        "db_name": "./alsa3dy_v2.db",
        "tables": [
            {
                "name": TABLE,
                "fields": {
                    "id": "int",
                    "tafsir_id": "int",
                    "sura": "int",
                    "aya": "int",
                    "cnt": "text",
                    "cnt_v2": "text",
                    "intro": "text",
                    "conclusion": "text",
                    "footnotes": "text",
                    "extra": "text",
                    "repeated": "text",
                },
                "primary_key": "id",
            }
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = self.TABLE


class DifferentWords(db.Model):
    # Actually not used on tha last version....
    TABLE = "words"
    DB_SCHEMA = {
        "db_name": "./alsa3dy_v2.db",
        "tables": [
            {
                "name": "words",
                "fields": {
                    "id": "int",
                    "sura": "int",
                    "aya": "int",
                    "word": "text",
                    "word_no_signs": "text",
                    "uthmani_word": "text",
                },
                "primary_key": "id",
            }
        ],
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.table = self.TABLE

    def write_diff_word(sura, aya, word, word_no_sign, uthmani_word):
        DifferentWords.write(
            susa=sura,
            aya=aya,
            word=word,
            word_no_sign=word_no_sign,
            uthmani_word=uthmani_word,
        )


# End of Database models


def build_imlai_uthmani_table():
    """
    build the imlai_uthmani_aya table (collecting it from the three tables)
    this table contains:
    - sura
    - aya
    - imlai_no_sign: The aya text in the imlai font with no signs
    - imlai_sign: The aya text in the imlai font with  signs
    - uthmani : The aya text in the Uthmani font with signs

    """
    im = ImlaiVersesNoSigns()
    ims = ImlaiVersesWithSigns()
    u = UthmaniVersesWithSigns()
    imsu = ImlaiUthmaniAya()
    nosigns = im.read()

    for aya in nosigns:
        sura = aya[0]
        aya_id = aya[1]
        aya_text_no_sign = aya[2]
        aya_text_with_sign = ims.read(
            sura=sura,
            ayah=aya_id,
        )[
            0
        ][2]
        uthmani_text = u.read(
            sura=sura,
            ayah=aya_id,
        )[
            0
        ][2]
        imsu.write(
            sura=sura,
            ayah=aya_id,
            imlai_sign=aya_text_with_sign,
            imlai_no_sign=aya_text_no_sign,
            uthmani_sign=uthmani_text,
        )
        imsu.commit()


def build_replacement_sheet():
    """
    Build a replacement sheet, it contains the following columns (see `Writer` also):
    - sura,
    - aya,
    - original_sentense: The complete sentense as written in the tafseer.
    - replace_string : The string that needs replacement based on our search criteria,
    - found,
                equal_length,
                approved,
                imlai,
                imlai_sign,
                uthmani,
    """
    imsu = ImlaiUthmaniAya()
    all_count = 0
    found_count = 0
    notfound_count = 0
    unequalLength_count = 0
    writer = Writer()
    pattern = re.compile(r"{(.+?)}")
    tafseer = Tafseer().read()
    for taf in tafseer:
        # The sure code -int-
        sura = taf[2]
        #  The aya code -int-
        aya = taf[3]
        cnt = taf[4]
        aya_fonts = imsu.read(
            sura=sura,
            ayah=aya,
        )[0]
        # The imlai fonts of the aya
        imlai = aya_fonts[3].strip()
        #  The imlai font of the aya with signs
        imlai_sign = aya_fonts[2].strip()
        #  The uthmani font of the aya
        uthmani = aya_fonts[4].strip()
        # search for all sentenses that match {SOME_THING}
        in_brackets = re.findall(pattern, cnt)
        for sentense in in_brackets:
            all_count += 1
            original_sentense = sentense
            # strip all tashkeel & small Alef from the sentense.
            sentense = strip_diacritics(sentense.strip())
            # strip all diacritics from the imlai_sign aya
            imlai_sign = strip_diacritics(imlai_sign)
            # Is the sentense in  imlai_sign aya (Note that we search after strip_diacritics)
            match = find(sentense, imlai_sign)
            found = 0
            equal_length = 0
            approved = 0
            replace_string = ""
            if match:
                found = 1
                found_count += 1
                # Now, we should compare the imlai_sign sentense with its counter uthmani
                # This step to avoid replacing sentence with a completely different one or shifting its start.
                # Note that it has false positive & false negative results.
                # But I choose to depnd on t.
                imlai_sign_words = imlai_sign.split()
                uthmani_words = uthmani.split()

                if len(imlai_sign_words) == len(uthmani_words):
                    # concentate the replace_string now, using the
                    # indexes returned by the `find` method.
                    # Now, we know that the replace_string
                    # is the string (in uthmani) that has the same indexes of the original string (in imlai)
                    replace_string = " ".join(uthmani_words[match[0] : match[1] + 1])
                    equal_length = 1
                else:
                    unequalLength_count += 1
            else:
                notfound_count += 1
            writer.write_row(
                sura,
                aya,
                original_sentense,
                replace_string,
                found,
                equal_length,
                approved,
                imlai,
                imlai_sign,
                uthmani,
            )
    print(
        "All: ",
        all_count,
        " Found: ",
        found_count,
        "Unequal length: ",
        unequalLength_count,
        " NoFound: ",
        notfound_count,
    )


HELP_MESSAGE = f"""Usage python3 main.py <COMMAND>
The avialable commands are:

table: {build_imlai_uthmani_table.__doc__}\n
sheet: {build_replacement_sheet.__doc__}\n
help: print this message
"""

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        raise RuntimeError(
            "You should pass a valid command. `help` to print allcommands "
        )
    command = args[1]
    if command == "table":
        build_imlai_uthmani_table()

    elif command == "sheet":
        build_replacement_sheet()
    elif command == "help":
        print(HELP_MESSAGE)
    else:
        print("Invalid command")
        print(HELP_MESSAGE)
        sys.exit(1)
