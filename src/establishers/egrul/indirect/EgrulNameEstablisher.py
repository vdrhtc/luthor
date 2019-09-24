from enum import Enum, auto

from src.StateMachine import StateMachine


class _States(Enum):
    INIT = auto()


class EgrulNameEstablisher(StateMachine):

    def __init__(self, bot, user_id, current_schema):
        super().__init__()
        self._behaviours.update({_States.INIT: self._handle_init})
        self._schema = current_schema
        self._user_id = user_id
        self._bot = bot
        self._state = _States.INIT

    def _handle_init(self, update):
        self._bot.send_message(self._user_id, "Вам понадобится Р13001 + стр 2. Лист А")
        self._schema["P13001"]["стр.2_ЛистА"] = {}
        return True  # END

