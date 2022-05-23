import json
import logging

class Schema():

    def __init__(self, data_path=None):

        self.data_path = data_path
        self.leaf_types = ["string", "integer", "date"]

        if not self.data_path:
            self.schema = {}
        else:
            self.schema = self.load_schema()
            logging.basicConfig(
                filename=f"{self.data_path}/schema.log",
                encoding='utf-8',
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_accepted_schema_values(self):
        return self.leaf_types + list(self.schema.keys())

    def load_schema(self):
        with open(f"{self.data_path}/schema.json", "r") as f:
            return json.load(f)

    def save_schema(self):
        with open(f"{self.data_path}/schema.json", "w") as f:
            json.dump(self.schema, f, indent=4, sort_keys=True)

    def close(self):
        self.save_schema()

    def create_type(self, id):
        self.raise_if_type_in_schema(id)
        self.schema[id] = {"properties": {}}
        self.logger.info(f"CREATE TYPE {id}")

    def show_type(self, id):
        self.raise_if_type_not_in_schema(id)
        return self.schema[id]

    def check_if_type_is_in_schema(self, id):
        return id in self.get_accepted_schema_values() + list(self.schema.keys())

    def check_if_property_is_on_type(self, id, property):
        self.raise_if_type_not_in_schema(id)
        return property in self.schema[id]["properties"].keys()

    def raise_if_type_not_in_schema(self, id):
        try:
            assert self.check_if_type_is_in_schema(id)
        except AssertionError:
            raise AssertionError(f"Type {id} not in schema.")

    def raise_if_type_in_schema(self, id):
        try:
            assert not self.check_if_type_is_in_schema(id)
        except AssertionError:
            raise AssertionError(f"Type {id} already exists in schema.")

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

    def get_child_ids(self, id):
        """hacky hacky. seems to work."""

        no_parent = [x for x in self.schema.keys() if "@parent" not in self.schema[x].keys()]
        parent = [x for x in self.schema.keys() if "@parent" in self.schema[x].keys()]

        inheritance = []
        for _id in no_parent + parent:
            if "@parent" in self.schema[_id].keys():
                inheritance.append(set([self.schema[_id]["@parent"], _id]))

        children_candidates = set()
        for rel in inheritance:
            if id in rel:
                children_candidates.update(rel)
            if not rel.isdisjoint(children_candidates):
                children_candidates.update(rel)

        children = set()
        for _id in children_candidates:
            if "@parent" in self.schema[_id].keys():
                children.update([_id])
        if id in children:
            children.remove(id)

        return children

    def get_parent_ids(self, id, parents=set()):
        try:
            parents.update([self.schema[id]["@parent"]])
            self.get_parent_ids(self.schema[id]["@parent"], parents=parents)
        except KeyError:
            pass
        return parents

    def get_parent_properties(self, id):
        parents = self.get_parent_ids(id)
        parent_properties = []
        for _id in parents:
            for property in self.schema[_id]["properties"].keys():
                parent_properties.append((_id, property))
        return parent_properties

    def check_if_property_is_from_a_parent(self, id, property):
        parent_properties = self.get_parent_properties(id)
        return property in [x[1] for x in parent_properties]

    def raise_if_property_is_from_a_parent(self, id, property):
        try:
            assert not self.check_if_property_is_from_a_parent(id, property)
        except AssertionError:
            raise AssertionError(f"Property {property} is an inherited property for type {id}.")

    def add_property(self, id, property, value_id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_type_not_in_schema(value_id)
        self.raise_if_property_is_on_type(id, property)
        self.schema[id]["properties"][property] = value_id
        self.logger.info(f"CREATE PROPERTY {property} VALUE {value_id} ON TYPE {id}")
        children = self.get_child_ids(id)
        for child in children:
            self.add_property(child, property, value_id)

    def edit_property(self, id, property, value_id, auto=False):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_type_not_in_schema(value_id)
        self.raise_if_property_not_on_type(id, property)

        if not auto:
            self.raise_if_property_is_from_a_parent(id, property)

        old_value_id = self.schema[id]["properties"][property]
        self.schema[id]["properties"][property] = value_id
        self.logger.info(f"UPDATE PROPERTY {property} FROM VALUE {old_value_id} TO VALUE {value_id} ON TYPE {id}")
        children = self.get_child_ids(id)
        for child in children:
            self.edit_property(child, property, value_id, auto=True)

    def remove_property(self, id, property, auto=False):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_property_not_on_type(id, property)

        if not auto:
            self.raise_if_property_is_from_a_parent(id, property)

        self.schema[id]["properties"].pop(property)
        self.logger.info(f"REMOVE PROPERTY {property} ON TYPE {id}")
        children = self.get_child_ids(id)
        for child in children:
            self.remove_property(child, property, auto=True)

    def make_parent(self, parent_id, id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_type_not_in_schema(parent_id)
        self.raise_if_type_has_parent(id)
        self.schema[id]["@parent"] = parent_id
        self.logger.info(f"CREATE PARENT {parent_id} ON TYPE {id}")

    def edit_parent(self, id, parent_id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_type_not_in_schema(parent_id)
        self.raise_if_type_has_no_parent(id)
        old_parent_id = self.schema[id]["@parent"]
        self.schema[id]["@parent"] = parent_id
        self.logger.info(f"UPDATE PARENT FROM VALUE {old_parent_id} TO VALUE {parent_id} ON TYPE {id}")

    def remove_parent(self, id):
        self.raise_if_type_not_in_schema(id)
        self.raise_if_type_has_no_parent(id)
        self.schema[id].pop("@parent")
        self.logger.info(f"REMOVE PARENT ON TYPE {id}")

    def get_all_string_properties(self):
        string_properties = []
        for type in self.schema.keys():
            for property in self.schema[type]["properties"]:
                string_properties.append((type, property))
        return string_properties
