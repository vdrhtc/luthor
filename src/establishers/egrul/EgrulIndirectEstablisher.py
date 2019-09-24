from enum import Enum, auto

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from src.ConstantsManager import ConstantsManager
from src.Formatter import Formatter
from src.StateMachine import StateMachine
from src.establishers.FormEstablisher import FormEstablisher, States
from src.establishers.egrul.indirect.EgrulCharterToCCEstablisher import EgrulCharterToCCEstablisher
from src.establishers.egrul.indirect.EgrulNameEstablisher import EgrulNameEstablisher


class _EgrulIndirectStates(Enum):
    CHOOSING_CHANGES = auto()
    PROCESSING_CHANGES = auto()


class _Changes(Enum):
    NAME = 0
    CHARTER_TO_CIVIL_CODE = 1
    OTHER_CHARTER = 2
    OKVAD = 3
    LEGAL_ADDRESS = 4
    SHARE_CAPITAL = 5
    PARTICIPANTS_ONLY = 6
    DIRECTOR = 7
    EGRUL_ERRORS = 8


class EgrulIndirectEstablisher(FormEstablisher):
    NAMES = {
        _Changes.NAME: "Название",
        _Changes.CHARTER_TO_CIVIL_CODE: "Устав (для соответствия с новой редакцией ГК)",
        _Changes.OTHER_CHARTER: "Устав (иные изменения)",
        _Changes.OKVAD: "ОКВЭД",
        _Changes.LEGAL_ADDRESS: "Юридический адрес",
        _Changes.SHARE_CAPITAL: "Уставный капитал",
        _Changes.PARTICIPANTS_ONLY: "Состав участников без изменения уставного капитала",
        _Changes.DIRECTOR: "Директора организации",
        _Changes.EGRUL_ERRORS: "Ошибки в ЕГРЮЛ"}

    ESTABLISHERS = {
        _Changes.NAME: EgrulNameEstablisher,
        _Changes.CHARTER_TO_CIVIL_CODE: EgrulCharterToCCEstablisher,
        _Changes.OTHER_CHARTER: EgrulNameEstablisher,
        _Changes.OKVAD: EgrulNameEstablisher,
        _Changes.LEGAL_ADDRESS: EgrulNameEstablisher,
        _Changes.SHARE_CAPITAL: EgrulNameEstablisher,
        _Changes.PARTICIPANTS_ONLY: EgrulNameEstablisher,
        _Changes.DIRECTOR: EgrulNameEstablisher,
        _Changes.EGRUL_ERRORS: EgrulNameEstablisher
    }

    def __init__(self, bot, user_id):
        super().__init__(bot, user_id)
        self._behaviours.update({
            _EgrulIndirectStates.CHOOSING_CHANGES: self._handle_choice,
            _EgrulIndirectStates.PROCESSING_CHANGES: self._handle_process_changes
        })
        self._chosen_changes = [None] * len(self.NAMES)
        self._cm = ConstantsManager(subcategory="egrul_indirect_establisher")
        self._schema.update({
            "P13001": {
                "стр.1": {},
                "стр.21_ЛистМ_с.1": {},
                "стр.22_ЛистМ_с.2": {},
                "стр.23_ЛистМ_с.3": {}
            }
        })

    def _handle_init(self, update):
        self._choice_keyboard = [[InlineKeyboardButton(self.NAMES[key],
                                                       callback_data=key.value)]
                                 for key in self.NAMES.keys()]
        self._choice_keyboard.append([InlineKeyboardButton("((Закончить))",
                                                           callback_data=-1)])

        update.message.reply_text(self._cm.get_string("init"),
                                  reply_markup=InlineKeyboardMarkup(self._choice_keyboard[:-1]))

        self._state = _EgrulIndirectStates.CHOOSING_CHANGES

    def _handle_choice(self, update):
        try:
            callback_data = int(update.callback_query.data)
        except AttributeError:
            self._bot.send_message(self._user_id, self._cm.get_string("use_buttons"))
            return

        message = update.callback_query.message

        if callback_data >= 0:
            chosen_change = _Changes(callback_data)
            if chosen_change in self._chosen_changes:
                self._chosen_changes[chosen_change.value] = None
            else:
                self._chosen_changes[chosen_change.value] = chosen_change

            if len([c for c in self._chosen_changes if c is not None]) > 0:
                reply_inline_keyboard = InlineKeyboardMarkup(self._choice_keyboard)
                new_message_text = self._cm.get_string("init") + "\n\n -- " + "\n -- ".join(
                    [self.NAMES[c] for c in self._chosen_changes if c is not None])
            else:
                reply_inline_keyboard = InlineKeyboardMarkup(self._choice_keyboard[:-1])
                new_message_text = self._cm.get_string("init")

            update.callback_query.edit_message_text(text=new_message_text,
                                                    reply_markup=reply_inline_keyboard)
        else:
            self._state = _EgrulIndirectStates.PROCESSING_CHANGES
            self._chosen_changes = [c for c in self._chosen_changes if c is not None]
            update.callback_query.edit_message_text(text=message.text,
                                                    reply_markup=None)

            self._current_change_id = 0
            self._current_change = self._chosen_changes[self._current_change_id]
            self._current_sub_establisher = self.ESTABLISHERS[self._current_change](self._bot,
                                                                                    self._user_id,
                                                                                    self._schema)
            return self.handle_update(update)

    def _handle_process_changes(self, update):

        result = self._current_sub_establisher.handle_update(update)

        if result:
            if self._current_change_id < len(self._chosen_changes) - 1:
                self._current_change_id += 1
                self._current_change = self._chosen_changes[self._current_change_id]
                self._current_sub_establisher = self.ESTABLISHERS[self._current_change](self._bot,
                                                                                        self._user_id,
                                                                                        self._schema)
                return self.handle_update(update)
            else:
                self._state = States.END
                return self.handle_update(update)
        else:
            return
