
# Abstract base class for establishing needed forms in a conversation with the user
from enum import Enum, auto


class EstablishmentStages(Enum):
    INIT = auto()
    ESTABLISH_RAW = auto()
    ESTABLISH = auto()
    END = auto()

class FormEstablisher:

    def __init__(self, user_id):
        self._user_id = user_id
        self._behaviours = {EstablishmentStages.INIT: self._handle_init,
                            EstablishmentStages.ESTABLISH_RAW: self._handle_establish_raw,
                            EstablishmentStages.ESTABLISH: self._handle_establish}
        self._state = EstablishmentStages.INIT
        self._mode = None

        self._schema = {}

    def handle_update(self, update):
        return self._behaviours[self._state](update)

    def set_mode(self, mode: EstablishmentStages):
        self._mode = mode

    def _handle_init(self, update):
        self._state = self._mode
        return self.handle_update()

    def _handle_establish_raw(self, update):
        pass

    def _handle_establish(self, update):
        pass
