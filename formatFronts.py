import re


def main(mw, deckName):
    # removing html characters; repeating, starting and trailing spaces
    # bringing to lowercase
    html_pattern = re.compile(r"<[^>]+>")
    entity_pattern = re.compile(r"&[a-z]+;")
    word_pattern = re.compile(r"[^\W_]+")

    deck_id = mw.col.decks.by_name(deckName)["id"]
    card_ids = mw.col.find_cards(f"did:{deck_id}")

    for card_id in card_ids:
        note = mw.col.get_card(card_id).note()

        text_only = html_pattern.sub(" ", note["Front"])
        text_only = entity_pattern.sub(" ", text_only)
        words = word_pattern.findall(text_only)
        cleaned = " ".join(words).lower()

        note["Front"] = cleaned
        mw.col.update_note(note)
