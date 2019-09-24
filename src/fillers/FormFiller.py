import json

from src.StateMachine import StateMachine


class FormFiller(StateMachine):

    def __init__(self, bot, submission_id, user_id):
        self._form_id = submission_id
        self._user_id = user_id
        self._bot = bot

        self._questions = []

        for form_id, form in self._collected_info.items():
            for sheet_id, sheet in form.items():
                for field_id, value in sheet.items():
                    if value is None:
                        self._questions.append(form_id, sheet_id, field_id)

        self._current_question = 0

    def init_collected_info(self, established_schema):
        collected_info = {}
        for form_id in established_schema:

            with open("resources/form_db.json") as f:
                form_schema = json.load(f)[form_id]["schema"]

            collected_info[form_id] = {}
            for sheet_id in established_schema[form_id]:
                collected_info[form_id][sheet_id] = {}
                for field_id in form_schema[sheet_id]:
                    if field_id in established_schema[form_id][sheet_id]:
                        collected_info[form_id][sheet_id][field_id] = \
                            established_schema[form_id][sheet_id][field_id]
                    else:
                        collected_info[form_id][sheet_id][field_id] = None

        self._collected_info = collected_info