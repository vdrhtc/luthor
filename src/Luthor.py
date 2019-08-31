import json
from enum import Enum, auto

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

from loggingserver import LoggingServer

from src.excel.ExcelEngine import ExcelEngine
from src.managers.P13001Manager import P13001Manager

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


class LuthorStates(Enum):
    QUESTION = auto()
    FORM = auto()
    EDIT = auto()


available_forms = ["P13001", "Документ", "Жопа"]

form_manager_classes = {"P13001": P13001Manager,
                        "Документ": P13001Manager,
                        "Жопа": P13001Manager}


class Luthor:
    USER_FORM_MANAGERS_STUB = {form_id: None for form_id in available_forms}

    def __init__(self, xl_engine, updater):
        self._xl_engine = xl_engine
        self._updater = updater
        self._logger = LoggingServer.getInstance("luthor")

        self._form_managers = {}
        self._active_managers = {}
        self.add_handlers()

    def add_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.on_start)],

            states={
                LuthorStates.QUESTION: [MessageHandler(Filters.text, self.on_question)],
                LuthorStates.FORM: [RegexHandler('^(P13001|Документ|Жопа)$', self.on_form)],
                LuthorStates.EDIT: [MessageHandler(Filters.text, self.on_edit)]
            },

            fallbacks=[CommandHandler('cancel', self.on_cancel)]
        )

        self._updater.dispatcher.add_handler(conv_handler)

        self._updater.dispatcher.add_error_handler(self.on_error)

    def launch(self):
        self._updater.start_polling()

    def on_start(self, bot, update):
        update.message.reply_text("Задай вопрос.")
        return LuthorStates.QUESTION

    def on_question(self, bot, update):
        reply_keyboard = [['P13001', 'Документ', 'Жопа']]

        update.message.reply_text('Не смей играть в игры, в которых ничего не смыслишь.',
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))

        self._form_managers[update.message.from_user.id] = Luthor.USER_FORM_MANAGERS_STUB.copy()

        return LuthorStates.FORM

    def on_form(self, bot, update):
        form_id = update.message.text
        user_id = update.message.from_user.id
        if self._form_managers[user_id][form_id] is None:
            manager = form_manager_classes[form_id](user_id, self._xl_engine)
            self._form_managers[user_id][form_id] = manager
        else:
            manager = self._form_managers[user_id][form_id]
        self._active_managers[user_id] = manager
        update.message.reply_text("Перенаправляю на специалиста.")
        manager.handle_update(update)
        return LuthorStates.EDIT

    def on_edit(self, bot, update):
        user_id = update.message.from_user.id
        manager = self._active_managers[user_id]
        return_val = manager.handle_update(update)
        if return_val is None:
            return LuthorStates.EDIT
        elif return_val is ConversationHandler.END:
            return ConversationHandler.END
        elif isinstance(return_val, str):
            update.message.reply_text(return_val)
            return ConversationHandler.END
        else:
            update.message.reply_text("Ваш документ:")
            self._updater.bot.send_document(update.message.from_user.id, return_val,
                                            filename=manager.get_form_id() + ".xls")
            update.message.reply_text("И еще ты пидор.")
            return ConversationHandler.END

    def on_cancel(self, bot, update):
        update.message.reply_text("Cancelled")
        return ConversationHandler.END

    def on_error(self, bot, update, error):
        print(error)


if __name__ == "__main__":
    with open("resources/auth.json") as f:
        token = json.load(f)["token"]

    updater = Updater(token)
    xl_engine = ExcelEngine()
    bot = Luthor(xl_engine, updater)
    bot.launch()

    # with open("resources/test_data.json") as f:
    #     data = json.load(f)["P13001"]
    # xl_engine.generate("123456", "P13001", data)
