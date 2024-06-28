# NLP tools
import re
from langdetect import detect


def verify_english(comment):
    # check if comment is in english using langdetect library
    try:
        return detect(comment) == "en"
    except:
        return False


def clean_comment(comment):
    # remove non-english characters and emojis
    comment = comment.encode("ascii", "ignore").decode("ascii")

    # remove html tags, ? is for a non-greedy match
    comment = re.sub(r"<.*?>", "", comment)

    # remove non punctuation special characters
    comment = re.sub(r"[^\w\s\.,!?;:]", "", comment)

    # Normalize whitespace
    comment = re.sub(r"\s+", " ", comment).strip()

    return comment


def preprocess_comment(comment):

    # clean comment
    comment = clean_comment(comment)

    # ensure comment is in english
    if not verify_english(comment):
        return None
    else:
        return comment
