import json
from enum import Enum, auto

from telegram import (ReplyKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

from loggingserver import LoggingServer

from src.ConstantsManager import ConstantsManager
from src.excel.ExcelEngine import ExcelEngine

import logging

from src.managers.egrul.EgrulManager import EgrulManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


class LuthorStates(Enum):  # User needs to make a submission (send a pack of documents to a certain authority)
    # first we provide a list of possible submissions (on start)
    CHOOSING_SUBMISSION = auto()
    BUILDING_SUBMISSION = auto()


class Luthor:

    INSTANCE = None

    def __init__(self, xl_engine, updater):
        self._xl_engine = xl_engine
        self._updater = updater
        self._logger = LoggingServer.getInstance("luthor")
        self._cm = ConstantsManager(subcategory="luthor")

        self._available_submission_classes = {"Изменения в ЕГРЮЛ": EgrulManager,
                                              "Заявление на Шенген": EgrulManager}
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
                    RegexHandler(self._submissions_regexp, self.on_choosing_submission)],
                LuthorStates.BUILDING_SUBMISSION: [
                    MessageHandler(Filters.text, self.on_building_submission_message),
                    CallbackQueryHandler(self.on_building_submission_callback)],
            },

            fallbacks=[CommandHandler('cancel', self.on_cancel)]
        )

        self._updater.dispatcher.add_handler(conv_handler)

        self._updater.dispatcher.add_error_handler(self.on_error)

    def launch(self):
        self._updater.start_polling()

    def on_start(self, bot, update):

        reply_keyboard = [[key for key in self._available_submission_classes.keys()]]

        update.message.reply_text(self._cm.get_string("hi"),
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))
        self._submission_managers[
            update.message.from_user.id] = Luthor.USER_FORM_MANAGERS_STUB.copy()

        return LuthorStates.CHOOSING_SUBMISSION

    def on_choosing_submission(self, bot, update):  #

        submission_id = update.message.text
        user_id = update.message.from_user.id
        if self._submission_managers[user_id][submission_id] is None:
            manager = self._available_submission_classes[submission_id](self._updater.bot,
                                                                        user_id,
                                                                        self._xl_engine)
            self._submission_managers[user_id][submission_id] = manager
        else:
            manager = self._submission_managers[user_id][submission_id]
        self._active_managers[user_id] = manager

        manager.handle_update(update)

        return LuthorStates.BUILDING_SUBMISSION


    def on_building_submission_message(self, bot, update):
        user_id = update.message.from_user.id
        return self._on_building_submission(user_id, update)

    def on_building_submission_callback(self, bot, update):
        user_id = update._effective_user.id
        return self._on_building_submission(user_id, update)

    def _on_building_submission(self, user_id, update):
        manager = self._active_managers[user_id]
        result = manager.handle_update(update)
        if result is None:
            return LuthorStates.BUILDING_SUBMISSION
        elif isinstance(result, str):
            self._bot.send_message(user_id, result)
            return ConversationHandler.END
        else:
            self._updater.bot.send_message(user_id, "Ваши документы:")
            self._updater.bot.send_document(user_id, result,
                                            filename=manager.get_form_id() + ".xls")
            return ConversationHandler.END

    def on_cancel(self, bot, update):
        update.message.reply_text("Cancelled")
        return ConversationHandler.END

    def on_error(self, bot, update, error):
        print(type(error), error)


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
