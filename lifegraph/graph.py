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
        uuid = str(uuid4())
        self.graph[uuid] = data
        return uuid

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

    def raise_if_id_not_in_graph(self, id):
        try:
            assert id in self.graph.keys()
        except AssertionError:
            raise AssertionError(f"Entity {id} not in graph.")

    def audit(self):
        audit_results = []
        audit_results = self.audit_entities_have_schema_properties(audit_results)
        audit_results = self.audit_entity_properties_point_to_correct_type(audit_results)
        return audit_results

    def create_from_copy(self, id):
        self.raise_if_id_not_in_graph(id)
        uuid = str(uuid4())
        self.graph[uuid] = self.graph[id]
        return uuid

    def create_from_smart_copy(self, id):
        self.raise_if_id_not_in_graph(id)
        print(id)
        #uuid = str(uuid4())
        #self.graph[uuid] = self.graph[id]
        #return uuid

    # smartcopy id <- copy everything that is not unique about this record to another record
    # disaggregate a parent type into a child type (i.e. states into cities - hierarchy also doesn't work this way!)
    # aggregate child types into parent type groups (i.e. cities into parent states? - hierarchy doesn't work this way?)
    #    maybe you need types to describe different relationships (like spatial containment?)
    # swap - switch group chartacteristics at same level (i.e. gender male vs. gender female)
    # query and generalise from graph
    # migrate data to another type?
    # integrate and test compute transformers against the current schema to ensure that they work


if __name__ == '__main__':
    graph = Graph(data_path="./data")
    person_id = graph.create_from_type("person")
    graph.create_from_copy(person_id)
    print(graph.graph)

    graph.save_graph()
