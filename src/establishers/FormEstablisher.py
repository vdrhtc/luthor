
# Abstract base class for establishing needed forms in a conversation with the user
from enum import Enum, auto

from src.StateMachine import StateMachine


class States(Enum):
    INIT = auto()
    ESTABLISH = auto()
    END = auto()

class FormEstablisher(StateMachine):

    def __init__(self, bot, user_id):
        self._bot = bot
        self._user_id = user_id
        self._behaviours = {
            States.INIT: self._handle_init,
            States.END: self._handle_end}
        self._state = States.INIT

        self._schema = {}

    def _handle_init(self, update):
        pass

    def _handle_establish(self, update):
        pass

    def _handle_end(self, update):
        return self._schema
