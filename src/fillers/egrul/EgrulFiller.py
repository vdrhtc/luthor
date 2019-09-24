from enum import Enum, auto

from src.ConstantsManager import ConstantsManager
from src.fillers import FormFiller


class States(Enum):
    INIT = auto()
    QUESTIONING = auto()


class EgrulFiller(FormFiller):

    def __init__(self, bot, user_id):
        super().__init__(bot, "egrul", user_id)
        self._behaviours.update({States.INIT: self._handle_init,
                                 States.QUESTIONING: self._handle_questioning})
        self._cm = ConstantsManager(subcategory="egrul_filler")

    def _handle_init(self, update):
        self._bot.send_message(self._user_id, self._cm.get_string("init"))

        form_id, sheet_id, field_id = self._questions[self._current_question]
        self._bot.send_message(self._user_id,
                               self._cm.get_string("field_request") % (form_id, sheet_id, field_id))
        self._current_question += 1

    def _handle_questioning(self, update):

        form_id, sheet_id, field_id = self._questions[self._current_question]
        self._collected_info[form_id][sheet_id][field_id] = update.message.text

        form_id, sheet_id, field_id = self._questions[self._current_question]
        self._bot.send_message(self._user_id,
                               self._cm.get_string("field_request") % (form_id, sheet_id, field_id))
        self._current_question += 1