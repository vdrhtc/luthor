import io
import json
from editpyxl import Workbook

from src.excel.CellField import CellField
from src.excel.CellFieldParameters import CellFieldParameters


class ExcelEngine:

    def generate(self, user_id, form_id, data):
        with open("resources/form_db.json") as f:
            form_json = json.load(f)[form_id]

        filename = form_json["filename"]
        form_schema = form_json["schema"]

        for sheet_id in form_schema.keys():
            for field_id in form_schema[sheet_id]:
                field_origin = form_schema[sheet_id][field_id][0]
                field_parameters = form_schema[sheet_id][field_id][1]
                cfp = CellFieldParameters(*field_parameters)
                form_schema[sheet_id][field_id] = CellField(field_origin, cfp)

        form_xl = self._load(filename)
        mapping = self._generate_mappings(form_schema, data)
        filled_form_xl = self._fill(form_xl, mapping)
        dest_filename = self._generate_file(user_id, filled_form_xl, filename)

        with open(dest_filename, "rb") as f:
            binary_stream = io.BytesIO(f.read())
        return binary_stream

    def _load(self, filename):
        return Workbook().open("forms/" + filename)

    def _fill(self, form_xl, mapping):
        for sheet_id in form_xl.get_sheet_names():
            if sheet_id in mapping:
                sheet_xl = form_xl[sheet_id]
                for key in mapping[sheet_id]:
                    sheet_xl.cell(key).value = mapping[sheet_id][key]
            else:
                form_xl.hide_sheet(sheet_id)
        return form_xl

    def _generate_file(self, user_id, form_xl, filename):
        fn_without_ext = "".join(filename.split(".")[:-1])
        dest_filename = "xl_build/" + fn_without_ext + str(user_id) + ".xlsx"
        form_xl.save(dest_filename)
        return dest_filename

    def _generate_mappings(self, form_schema, data):

        total_mapping = {}

        sheet_ids = form_schema.keys()
        for sheet_id in sheet_ids:
            if sheet_id in data.keys():
                sheet_data = data[sheet_id]
                sheet_mapping = {}

                for field_name in sheet_data.keys():
                    cell_field = form_schema[sheet_id][field_name]
                    field_value = sheet_data[field_name]
                    try:
                        mapping = cell_field.fill_mapping(field_value)
                    except ValueError as e:
                        raise ValueError(
                            "Failed to fill field %s on %s: %s" % (field_name, sheet_id, str(e)))
                    sheet_mapping.update(mapping)

            total_mapping[sheet_id] = sheet_mapping

        return total_mapping
