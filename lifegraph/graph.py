import os
import json
from uuid import uuid4
from schema import Schema

class Graph:
    def __init__(self, data_path=None):
        self.data_path = data_path
        self.schema = Schema(data_path=data_path)

        if data_path is None:
            self.graph = {}
        else:
            self.graph = self.load_graph()

    def load_graph(self):
        graph = {}
        for type in self.schema.schema.keys():
            type_fn = f"{self.data_path}/graph/{type}.json"
            if os.path.exists(type_fn):
                with open(type_fn, "r") as f:
                    graph.update(json.load(f))
        return graph

    def save_graph(self):
        data_types = set([self.graph[x]["@type"] for x in self.graph.keys()])
        for type in data_types:
            type_fn = f"{self.data_path}/graph/{type}.json"
            type_entities = [x for x in self.graph.keys() if self.graph[x]["@type"] == type]
            with open(type_fn, "w") as f:
                json.dump({k: self.graph[k] for k in type_entities}, f,
                    indent=4, sort_keys=True)

    def create_from_type(self, type):
        type_model = self.schema.show_type(type)
        data = {}
        data['@type'] = type
        for k, v in type_model["properties"].items():
            data[k] = v
        self.graph[str(uuid4())] = data

    def audit_entities_have_schema_properties(self, audit_results):
        for k in self.graph.keys():
            entity = self.graph[k]
            expected_type = entity["@type"]
            expected_schema = self.schema.schema[expected_type]
            for property in expected_schema["properties"].keys():
                try:
                    assert property in entity.keys()
                except AssertionError:
                    audit_results.append(f"Entity {k} is missing required property {property}")
                    pass
        return audit_results

    def audit_entity_properties_point_to_correct_type(self, audit_results):
        for k in self.graph.keys():
            entity = self.graph[k]
            data_observed_type = entity["@type"]
            for property in entity.keys():
                if property != "@type":
                    pointed_entity_id = entity[property]
                    if pointed_entity_id not in self.schema.leaf_types:
                        schema_expected_type = self.schema.schema[data_observed_type]["properties"][property]
                        schema_expected_types = list(self.schema.get_child_ids(schema_expected_type)) + [schema_expected_type]
                        data_pointed_type = self.graph[pointed_entity_id]["@type"]
                        try:
                            assert data_pointed_type in schema_expected_types
                        except:
                            audit_results.append(f"Entity {k} property {property} points to entity {pointed_entity_id} of type {data_pointed_type}. Expected type {schema_expected_type}.")
                            pass
        return audit_results

    def get_ids_of_type(self, type):
        return [x for x in self.graph.keys() if self.graph[x]["@type"] == type]

    def audit(self):
        # strict? which would mean no unknown values for certain types?
        audit_results = []
        audit_results = self.audit_entities_have_schema_properties(audit_results)
        audit_results = self.audit_entity_properties_point_to_correct_type(audit_results)
        return audit_results

    # copy data from one id to a new one
    # smartcopy id <- copy everything that is not unique about this record to another record
    # query and generalise from graph
    # migrate data to another type?
    # integrate and test compute transformers against the current schema to ensure that they work


if __name__ == '__main__':
    graph = Graph(data_path="./data")
    graph.create_from_type("person")
    print(graph.graph)
    graph.save_graph()
