from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

from . import checkParams
from . import formatFronts
from . import getUnprocessed
from . import defineWordsAPI
from . import applyDefinitions


class DeckDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Deck Setup")

        layout = QVBoxLayout(self)

        # Deck name field
        layout.addWidget(QLabel("Deck name:"))
        self.deck_name_edit = QLineEdit(self)
        self.deck_name_edit.setText("English")
        layout.addWidget(self.deck_name_edit)

        # Notes limit field
        layout.addWidget(QLabel("Amount of notes to define:"))
        self.notes_limit_spin = QSpinBox(self)
        self.notes_limit_spin.setMinimum(1)
        self.notes_limit_spin.setValue(50)
        layout.addWidget(self.notes_limit_spin)

        # Model name field
        layout.addWidget(QLabel("Model name:"))
        self.model_name_edit = QLineEdit(self)
        self.model_name_edit.setText("gemma-3n-e4b-it")
        layout.addWidget(self.model_name_edit)

        # Concurrent requests limit
        layout.addWidget(QLabel("Concurrent API calls limit:"))
        self.concurrent_spin = QSpinBox(self)
        self.concurrent_spin.setMinimum(1)
        self.concurrent_spin.setValue(25)
        layout.addWidget(self.concurrent_spin)

        # OK/Cancel buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

    def get_values(self):
        return (
            self.deck_name_edit.text(),
            self.notes_limit_spin.value(),
            self.concurrent_spin.value(),
            self.model_name_edit.text(),
        )


# the actual process to be run in background
def processing():
    formatFronts.main(mw, deckName)
    notes, unprocessedWords = getUnprocessed.main(mw, deckName, notesLimit)
    definedWords = defineWordsAPI.main(unprocessedWords, modelName, rateLimit)
    applyDefinitions.main(mw, notes, definedWords)


# taskman.run_in_background() wants its second argument (function) to have an argument
def reportFinish(blam):
    showInfo("DONE")


# UI button listener, starting the process in background
def startDialog() -> None:
    dialog = DeckDialog(mw)
    if dialog.exec():
        global deckName, notesLimit, rateLimit, modelName
        deckName, notesLimit, rateLimit, modelName = dialog.get_values()

        if mw.col.decks.by_name(deckName) is None:
            showInfo("Wrong deck name")
            return

        paramsCode = checkParams.main(modelName)
        if paramsCode == 404:
            showInfo("Wrong model name")
            return

        if paramsCode == 1000:
            showInfo("Incorrect API key")
            return

        mw.taskman.run_in_background(processing, reportFinish)


deckName = ""
notesLimit = 0
rateLimit = 0
modelName = ""

# creating a button and connecting a listener to it
action = QAction("Define words with Gemini", mw)
qconnect(action.triggered, startDialog)
mw.form.menuTools.addAction(action)
