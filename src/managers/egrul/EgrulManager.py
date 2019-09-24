from telegram import ReplyKeyboardRemove, ReplyKeyboardMarkup

from src.establishers.egrul.EgrulDirectEstablisher import EgrulDirectEstablisher
from src.establishers.egrul.EgrulIndirectEstablisher import EgrulIndirectEstablisher
from src.fillers.egrul.EgrulFiller import EgrulFiller
from src.managers.SubmissionManager import SubmissionManager, SubmissionStages


class EgrulManager(SubmissionManager):

    def __init__(self, bot, user_id, xl_engine):
        super().__init__(bot, "egrul", user_id, xl_engine)
        self._filler = EgrulFiller(self._bot, self._user_id)

    def _handle_fill_or_establish(self, update):
        user_choice = update.message.text
        update.message.reply_text("OK!", reply_markup = ReplyKeyboardRemove())

        if user_choice == self._cm.get_string("help_submit"):
            self._establisher = EgrulIndirectEstablisher(self._bot, self._user_id)
        elif user_choice == self._cm.get_string("help_fill"):
            self._establisher = EgrulDirectEstablisher(self._bot, self._user_id)
        else:
            return

        self._state = SubmissionStages.ESTABLISHMENT
        self._establisher.handle_update(update)
