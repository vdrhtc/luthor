import json
from enum import auto, Enum

from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

from src.ResourceManager import ResourceManager

class FormManagerStages(Enum):
    ENTER = auto()
    ACTION = auto()
    START_EDIT = auto()
    CLEAR = auto()
    EXIT = auto()

class FormManager:

    def __init__(self, form_id, user_id, xl_engine):
        self._form_id = form_id
        self._user_id = user_id
        self._xl_engine = xl_engine
        self._rm = ResourceManager(subcategory="form_manager")

        with open("resources/form_db.json") as f:
            self._schema = json.load(f)[form_id]["schema"]

        self._collected_info = self._init_collected_info()

        self._behaviours = {FormManagerStages.ENTER: self._handle_enter,
                            FormManagerStages.ACTION: self._handle_action,
                            FormManagerStages.EXIT: self._handle_exit,
                            FormManagerStages.START_EDIT: self._handle_start_edit}  # must be overridden

        self._actions = {"continue": FormManagerStages.START_EDIT,
                         "clear": FormManagerStages.CLEAR,
                         "exit": FormManagerStages.EXIT}

        self._action_commands = {self._rm.get_string(action):action for action in
                                 self._actions.keys()}

        self._state = FormManagerStages.ENTER

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
        return self._behaviours[self._state](update)

    def _handle_enter(self, update):
        message = self._rm.get_string("hi") % (self._form_id, str(self._collected_info))
        update.message.reply_text(message)

        message = self._rm.get_string("what_to_do")
        reply_keyboard = [[self._rm.get_string("continue"),
                           self._rm.get_string("clear"),
                           self._rm.get_string("exit")]]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(message, reply_markup = reply_markup)

        self._state = FormManagerStages.ACTION

    def _handle_action(self, update):
        user_action = update.message.text

        try:
            command = self._action_commands[user_action]
        except KeyError:
            update.message.reply_text("Bad command!")
        else:
            self._state = self._actions[command]
            self.handle_update(update)

    def _handle_exit(self, update):
        return ConversationHandler.END

    def finalize(self):
        try:
            return self._xl_engine.generate(self._user_id, self._form_id, self._collected_info)
        except ValueError as e:
            return e.message

    def _handle_start_edit(self, update):
        pass
