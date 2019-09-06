from enum import Enum, auto

from src.establishers.FormEstablisher import FormEstablisher

class ErgulEstablisher(FormEstablisher):

    def __init__(self, user_id):
        super().__init__(user_id)

    def _handle_establish_raw(self, update):
        pass

    def _handle_establish(self, update):
        pass




