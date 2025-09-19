def main(mw, deckName, notesLimit):
    deck_id = mw.col.decks.by_name(deckName)["id"]
    card_ids = mw.col.find_cards(f"did:{deck_id}")

    counter = 0
    notes = []
    unprocessedWords = []
    for card_id in card_ids:
        note = mw.col.get_card(card_id).note()
        if (len(note["Back"]) < 300): # not already defined
            notes.append(note)
            unprocessedWords.append(note["Front"])
            counter += 1
            
            if (notesLimit <= counter):
                break

    return notes, unprocessedWords
