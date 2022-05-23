import pytest
import json
from graph import Graph

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
def mock_graph_with_duration_statistic():
    graph = Graph(data_path=None)
    graph.schema.create_type("human_group_activity_duration_statistic")
    graph.schema.create_type("group")
    graph.schema.create_type("country")
    graph.schema.create_type("city")
    graph.schema.create_type("planet")
    graph.schema.create_type("continent")
    graph.schema.create_type("defense_alliance")
    graph.schema.create_type("activity")
    graph.schema.add_property("group", "name", "string")
    graph.schema.add_property("group", "group", "group")
    graph.schema.add_property("city", "country", "country")
    graph.schema.add_property("country", "name", "string")
    graph.schema.add_property("country", "continent", "continent")
    graph.schema.add_property("country", "defense_alliance", "defense_alliance")
    graph.schema.add_property("planet", "name", "string")
    graph.schema.add_property("continent", "name", "string")
    graph.schema.add_property("continent", "group", "planet")
    graph.schema.add_property("defense_alliance", "name", "string")
    graph.schema.add_property("activity", "name", "string")
    graph.schema.add_property("human_group_activity_duration_statistic", "human_group", "group")
    graph.schema.add_property("human_group_activity_duration_statistic", "location", "country")
    graph.schema.add_property("human_group_activity_duration_statistic", "time", "date")
    graph.schema.add_property("human_group_activity_duration_statistic", "value", "integer")
    graph.schema.add_property("human_group_activity_duration_statistic", "activity", "activity")
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

def test_aggregation_paths(mock_graph_with_duration_statistic):
    graph = mock_graph_with_duration_statistic
    group_id1 = graph.create_from_type("group")
    group_id2 = graph.create_from_type("group")
    planet_id1 = graph.create_from_type("planet")
    continent_id1 = graph.create_from_type("continent")
    defense_alliance_id1 = graph.create_from_type("defense_alliance")
    country_id1 = graph.create_from_type("country")
    city_id1 = graph.create_from_type("city")
    stat_id1 = graph.create_from_type("human_group_activity_duration_statistic")
    activity_id1 = graph.create_from_type("activity")

    graph.graph[planet_id1]["name"] = "earth"
    graph.graph[group_id1]["name"] = "humans"
    graph.graph[group_id2]["name"] = "women"
    graph.graph[group_id2]["group"] = group_id1
    graph.graph[continent_id1]["name"] = "Europe"
    graph.graph[continent_id1]["group"] = planet_id1
    graph.graph[defense_alliance_id1]["name"] = "NATO"
    graph.graph[country_id1]["name"] = "United Kingdom"
    graph.graph[country_id1]["continent"] = continent_id1
    graph.graph[country_id1]["defense_alliance"] = defense_alliance_id1
    graph.graph[city_id1]["country"] = country_id1
    graph.graph[activity_id1]["name"] = "Raising a child"
    graph.graph[stat_id1]["human_group"] = group_id2
    graph.graph[stat_id1]["location"] = country_id1
    graph.graph[stat_id1]["time"] = "2020"
    graph.graph[stat_id1]["value"] = 53
    graph.graph[stat_id1]["activity"] = activity_id1
    stat_id2 = graph.create_from_copy(stat_id1)
    graph.graph[stat_id2]["time"] = "2019"
    graph.graph[stat_id2]["value"] = 50
    graph.graph[stat_id2]["location"] = country_id1


    # print(json.dumps(self.graph, indent=4))
    print(graph.categorical_aggregation_paths([stat_id1, stat_id2]))
    assert False
