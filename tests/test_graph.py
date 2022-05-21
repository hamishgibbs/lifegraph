import pytest
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

def test_create_from_type(mock_graph_with_person_schema):
    graph = mock_graph_with_person_schema
    graph.create_from_type("person")
    assert len(graph.graph.keys()) == 1
    id = list(graph.graph.keys())[0]
    assert graph.graph[id] == {"@type": "person", "name": "string"}

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
    person_ids = graph.get_ids_of_type("person")
    city_ids = graph.get_ids_of_type("person")
    graph.graph[person_ids[0]]["hometown"] = city_ids[0]
    audit_results = []
    audit_results = graph.audit_entity_properties_point_to_correct_type(audit_results)
    assert len(audit_results) == 1
    assert "type person. Expected type city." in audit_results[0]

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
    """
    (a, name, hamish)
    (b, name, peter)
    (a, hometown, syracuse)
    (b, hometown, syracuse)
    - no need to chase down the connections, right?
    """
    # this one is going to be hard! Sets the structure for generalisation also

    print(graph)
    assert False
