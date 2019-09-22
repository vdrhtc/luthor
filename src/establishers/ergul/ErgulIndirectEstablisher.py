from enum import Enum, auto

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.ConstantsManager import ConstantsManager
from src.StateMachine import StateMachine
from src.establishers.FormEstablisher import FormEstablisher


class ErgulIndirectStates(Enum):
    CHOOSING_CHANGES = auto()


class _Changes(Enum):
    NAME = auto()
    CHARTER_TO_CIVIL_CODE = auto()
    OTHER_CHARTER = auto()
    OKVAD = auto()
    LEGAL_ADDRESS = auto()
    SHARE_CAPITAL = auto()
    PARTICIPANTS_ONLY = auto()
    DIRECTOR = auto()
    ERGUL_ERRORS = auto()


class ErgulIndirectEstablisher(FormEstablisher):

    def __init__(self, user_id):
        super().__init__(user_id)
        self._behaviours.update({
            ErgulIndirectStates.CHOOSING_CHANGES: self._handle_choice
        })
        self._chosen_changes = []
        self._cm = ConstantsManager(subcategory="ergul_indirect_establisher")

    def _handle_init(self, update):
        callback_keyboard = [[InlineKeyboardButton("LOL", callback_data="LOL!!!")]]

        update.message.reply_text(self._cm.get_string("init"),
                                  reply_markup=InlineKeyboardMarkup(callback_keyboard))

        self._state = ErgulIndirectStates.CHOOSING_CHANGES

    def _handle_choice(self, update):
        update.callback_query.bot.send_message(self._user_id, update.callback_query.data)
        self._state = ErgulIndirectStates.CHOOSING_CHANGES