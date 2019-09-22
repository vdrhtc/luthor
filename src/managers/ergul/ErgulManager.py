from src.establishers.ergul.ErgulDirectEstablisher import ErgulDirectEstablisher
from src.establishers.ergul.ErgulIndirectEstablisher import ErgulIndirectEstablisher
from src.managers.SubmissionManager import SubmissionManager, SubmissionStages


class ErgulManager(SubmissionManager):

    def __init__(self, user_id, xl_engine):
        super().__init__("ergul", user_id, xl_engine)

    def _handle_fill_or_establish(self, update):
        user_choice = update.message.text


        if user_choice == self._cm.get_string("help_submit"):
            self._establisher = ErgulIndirectEstablisher(self._user_id)
        elif user_choice == self._cm.get_string("help_fill"):
            self._establisher = ErgulDirectEstablisher(self._user_id)
        else:
            return

        self._state = SubmissionStages.ESTABLISHMENT
        self._establisher.handle_update(update)
