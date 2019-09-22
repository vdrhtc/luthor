

class StateMachine:

    def __init__(self):
        self._state = None
        self._behaviours = {}

    def handle_update(self, update):
        return self._behaviours[self._state](update)
