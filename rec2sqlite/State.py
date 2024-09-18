class State:
    def __init__(self):
        self.table_fields = []
        self.data_types = {}
        self.autoinc_values = {}
        self.cinvs = [] 

    def reset(self, new_state):
        self.state = new_state
        self.record = {}
        self.cur_field = ""

    def add_field(self, field):
        self.table_fields.append(field)
        self.data_types[field.name] = field.data_type
