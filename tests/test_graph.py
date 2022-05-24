import pytest
import json
from graph import Graph
import pandas as pd
import statistics

@pytest.fixture()
def mock_graph_with_person_schema():
    graph = Graph(data_path=None)
    graph.schema.create_type("person")
    graph.schema.add_property("person", "name", "string")
    return graph

@pytest.fixture()
def mock_graph_with_person_hometown_schema():
    graph = Graph(data_path=None)
    graph.schema.create_type("person")
    graph.schema.create_type("city")
    graph.schema.add_property("person", "name", "string")
    graph.schema.add_property("person", "hometown", "city")
    graph.schema.add_property("city", "name", "string")
    return graph

@pytest.fixture()
def mock_graph_with_person_with_country_continent():
    graph = Graph(data_path=None)
    graph.schema.create_type("continent")
    graph.schema.create_type("country")
    graph.schema.create_type("person")
    graph.schema.add_property("person", "name", "string")
    graph.schema.add_property("person", "age", "integer")
    graph.schema.add_property("person", "location", "country")
    graph.schema.add_property("country", "continent", "continent")
    return graph

def test_create_from_type(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.create_from_type("person")
    assert len(graph.graph.keys()) == 1
    id = list(graph.graph.keys())[0]
    assert graph.graph[id] == {"@type": "person", "name": "UNKNOWN"}

def test_audit_entities_have_schema_properties_passes(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.create_from_type("person")
    audit_results = []
    audit_results = graph.audit_entities_have_schema_properties(audit_results)
    assert len(audit_results) == 0

def test_audit_entities_have_schema_properties_fails(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.create_from_type("person")
    graph.graph[list(graph.graph.keys())[0]].pop("name")
    audit_results = []
    audit_results = graph.audit_entities_have_schema_properties(audit_results)
    assert len(audit_results) == 1
    assert 'is missing required property name' in audit_results[0]

def test_get_ids_of_type_exists(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.create_from_type("person")
    res = graph.get_ids_of_type("person")
    assert len(res) == 1

def test_get_ids_of_type_missing(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    res = graph.get_ids_of_type("person")
    assert len(res) == 0

def test_audit_entity_properties_point_to_correct_type_passes_with_leaf_type(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.create_from_type("person")
    audit_results = []
    audit_results = graph.audit_entity_properties_point_to_correct_type(audit_results)
    assert len(audit_results) == 0

def test_audit_entity_properties_point_to_correct_type_passes_with_pointed_type(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.schema.create_type("city")
    graph.schema.add_property("person", "hometown", "city")
    graph.create_from_type("person")
    graph.create_from_type("city")
    person_ids = graph.get_ids_of_type("person")
    city_ids = graph.get_ids_of_type("city")
    graph.graph[person_ids[0]]["hometown"] = city_ids[0]
    audit_results = []
    audit_results = graph.audit_entity_properties_point_to_correct_type(audit_results)
    assert len(audit_results) == 0

def test_audit_entity_properties_point_to_correct_type_passes_with_pointed_type_to_child(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.schema.create_type("city")
    graph.schema.create_type("little_city")
    graph.schema.make_parent("city", "little_city")
    graph.schema.add_property("person", "hometown", "city")
    graph.create_from_type("person")
    graph.create_from_type("little_city")
    person_ids = graph.get_ids_of_type("person")
    little_city_ids = graph.get_ids_of_type("little_city")
    graph.graph[person_ids[0]]["hometown"] = little_city_ids[0]
    audit_results = []
    audit_results = graph.audit_entity_properties_point_to_correct_type(audit_results)
    assert len(audit_results) == 0

def test_audit_entity_properties_point_to_correct_type_fails_with_pointed_type(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.schema.create_type("city")
    graph.schema.add_property("person", "hometown", "city")
    graph.create_from_type("person")
    graph.create_from_type("city")
    graph.schema.add_property("city", "name", "string")
    person_ids = graph.get_ids_of_type("person")
    city_ids = graph.get_ids_of_type("person")
    graph.graph[person_ids[0]]["hometown"] = city_ids[0]
    audit_results = []
    audit_results = graph.audit_entity_properties_point_to_correct_type(audit_results)
    assert len(audit_results) == 1
    assert "type 'person'. Expected type 'city'." in audit_results[0]

def test_raise_if_id_not_in_graph(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    with pytest.raises(AssertionError) as exc_info:
        graph.raise_if_id_not_in_graph("id")
    assert exc_info.value.args[0] == "Entity id not in graph."

def test_create_from_copy(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    person_id = graph.create_from_type("person")
    copy_id = graph.create_from_copy(person_id)
    assert len(graph.graph.keys()) == 2
    assert graph.graph[person_id] == graph.graph[copy_id]

def test_create_from_smart_copy(mock_graph_with_person_hometown_schema):
    graph = mock_graph_with_person_hometown_schema
    person_id1 = graph.create_from_type("person")
    person_id2 = graph.create_from_type("person")
    city_id1 = graph.create_from_type("city")
    graph.graph[person_id1]["name"] = "Hamish"
    graph.graph[person_id2]["name"] = "Peter"
    graph.graph[city_id1]["name"] = "Syracuse"
    graph.graph[person_id1]["hometown"] = city_id1
    graph.graph[person_id2]["hometown"] = city_id1
    smart_copy_id = graph.create_from_smart_copy(person_id1)
    assert graph.graph[smart_copy_id]["name"] == "UNKNOWN"
    assert graph.graph[smart_copy_id]["hometown"] == city_id1

def test_search_only_value_one_match(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    person_id1 = graph.create_from_type("person")
    person_id2 = graph.create_from_type("person")
    graph.graph[person_id1]["name"] = "Hamish"
    graph.graph[person_id2]["name"] = "Peter"
    res = graph.search("Hamish")
    assert len(res) == 1
    assert res[0] == person_id1

def test_search_only_value_two_matches(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    person_id1 = graph.create_from_type("person")
    person_id2 = graph.create_from_type("person")
    graph.graph[person_id1]["name"] = "Hamish"
    graph.graph[person_id2]["name"] = "Hamish"
    res = graph.search("Hamish")
    assert len(res) == 2
    assert res[0] == person_id1
    assert res[1] == person_id2


def test_search_with_type_constraint_one_match(mock_graph_with_person_hometown_schema):
    graph = mock_graph_with_person_hometown_schema
    person_id1 = graph.create_from_type("person")
    city_id1 = graph.create_from_type("city")
    graph.graph[person_id1]["name"] = "Hamish"
    graph.graph[city_id1]["name"] = "Hamish"
    res = graph.search("Hamish", type="city")
    assert len(res) == 1
    assert res[0] == city_id1

def test_search_with_value_and_type_constraint_one_match(mock_graph_with_person_hometown_schema):
    graph = mock_graph_with_person_hometown_schema
    person_id1 = graph.create_from_type("person")
    city_id1 = graph.create_from_type("city")
    graph.graph[person_id1]["name"] = "Hamish"
    graph.graph[city_id1]["name"] = "Hamish"
    res = graph.search("Hamish", type="city")
    assert len(res) == 1
    assert res[0] == city_id1

def test_raise_if_ids_not_the_same_type_raises(mock_graph_with_person_hometown_schema):
    graph = mock_graph_with_person_hometown_schema
    person_id1 = graph.create_from_type("person")
    city_id1 = graph.create_from_type("city")
    with pytest.raises(AssertionError) as exc_info:
        graph.raise_if_ids_not_the_same_type([person_id1, city_id1])
    assert "IDs point to more than one type: " in exc_info.value.args[0]

def test_search_out_from_id_property(mock_graph_with_person_with_country_continent):
    graph = mock_graph_with_person_with_country_continent
    continent1 = graph.create_from_type("continent")
    country1 = graph.create_from_type("country")
    country2 = graph.create_from_type("country")
    person1 = graph.create_from_type("person")
    person2 = graph.create_from_type("person")
    graph.edit_property(person1, "location", country1)
    graph.edit_property(person2, "location", country2)
    graph.edit_property(country1, "continent", continent1)
    graph.edit_property(country2, "continent", continent1)

    res = graph.search_out_from_id_property(person1, "location")
    assert {
        "original_id": person1,
        "original_property": "location",
        "depth": 0,
        "pointing_property": "location",
        "pointed_id": country1,
        "pointed_id_type": "country"
    } in res
    assert {
        "original_id": person1,
        "original_property": "location",
        "depth": 1,
        "pointing_property": "continent",
        "pointed_id": continent1,
        "pointed_id_type": "continent"
    } in res

def test_categorical_aggregation_groups(mock_graph_with_person_with_country_continent):
    graph = mock_graph_with_person_with_country_continent
    continent1 = graph.create_from_type("continent")
    country1 = graph.create_from_type("country")
    country2 = graph.create_from_type("country")
    person1 = graph.create_from_type("person")
    person2 = graph.create_from_type("person")
    graph.edit_property(person1, "location", country1)
    graph.edit_property(person2, "location", country2)
    graph.edit_property(country1, "continent", continent1)
    graph.edit_property(country2, "continent", continent1)

    res = graph.categorical_aggregation_groups([person1, person2])
    assert res.shape[0] == 4
    assert res.iloc[0, :]['original_id'] == person1
    assert res.iloc[0, :]['pointed_id'] == country1
    assert res.iloc[1, :]['original_id'] == person1
    assert res.iloc[1, :]['pointed_id'] == continent1

def test_categorical_aggregation_paths(mock_graph_with_person_with_country_continent):
    # also used in 2 tests above - move to fixture?
    graph = mock_graph_with_person_with_country_continent
    continent1 = graph.create_from_type("continent")
    country1 = graph.create_from_type("country")
    country2 = graph.create_from_type("country")
    person1 = graph.create_from_type("person")
    person2 = graph.create_from_type("person")
    graph.edit_property(person1, "location", country1)
    graph.edit_property(person2, "location", country2)
    graph.edit_property(country1, "continent", continent1)
    graph.edit_property(country2, "continent", continent1)
    res = graph.categorical_aggregation_paths([person1, person2])
    assert res.shape[0] == 2
    assert res.shape[1] == 5
    assert res.iloc[0, :]["aggregation_type"] == "country"
    assert res.iloc[1, :]["aggregation_type"] == "continent"

def test_categorical_aggregation(mock_graph_with_person_with_country_continent):
    graph = mock_graph_with_person_with_country_continent
    continent1 = graph.create_from_type("continent")
    country1 = graph.create_from_type("country")
    country2 = graph.create_from_type("country")
    person1 = graph.create_from_type("person")
    person2 = graph.create_from_type("person")
    graph.edit_property(person1, "location", country1)
    graph.edit_property(person2, "location", country2)
    graph.edit_property(person1, "age", 18)
    graph.edit_property(person2, "age", 22)
    graph.edit_property(country1, "continent", continent1)
    graph.edit_property(country2, "continent", continent1)
    aggregation_paths = graph.categorical_aggregation_paths([person1, person2])

    aggregations = [
        {
         "depth": aggregation_paths.iloc[0]["depth"],
         "pointing_property": aggregation_paths.iloc[0]["pointing_property"],
         "aggregation_type": aggregation_paths.iloc[0]["aggregation_type"]
        },
        {
         "depth": aggregation_paths.iloc[1]["depth"],
         "pointing_property": aggregation_paths.iloc[1]["pointing_property"],
         "aggregation_type": aggregation_paths.iloc[1]["aggregation_type"]
        }
    ]

    def agg_fun_mean(vals):
        return statistics.mean(vals)

    res = graph.categorical_aggregation(
        ids = [person1, person2],
        value_property = "age",
        aggregation_fun = agg_fun_mean,
        aggregations = aggregations)

    assert {"value": 18, "group": (country1, continent1)} in res
    assert {"value": 22, "group": (country2, continent1)} in res

def test_get_expected_pointed_type(mock_graph_with_person_hometown_schema):
    graph = mock_graph_with_person_hometown_schema
    person_id = graph.create_from_type("person")
    res = graph.get_expected_pointed_type(person_id, "name")
    assert res == "string"
    res = graph.get_expected_pointed_type(person_id, "hometown")
    assert res == "city"

def test_raise_if_id_not_expected_type_riases(mock_graph_with_person_hometown_schema):
    graph = mock_graph_with_person_hometown_schema
    city_id = graph.create_from_type("city")
    with pytest.raises(AssertionError) as exc_info:
        graph.raise_if_id_not_expected_type(city_id, "person")
    assert exc_info.value.args[0] == f"Entity '{city_id}' has type 'city'. Expected type 'person'."
