import os
import json
from uuid import uuid4
from schema import Schema
from fuzzywuzzy import process
import pandas as pd
import logging
import functools as ft

class Graph:
    def __init__(self, data_path=None):
        self.data_path = data_path
        self.schema = Schema(data_path=self.data_path)

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

    def flat(self, x):
        return [item for sublist in x for item in sublist]

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

    def search_out_from_id_property(self, id, property):
        original_id, original_property = id, property
        ids_to_explore = [(0, id, [property])]
        paths_out = []
        while len(ids_to_explore) > 0:
            (depth, id, properties) = ids_to_explore[0]
            id_type = self.graph[id]["@type"]
            for property in properties:
                schema_expected_type = self.schema.schema[id_type]["properties"][property]
                if schema_expected_type not in self.schema.leaf_types:
                    pointed_id = self.graph[id][property]
                    pointed_id_type = self.graph[pointed_id]["@type"]
                    pointed_id_properties = [x for x in self.schema.schema[pointed_id_type]["properties"].keys() if x != "@tyoe"]
                    ids_to_explore.append((depth+1, pointed_id, pointed_id_properties))
                    paths_out.append({
                        "original_id": original_id,
                        "original_property": original_property,
                        "depth": depth,
                        "pointing_property": property,
                        "pointed_id": pointed_id,
                        "pointed_id_type": pointed_id_type})

            del ids_to_explore[0]
        return paths_out

    def categorical_aggregation_groups(self, ids):
        self.raise_if_ids_not_the_same_type(ids)
        [self.raise_if_id_not_in_graph(x) for x in ids]

        expected_properties = self.schema.schema[self.graph[ids[0]]["@type"]]["properties"].keys()
        search_starts = []
        for id in ids:
            for property in expected_properties:
                search_starts.append((id, property))

        aggregation_paths = []
        for id, property in search_starts:
            agg_paths_out = self.search_out_from_id_property(id, property)
            if agg_paths_out:
                aggregation_paths.append(agg_paths_out)

        return pd.DataFrame(self.flat(aggregation_paths))

    def categorical_aggregation_paths(self, ids):
        aggregation_groups = self.categorical_aggregation_groups(ids)
        aggregation_paths = aggregation_groups.groupby(
            ["depth", "pointing_property", "pointed_id_type"], as_index=False
        ).agg({"pointed_id": [pd.Series.nunique, "count"]})
        aggregation_paths.columns = ["depth", "pointing_property", "aggregation_type", "n_groups", "aggregation_proportion"]
        aggregation_paths["aggregation_proportion"] = aggregation_paths["aggregation_proportion"] / len(ids)
        return aggregation_paths

    def categorical_aggregation(self,
        ids,
        value_property,
        aggregation_fun,
        aggregations):

        aggregation_groups = self.categorical_aggregation_groups(ids)
        aggregation_lookups = []
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            for i, aggregation in enumerate(aggregations):
                aggregation_lookup = aggregation_groups[
                    (aggregation_groups["depth"] == aggregation["depth"]) &
                    (aggregation_groups["pointing_property"] == aggregation["pointing_property"]) &
                    (aggregation_groups["pointed_id_type"] == aggregation["aggregation_type"])]
                aggregation_lookup = aggregation_lookup[["original_id", "pointed_id"]]
                aggregation_lookup.columns = ["original_id", f"aggregation_{i}"]
                aggregation_lookups.append(aggregation_lookup)

        aggregation_join_table = ft.reduce(
            lambda left, right: pd.merge(left, right, how="left", on="original_id"),
            aggregation_lookups)
        group_columns = list(aggregation_join_table.drop("original_id", axis=1).columns)

        aggregated = []

        for name, group in aggregation_join_table.groupby(group_columns):
            vals = [self.graph[x][value_property] for x in group["original_id"]]
            aggregated.append({
                "value": aggregation_fun(vals),
                "group": name
            })
        return aggregated

    def get_expected_pointed_type(self, id, property):
        self.raise_if_id_not_in_graph(id)
        entity_type = self.graph[id]["@type"]
        return self.schema.schema[entity_type]["properties"][property]

    def raise_if_id_not_expected_type(self, id, expected_type):
        observed_type = self.graph[id]["@type"]
        try:
            assert observed_type == expected_type
        except AssertionError:
            raise AssertionError(f"Entity '{id}' has type '{observed_type}'. Expected type '{expected_type}'.")

    def edit_property(self, id, property, value):
        self.raise_if_id_not_in_graph(id)
        # TODO: Also check that the schema has this property!
        expected_type = self.get_expected_pointed_type(id, property)
        if expected_type not in self.schema.leaf_types:
            self.raise_if_id_not_expected_type(value, expected_type)
        self.graph[id][property] = value

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

    # schema changes should result in changes to the graph - do this when this concept is working
