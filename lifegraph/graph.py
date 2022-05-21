import os
import json
from uuid import uuid4
from schema import Schema
from fuzzywuzzy import process
import pandas as pd

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
            data[k] = "UNKNOWN"
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
                    schema_expected_type = self.schema.schema[data_observed_type]["properties"][property]
                    if schema_expected_type not in self.schema.leaf_types:
                        schema_expected_types = list(self.schema.get_child_ids(schema_expected_type)) + [schema_expected_type]
                        try:
                            data_pointed_type = self.graph[pointed_entity_id]["@type"]
                        except KeyError:
                            audit_results.append(f"Entity '{k}' property '{property}' points to unknown entity '{pointed_entity_id}'. Expected type '{schema_expected_type}'.")
                            continue

                        try:
                            assert data_pointed_type in schema_expected_types
                        except AssertionError:
                            audit_results.append(f"Entity '{k}' property '{property}' points to entity '{pointed_entity_id}' of type '{data_pointed_type}'. Expected type '{schema_expected_type}'.")
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
        self.graph[uuid] = self.graph[id].copy()
        return uuid

    def create_from_smart_copy(self, id):
        # This should be abstracted and clarified - same for a few other methods
        self.raise_if_id_not_in_graph(id)
        group_type = self.graph[id]["@type"]
        group_properties = self.schema.schema[group_type]["properties"].keys()
        other_group_member_ids = [x for x in self.get_ids_of_type(group_type) if x != id]
        unique_properties = []
        for property in group_properties:
            other_group_values = set([self.graph[x][property] for x in other_group_member_ids])
            if self.graph[id][property] not in other_group_values:
                unique_properties.append(property)
        data = {}
        data['@type'] = group_type
        for property in group_properties:
            if property in unique_properties:
                data[property] = "UNKNOWN"
            else:
                data[property] = self.graph[id][property]
        uuid = str(uuid4())
        self.graph[uuid] = data
        return uuid

    def search(self, value, type=None):
        # DEV: In the future this could also have a constraint for property name
        if type:
            search_ids = self.get_ids_of_type(type)
        else:
            search_ids = self.graph.keys()
        search_properties = self.schema.get_all_string_properties()
        search_candidates = []
        for id in search_ids:
            for type, property in search_properties:
                if self.graph[id]["@type"] == type:
                    search_candidates.append((id, self.graph[id][property]))
        match = process.extract(value, [x[1] for x in search_candidates], limit=1)
        return [x[0] for x in search_candidates if x[1] == match[0][0]]

    def raise_if_ids_not_the_same_type(self, ids):
        type = self.graph[ids[0]]["@type"]
        id_types = set([self.graph[x]["@type"] for x in ids])
        try:
            assert set([type]) == id_types
        except AssertionError:
            raise AssertionError(f"IDs point to more than one type: {', '.join(list(id_types))}.")

    def categorical_aggregation_paths(self, ids):
        self.raise_if_ids_not_the_same_type(ids)
        # paths that could be used to aggregate a collection of ids into categorical groups

        print(json.dumps(self.graph, indent=4))

        # in the future this will have to tolerate multiple pointed entities (i.e. multiple defense alliances)
        ids_depth = [(0, x) for x in ids]
        ids_to_explore = ids_depth
        depth_groups = []
        while len(ids_to_explore) > 0:
            id = ids_to_explore[0]
            id_type = self.graph[id[1]]["@type"]
            schema_expected_properties = self.schema.schema[id_type]["properties"]
            for property in self.graph[id[1]].keys():
                if property != "@type":
                    if schema_expected_properties[property] not in self.schema.leaf_types and id_type != schema_expected_properties[property]:
                        pointed_entity_id = self.graph[id[1]][property]
                        ids_to_explore.append((id[0]+1, pointed_entity_id))
                        depth_groups.append((id[0], self.graph[pointed_entity_id]["@type"], pointed_entity_id))

            del ids_to_explore[0]
        depth_groups = pd.DataFrame(depth_groups, columns=["depth", "type", "pointed_id"])
        depth_groups_summarised = depth_groups.groupby(
            ["depth", "type"], as_index=False
        ).agg({"pointed_id": [pd.Series.nunique, "count"]})
        depth_groups_summarised.columns = ["depth", "aggregation_type", "n_groups", "aggregation_proportion"]
        depth_groups_summarised["aggregation_proportion"] = depth_groups_summarised["aggregation_proportion"] / len(ids)
        return depth_groups_summarised

    # actually implement aggregation for given categorical aggregation(s)


    # change property on graph should be implemented to check that a property exists on an entity and
    # make sure new thing points to the correct type, validate input data

    # then actually try to the the graph for something simple, then something messy & record the pain points (changing / migrating schema etc)
    # feeling like i don't exactly know what I am doing - do the simple things, then try to use it
    # what is the application of the aggregation?

    # swap - switch group chartacteristics at same level (i.e. gender male vs. gender female)
    # query and generalise from graph
    # migrate data to another type?
    # integrate and test compute transformers against the current schema to ensure that they work
    # maybe there is a way to make this quicker without all of these fucking for loops in the future - no time now!!
    # try aggreation with some really partial information

    # fuck fuck - this isn't working - because type enforcement isn't conducive to having a country
    # be a member of a continent and a defense alliance (they are not even usefully the same type)
    # is a continent an organisation? no. is a defense alliance a land area? no.
    # fuck fuck.
    # but of course in the fucking real world - the UK is easily in both Europe and NATO. fucking fuck.
    # go get some paper from the printer and work this out


if __name__ == '__main__':
    graph = Graph(data_path="./data")
    person_id = graph.create_from_type("person")
    graph.create_from_copy(person_id)
    print(graph.graph)

    graph.save_graph()
