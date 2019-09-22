import json
from enum import Enum, auto

from telegram import (ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

from loggingserver import LoggingServer

from src.ConstantsManager import ConstantsManager
from src.excel.ExcelEngine import ExcelEngine

import logging

from src.managers.ergul.ErgulManager import ErgulManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


class LuthorStates(Enum):  # User needs to make a submission (send a pack of documents to a certain authority)
    # first we provide a list of possible submissions (on start)
    CHOOSING_SUBMISSION = auto()
    BUILDING_SUBMISSION = auto()


class Luthor:

    def __init__(self, xl_engine, updater):
        self._xl_engine = xl_engine
        self._updater = updater
        self._logger = LoggingServer.getInstance("luthor")
        self._cm = ConstantsManager(subcategory="luthor")

        self._available_submission_classes = {"Изменения в ЕРГЮЛ": ErgulManager,
                                              "Заявление на Шенген": ErgulManager}
        self._submissions_regexp = "^(" + "|".join(self._available_submission_classes.keys()) + ")$"

        self.add_handlers()

        self._submission_managers = {}
        self._active_managers = {}

        Luthor.USER_FORM_MANAGERS_STUB = {form_id: None for form_id in
                                          self._available_submission_classes}

    def add_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.on_start)],

            states={
                LuthorStates.CHOOSING_SUBMISSION: [
                    RegexHandler(self._submissions_regexp, self.on_choosing_sumbission)],
                LuthorStates.BUILDING_SUBMISSION: [
                    MessageHandler(Filters.text, self.on_building_submission),
                    CallbackQueryHandler(self.on_building_submission_callback)],
            },

            fallbacks=[CommandHandler('cancel', self.on_cancel)]
        )

        self._updater.dispatcher.add_handler(conv_handler)

        self._updater.dispatcher.add_error_handler(self.on_error)

    def launch(self):
        self._updater.start_polling()

    def on_start(self, bot, update):  # какая форма?

        reply_keyboard = [[key for key in self._available_submission_classes.keys()]]

        update.message.reply_text(self._cm.get_string("hi"),
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))
        self._submission_managers[
            update.message.from_user.id] = Luthor.USER_FORM_MANAGERS_STUB.copy()

        return LuthorStates.CHOOSING_SUBMISSION

    def on_choosing_sumbission(self, bot, update):  #

        submission_id = update.message.text
        user_id = update.message.from_user.id
        if self._submission_managers[user_id][submission_id] is None:
            manager = self._available_submission_classes[submission_id](user_id, self._xl_engine)
            self._submission_managers[user_id][submission_id] = manager
        else:
            manager = self._submission_managers[user_id][submission_id]
        self._active_managers[user_id] = manager

        manager.handle_update(update)

        return LuthorStates.BUILDING_SUBMISSION


    def on_building_submission(self, bot, update):
        user_id = update.message.from_user.id
        manager = self._active_managers[user_id]
        return_val = manager.handle_update(update)
        if return_val is None:
            return LuthorStates.BUILDING_SUBMISSION
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

    def on_building_submission_callback(self, bot, update):
        user_id = update._effective_user.id
        manager = self._active_managers[user_id]
        manager.handle_update(update)
        return LuthorStates.BUILDING_SUBMISSION

    def on_cancel(self, bot, update):
        update.message.reply_text("Cancelled")
        return ConversationHandler.END

    def on_error(self, bot, update, error):
        print(error)


if __name__ == "__main__":
    with open("resources/auth.json") as f:
        auth_data = json.load(f)
        # token = auth_data["token"]
        token = auth_data["testing_token"]

    updater = Updater(token)
    xl_engine = ExcelEngine()
    bot = Luthor(xl_engine, updater)
    bot.launch()

    # with open("resources/test_data.json") as f:
    #     data = json.load(f)["P13001"]
    # xl_engine.generate("123456", "P13001", data)
