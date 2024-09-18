from .Cinv import Cinv
from .Constants import Constants
from .Field import Field
from .State import State
from .WhatAreWeReading import WhatAreWeReading

import os

class Transformer:
    def __init__(self):
        self.state = State()
        self.state.reset(WhatAreWeReading.UNKNOWN)
        self.sql = []

    def get_sql(self):
        return Constants.LINE_SEPARATOR.join(self.sql)

    def process_table_marker(self, cur_line):
        self.state.state = WhatAreWeReading.DDL
        self.state.table_name = cur_line[len(Constants.TABLE_MARKER):].strip()
        self.state.data_types = {}
        self.state.table_fields = []
        self.state.autoinc_values = {}
        self.state.cinvs = []
        self.record = {}

    def parse_cinv(self, field_def_txt):
        parts = field_def_txt.split(' ')
        cinv = Cinv()
        cinv.list_field = parts[0].strip()
        cinv_def = field_def_txt[len(cinv.list_field):].strip()
        cinv_parts = cinv_def.split('|')
        cinv.sql = cinv_parts[1]
        cinv.field = cinv_parts[2]
        return cinv

    def process_type_marker(self, cur_line):
        self.state.state = WhatAreWeReading.DDL
        field_def_txt = cur_line[len(Constants.TYPE_MARKER):].strip()
        field_def_parts = field_def_txt.split(' ')
        field_name = field_def_parts[0].strip()
        field_type = field_def_parts[1].strip()
        if field_type == "AUTOINC":
            self.state.autoinc_values[field_name] = 1
        if field_type.startswith("CINV"):
            self.state.cinvs.append(self.parse_cinv(field_def_txt))
        self.state.add_field(Field(field_name, field_type))

    def process_field_value_record(self, cur_line):
        colon_idx = cur_line.find(":")
        field_name = cur_line[0:colon_idx].strip()
        field_value = self.escape_single_quotes(cur_line[colon_idx+1:].strip())

        if (field_name in self.state.data_types):
            self.state.cur_field = field_name
            self.state.record[field_name] = field_value
            self.state.state = WhatAreWeReading.DML
        else:
            self.save("-- Undeclared field '" + field_name + "'" + Constants.LINE_SEPARATOR)

    def escape_single_quotes(self, txt):
        return txt.replace("'", "''")

    def process_multiline_value_fragment(self, cur_line):
        # Second line of a multiline value
        value_fragment = self.escape_single_quotes(cur_line[2:])
        old_value = self.state.record[self.state.cur_field]
        new_value = old_value + Constants.LINE_SEPARATOR + value_fragment
        self.state.record[self.state.cur_field] = new_value 

    def process_ddl(self, cur_line):
        sql = self.compose_create_table_sql(self.state.table_name, self.state.table_fields)
        self.save(sql)
        self.state.reset(WhatAreWeReading.SEPARATOR)

    def compose_cinv_insert_sql(self, state):
        pts = []
        for cinv in state.cinvs:
            sql_template = cinv.sql
            field_name = cinv.field
            field_value = state.record[field_name]
            if cinv.list_field not in state.record:
                self.save("-- CINV error: Field '" + cinv.list_field + "' is not present in record '" + str(state.record) + "'")
                continue
            list_field_value = state.record[cinv.list_field]
            list_elems = list_field_value.split(',')
            for cur_list_elem in list_elems:
                cur_sql = sql_template.format(field_value, cur_list_elem.strip())
                pts.append(cur_sql)
                pts.append(Constants.LINE_SEPARATOR)
        return "".join(pts)

    def process_dml(self, cur_line):
        if not self.state.record:
            self.save("-- Ignoring empty record in " + self.state.table_name + " table")
            return
        sql = self.compose_insert_sql(self.state.table_name, self.state.record, self.state.data_types)
        self.save(sql)
        if self.state.cinvs:
            sql = self.compose_cinv_insert_sql(self.state)
            self.save(sql)
        self.state.reset(WhatAreWeReading.DML)
        
    def process_line(self, cur_line):
        if cur_line.startswith('#'):
            return
        if cur_line.startswith(Constants.TABLE_MARKER):
            self.process_table_marker(cur_line)
            return
        if cur_line.startswith(Constants.TYPE_MARKER):
            self.process_type_marker(cur_line)
            return
        empty_line = not cur_line.strip()
        if cur_line.find(":") and (not cur_line.startswith(Constants.MULTILINE_MARKER)) and (not empty_line):
            self.process_field_value_record(cur_line)
            return
        if cur_line.find(":") and cur_line.startswith(Constants.MULTILINE_MARKER) and (not empty_line):
            self.process_multiline_value_fragment(cur_line)
            return
        if empty_line and (self.state.state == WhatAreWeReading.DDL):
            self.process_ddl(cur_line)
            return
        if empty_line and (self.state.state == WhatAreWeReading.DML):
            self.process_dml(cur_line)

    def save(self, sql):
        self.sql.append(sql)

    def compose_create_table_sql(self, table_name, table_fields):
        pts = []
        pts.append("CREATE TABLE ")
        pts.append(table_name)
        pts.append("(")
        first_field = True
        for cur_field in table_fields:
            if self.is_cinv(cur_field.data_type):
                continue
            if first_field:
                first_field = False
            else:
                pts.append(", ")
            pts.append(cur_field.name)
            pts.append(" ")
            pts.append(self.convert_data_type(cur_field.data_type))
        pts.append(");")
        return "".join(pts)
    
    def is_cinv(self, in_type):
        return in_type.startswith("CINV")

    def convert_data_type(self, in_type):
        if in_type == "AUTOINC":
            return "INTEGER"
        else:
            return in_type
    def add_autoinc_values(self, record):
        if not self.state.autoinc_values:
            return
        for cur_kv in self.state.autoinc_values.items():
            field_name = cur_kv[0]
            old_value = cur_kv[1]
            record[field_name] = old_value
            new_value = old_value + 1
            self.state.autoinc_values[field_name] = new_value

    def compose_insert_sql(self, table_name, record, data_types):
        pts = []
        self.add_autoinc_values(record)
        field_names = record.keys()
        pts.append("INSERT INTO ")
        pts.append(table_name)
        pts.append("(")
        first_field_name = True
        for cur_field in field_names:
            if self.is_cinv(data_types[cur_field]):
                continue
            if first_field_name:
                first_field_name = False
            else:
                pts.append(", ")
            pts.append(cur_field)
        pts.append(") VALUES(")
        first_field_name = True
        for cur_field in field_names:
            if self.is_cinv(data_types[cur_field]):
                continue
            if first_field_name:
                first_field_name = False
            else:
                pts.append(", ")
            cur_data_type = data_types[cur_field]
            cur_value = record[cur_field]
            if cur_data_type == "TEXT":
                cur_value = "'{cur_value}'".format(cur_value=cur_value)
            elif cur_data_type == "AUTOINC":
                cur_value = str(cur_value)
            pts.append(cur_value)
        pts.append(");")
        return "".join(pts)
