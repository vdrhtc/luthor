import json
from enum import auto, Enum

from telegram import ReplyKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler

from src.ConstantsManager import ConstantsManager
from src.Formatter import Formatter
from src.StateMachine import StateMachine
from src.establishers.FormEstablisher import FormEstablisher, States


class SubmissionStages(Enum):
    INIT = auto()
    Q_FILL_OR_ESTABLISH = auto()
    ESTABLISHMENT = auto()
    FILLING = auto()
    CLEAR = auto()
    EXIT = auto()


# An abstract class for general management of the user's submission

class SubmissionManager(StateMachine):

    def __init__(self, bot, submission_id, user_id, xl_engine):
        self._bot = bot
        self._form_id = submission_id
        self._user_id = user_id
        self._xl_engine = xl_engine
        self._cm = ConstantsManager(subcategory="form_manager")

        self._collected_info = None

        self._behaviours = {SubmissionStages.INIT: self._handle_init,
                            SubmissionStages.Q_FILL_OR_ESTABLISH: self._handle_fill_or_establish,
                            # must be overridden
                            SubmissionStages.ESTABLISHMENT: self._handle_establishment,
                            SubmissionStages.FILLING: self._handle_filling,
                            SubmissionStages.CLEAR: self._handle_clear}

        self._establisher = None
        self._filler = None

        self._state = SubmissionStages.INIT

    def _handle_init(self, update):
        reply_keyboard = [[self._cm.get_string("help_submit")],
                          [self._cm.get_string("help_fill")]]

        update.message.reply_text(self._cm.get_string("submission_help"),
                                  reply_markup=ReplyKeyboardMarkup(
                                      reply_keyboard,
                                      one_time_keyboard=True))
        self._state = SubmissionStages.Q_FILL_OR_ESTABLISH

    def _handle_fill_or_establish(self, update):
        pass  # has to be overridden

    def _handle_establishment(self, update):
        schema = self._establisher.handle_update(update)

        if schema is not None:
            self._schema = schema
            f = Formatter()
            self._bot.send_message(self._user_id,
                                   'DEBUG Established schema:\n```%s```' % f(self._schema),
                                   parse_mode=ParseMode.MARKDOWN)
            self._state = SubmissionStages.FILLING
            self._filler.init_collected_info(self._schema)  # TODO: Do we need both schema and collected info?
            return self.handle_update(update)

    def _handle_filling(self, update):
        result = self._filler.handle_update(update)
        if result:
            return self._finalize()

    def _finalize(self):
        try:
            return self._xl_engine.generate(self._user_id, self._form_id, self._collected_info)
        except ValueError as e:
            return str(e)

    def _handle_clear(self, update):
        return ConversationHandler.END
