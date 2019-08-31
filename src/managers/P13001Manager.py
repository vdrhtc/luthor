from enum import Enum, auto

from telegram.ext import ConversationHandler

from src.managers.FormManager import FormManager, FormManagerStages

class P13001Stages(Enum):
    QUESTION = auto()

class P13001Manager(FormManager):

    def __init__(self, user_id, xl_engine):
        super().__init__("P13001", user_id, xl_engine)
        self._behaviours.update({P13001Stages.QUESTION: self._handle_questioning})
        self._current_question = 0
        self._questions = []

    def _handle_start_edit(self, update):

        for sheet_id in self._collected_info.keys():
            for field_id in self._collected_info[sheet_id].keys():
                if self._collected_info[sheet_id][field_id] is None:
                    self._questions.append((sheet_id, field_id))

        self._state = P13001Stages.QUESTION

        sheet_id, field_id = self._questions[self._current_question]
        update.message.reply_text("Provide %s for sheet %s"%(field_id, sheet_id))

    def _handle_questioning(self, update):
        sheet_id, field_id = self._questions[self._current_question]
        self._collected_info[sheet_id][field_id] = update.message.text

        self._current_question += 1
        try:
            sheet_id, field_id = self._questions[self._current_question]
        except IndexError:
            update.message.reply_text("Filling is done")
            return self.finalize()
        else:
            update.message.reply_text("Provide %s for sheet %s"%(field_id, sheet_id))




