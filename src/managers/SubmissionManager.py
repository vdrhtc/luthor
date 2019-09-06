import json
from enum import auto, Enum

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

from src.ConstantsManager import ConstantsManager
from src.establishers.FormEstablisher import FormEstablisher, EstablishmentStages


class SubmissionStages(Enum):
    INIT = auto()
    Q_FILL_OR_ESTABLISH = auto()
    ESTABLISHMENT = auto()
    FILLING = auto()
    CLEAR = auto()
    EXIT = auto()

# Abstract class for general management of the user's submission

class SubmissionManager:

    def __init__(self, submission_id, user_id, xl_engine):
        self._form_id = submission_id
        self._user_id = user_id
        self._xl_engine = xl_engine
        self._cm = ConstantsManager(subcategory="form_manager")

        with open("resources/form_db.json") as f:
            self._schema = json.load(f)[submission_id]["schema"]

        self._collected_info = self._init_collected_info()

        self._behaviours = {SubmissionStages.INIT: self._handle_enter,
                            SubmissionStages.Q_FILL_OR_ESTABLISH: self._handle_fill_or_establish,
                            SubmissionStages.ESTABLISHMENT: self._handle_start_edit,  # must be overridden
                            SubmissionStages.FILLING: self._handle_filling,
                            SubmissionStages.CLEAR: self._handle_clear,
                            SubmissionStages.EXIT: self._handle_exit}

        self._establisher = None
        self._filler = None

        self._state = SubmissionStages.INIT

    def get_form_id(self):
        return self._form_id

    def _init_collected_info(self):
        collected_info = {}
        for sheet_id in self._schema:
            sheet = {}
            for field_id in self._schema[sheet_id]:
                sheet[field_id] = None
            collected_info[sheet_id] = sheet
        return collected_info

    def handle_update(self, update):
        return self._behaviours[self._mode][self._state](update)

    def _handle_enter(self, update):

        reply_keyboard = [[self._cm.get_string("help_submit")],
                          [self._cm.get_string("help_fill")]]

        update.message.reply_text(self._cm.get_string("submission_help"),
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))

        self._state = SubmissionStages.Q_FILL_OR_ESTABLISH

    def _handle_fill_or_establish(self, update):
        user_choice = update.message.text

        if user_choice == self._cm.get_string("help_submit"):
            self._establisher.set_mode(EstablishmentStages.ESTABLISH)
        elif user_choice == self._cm.get_string("help_fill"):
            self._establisher.set_mode(EstablishmentStages.ESTABLISH_RAW)

        self._establisher.handle_update(update)

        self._state = SubmissionStages.ESTABLISHMENT

    def _handle_establishment(self, update):
        schema = self._establisher.handle_update(update)

        if schema is not None:
            self._schema = schema
            self._state = SubmissionStages.FILLING

    def _handle_filling(self, update):
        pass

    def _handle_exit(self, update):
        return ConversationHandler.END

    def finalize(self):
        try:
            return self._xl_engine.generate(self._user_id, self._form_id, self._collected_info)
        except ValueError as e:
            return str(e)

    def _handle_clear(self, update):
        return ConversationHandler.END
