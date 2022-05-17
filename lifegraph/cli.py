class Schema():

    def __init__(self, testing=False):

        self.leaf_types = ["string"]

        if testing:
            self.schema = {}
            self.changelog = []
        else:
            self.schema = self.load_schema()
            self.changelog = self.load_changelog()

    def get_accepted_schema_values(self):
        return self.leaf_types + list(self.schema.keys())

    def load_schema():
        return None

    def load_changelog():
        return None

    def create_type(self, id):
        self.schema[id] = {"properties": {}}
        self.changelog.append(("CREATE", "TYPE", id))

    def check_if_type_is_in_schema(self, id):
        return id in self.schema.keys()

    def check_if_property_is_on_type(self, id, property):
        self.raise_if_type_not_in_schema(id)
        return property in self.schema[id]["properties"].keys()

    def raise_if_type_not_in_schema(self, id):
        try:
            assert self.check_if_type_is_in_schema(id)
        except AssertionError:
            raise AssertionError(f"Type {id} not in schema.")

    def raise_if_property_is_on_type(self, id, property):
        try:
            assert not self.check_if_property_is_on_type(id, property)
        except AssertionError:
            raise AssertionError(f"Type {id} has existing property {property}.")

    def raise_if_property_not_on_type(self, id, property):
        try:
            assert self.check_if_property_is_on_type(id, property)
        except AssertionError:
            raise AssertionError(f"Type {id} has no property {property}.")

    def check_if_type_has_parent(self, id):
        return "@parent" in self.schema[id].keys()

    def raise_if_type_has_parent(self, id):
        try:
            assert not self.check_if_type_has_parent(id)
        except AssertionError:
            raise AssertionError(f"Type {id} has existing parent {self.schema[id]['@parent']}.")

    def raise_if_type_has_no_parent(self, id):
        try:
            assert self.check_if_type_has_parent(id)
        except AssertionError:
            raise AssertionError(f"Type {id} has no parent.")

    def add_property(self, id, property, value_id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_property_is_on_type(id, property)
        self.schema[id]["properties"][property] = value_id
        self.changelog.append(("CREATE", "PROPERTY", property, "VALUE", value_id, "ON", id))

    def edit_property(self, id, property, value_id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_property_not_on_type(id, property)
        old_value_id = self.schema[id]["properties"][property]
        self.schema[id]["properties"][property] = value_id
        self.changelog.append(("UPDATE", "PROPERTY", property, "FROM", "VALUE", old_value_id, "TO", "VALUE", value_id, "ON", id))

    def remove_property(self, id, property):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_property_not_on_type(id, property)
        self.schema[id]["properties"].pop(property)
        self.changelog.append(("REMOVE", "PROPERTY", property, "ON", id))

    def make_child(self, id, parent_id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_type_not_in_schema(parent_id)
        self.raise_if_type_has_parent(id)
        self.schema[id]["@parent"] = parent_id
        self.changelog.append(("CREATE", "PARENT", parent_id, "ON", id))

    def edit_parent(self, id, parent_id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_type_not_in_schema(parent_id)
        self.raise_if_type_has_no_parent(id)
        old_parent_id = self.schema[id]["@parent"]
        self.schema[id]["@parent"] = parent_id
        self.changelog.append(("UPDATE", "PARENT", "FROM", "VALUE", old_parent_id, "TO", "VALUE", parent_id, "ON", id))

    def remove_parent(self, id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_type_has_no_parent(id)
        self.schema[id].pop("@parent")
        self.changelog.append(("REMOVE", "PARENT", "ON", id))
