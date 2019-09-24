from enum import Enum, auto

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.StateMachine import StateMachine
from src.establishers.FormEstablisher import FormEstablisher


class _States(Enum):
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
    EGRUL_ERRORS = auto()


class EgrulDirectEstablisher(FormEstablisher):

    def __init__(self):
        self._behaviours = {}
        self._egrul_changes = []
        self._schema = {}

    def _handle_enter(self, update):
        pass