from schema import Schema
import pytest

def test_get_accepted_schema_value():
    schema = Schema(data_path=None)
    schema.create_type("person")
    accepted = schema.get_accepted_schema_values()
    assert accepted == ["string", "integer", "person"]

def test_create_type():
    schema = Schema(data_path=None)
    schema.create_type("person")
    assert schema.schema["person"] == {"properties": {}}
    assert schema.changelog[0] == ("CREATE", "TYPE", "person")

def test_create_type_raises_if_type_exists():
    schema = Schema(data_path=None)
    schema.create_type("person")
    with pytest.raises(AssertionError) as exc_info:
        schema.create_type("person")
    assert exc_info.value.args[0] == 'Type person already exists in schema.'

def test_show_type():
    schema = Schema(data_path=None)
    schema.create_type("person")
    res = schema.show_type("person")
    assert res == {"properties": {}}

def test_show_type_raises_if_type_not_in_schema():
    schema = Schema(data_path=None)
    with pytest.raises(AssertionError) as exc_info:
        schema.show_type("person")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_check_if_type_is_in_schema():
    schema = Schema(data_path=None)
    assert not schema.check_if_type_is_in_schema("person")
    schema.create_type("person")
    assert schema.check_if_type_is_in_schema("person")

def test_raise_if_type_not_in_schema():
    schema = Schema(data_path=None)
    with pytest.raises(AssertionError) as exc_info:
        schema.raise_if_type_not_in_schema("person")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_add_property():
    schema = Schema(data_path=None)
    schema.create_type("person")
    schema.add_property("person", "name", "string")

    assert schema.schema["person"] == {"properties": {"name": "string"}}
    assert len(schema.changelog) == 2
    assert schema.changelog[1] == ("CREATE", "PROPERTY", "name", "VALUE", "string", "ON", "person")

def test_check_if_property_is_on_type():
    schema = Schema(data_path=None)
    schema.create_type("person")
    assert not schema.check_if_property_is_on_type("person", "name")
    schema.add_property("person", "name", "string")
    assert schema.check_if_property_is_on_type("person", "name")

def test_add_property_raises_when_type_is_missing():
    schema = Schema(data_path=None)
    with pytest.raises(AssertionError) as exc_info:
        schema.add_property("person", "name", "string")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_add_property_raises_when_property_exists():
    schema = Schema(data_path=None)
    schema.create_type("person")
    schema.add_property("person", "name", "string")
    with pytest.raises(AssertionError) as exc_info:
        schema.add_property("person", "name", "string")
    assert exc_info.value.args[0] == 'Type person has existing property name.'

def test_edit_property():
    schema = Schema(data_path=None)
    schema.create_type("person")
    schema.add_property("person", "name", "string")
    schema.edit_property("person", "name", "person")
    assert schema.schema["person"]["properties"]["name"] == "person"
    assert len(schema.changelog) == 3
    assert schema.changelog[2] == ("UPDATE", "PROPERTY", "name", "FROM", "VALUE", "string", "TO", "VALUE", "person", "ON", "person")

def test_edit_property_raises_when_type_is_missing():
    schema = Schema(data_path=None)
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_property("person", "name", "string")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_edit_property_raises_when_property_does_not_exist():
    schema = Schema(data_path=None)
    schema.create_type("person")
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_property("person", "name", "string")
    assert exc_info.value.args[0] == 'Type person has no property name.'

def test_remove_property():
    schema = Schema(data_path=None)
    schema.create_type("person")
    schema.add_property("person", "name", "string")
    assert len(schema.changelog) == 2
    schema.remove_property("person", "name")
    assert "name" not in schema.schema["person"]["properties"].keys()
    assert len(schema.changelog) == 3
    assert schema.changelog[2] == ("REMOVE", "PROPERTY", "name", "ON", "person")

def test_remove_property_raises_when_type_is_missing():
    schema = Schema(data_path=None)
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_property("person", "name")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_remove_property_raises_when_property_does_not_exist():
    schema = Schema(data_path=None)
    schema.create_type("person")
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_property("person", "name")
    assert exc_info.value.args[0] == 'Type person has no property name.'

def test_make_parent():
    schema = Schema(data_path=None)
    schema.create_type("adult")
    schema.create_type("human")
    schema.make_parent("human", "adult")
    assert len(schema.changelog) == 3
    assert schema.changelog[2] == ("CREATE", "PARENT", "human", "ON", "adult")

def test_make_parent_raises_when_type_is_missing():
    schema = Schema(data_path=None)
    with pytest.raises(AssertionError) as exc_info:
        schema.make_parent("human", "adult")
    assert exc_info.value.args[0] == 'Type adult not in schema.'
    schema.create_type("adult")
    with pytest.raises(AssertionError) as exc_info:
        schema.make_parent("human", "adult")
    assert exc_info.value.args[0] == 'Type human not in schema.'

def test_make_parent_raises_if_type_has_parent():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("adult")
    schema.make_parent("human", "adult")
    with pytest.raises(AssertionError) as exc_info:
        schema.make_parent("human", "adult")
    assert exc_info.value.args[0] == 'Type adult has existing parent human.'

def test_edit_parent():
    schema = Schema(data_path=None)
    schema.create_type("adult")
    schema.create_type("human")
    schema.create_type("person")
    schema.make_parent("human", "adult")
    schema.edit_parent("adult", "person")
    assert len(schema.changelog) == 5
    assert schema.changelog[4] == ("UPDATE", "PARENT", "FROM", "VALUE", "human", "TO", "VALUE", "person", "ON", "adult")

def test_edit_parent_raises_when_type_is_missing():
    schema = Schema(data_path=None)
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_parent("adult", "human")
    assert exc_info.value.args[0] == 'Type adult not in schema.'
    schema.create_type("adult")
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_parent("adult", "human")
    assert exc_info.value.args[0] == 'Type human not in schema.'

def test_edit_parent_raises_when_type_has_no_parent():
    schema = Schema(data_path=None)
    schema.create_type("adult")
    schema.create_type("human")
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_parent("adult", "human")
    assert exc_info.value.args[0] == 'Type adult has no parent.'

def test_remove_parent():
    schema = Schema(data_path=None)
    schema.create_type("adult")
    schema.create_type("human")
    schema.make_parent("human", "adult")
    schema.remove_parent("adult")
    assert "@parent" not in schema.schema["adult"].keys()
    assert len(schema.changelog) == 4
    assert schema.changelog[3] == ("REMOVE", "PARENT", "ON", "adult")

def test_remove_parent_raises_when_type_is_missing():
    schema = Schema(data_path=None)
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_parent("adult")
    assert exc_info.value.args[0] == 'Type adult not in schema.'

def test_remove_parent_raises_when_type_has_no_parent():
    schema = Schema(data_path=None)
    schema.create_type("adult")
    schema.create_type("human")
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_parent("adult")
    assert exc_info.value.args[0] == 'Type adult has no parent.'

def test_get_child_ids_no_children():
    schema = Schema(data_path=None)
    schema.create_type("human")
    assert schema.get_child_ids("human") == set()

def test_get_child_ids_children_one_level():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("adult")
    schema.create_type("child")
    schema.make_parent("human", "adult")
    schema.make_parent("human", "child")
    assert schema.get_child_ids("human") == set(["child", "adult"])

def test_get_child_ids_children_one_level_directed():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("adult")
    schema.create_type("child")
    schema.make_parent("human", "adult")
    schema.make_parent("human", "child")
    assert schema.get_child_ids("child") == set()

def test_get_child_ids_children_two_levels():
    schema = Schema(data_path=None)
    schema.create_type("thing")
    schema.create_type("human")
    schema.create_type("organisation")
    schema.create_type("government")
    schema.create_type("adult")
    schema.create_type("child")
    schema.make_parent("thing", "human")
    schema.make_parent("human", "adult")
    schema.make_parent("human", "child")
    schema.make_parent("thing", "organisation")
    schema.make_parent("organisation", "government")
    assert schema.get_child_ids("thing") == set(["human", "child", "adult", "organisation", "government"])

def test_add_property_recursively():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_parent("human", "child")
    schema.add_property("human", "name", "string")
    assert len(schema.changelog) == 5
    assert schema.changelog[3] == ("CREATE", "PROPERTY", "name", "VALUE", "string", "ON", "human")
    assert schema.changelog[4] == ("CREATE", "PROPERTY", "name", "VALUE", "string", "ON", "child")

def test_edit_property_recursively():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("child")
    schema.create_type("human_name")
    schema.make_parent("human", "child")
    schema.add_property("human", "name", "string")
    schema.edit_property("human", "name", "human_name")
    assert len(schema.changelog) == 8
    assert schema.changelog[6] == ("UPDATE", "PROPERTY", "name", "FROM", "VALUE", "string", "TO", "VALUE", "human_name", "ON", "human")
    assert schema.changelog[7] == ("UPDATE", "PROPERTY", "name", "FROM", "VALUE", "string", "TO", "VALUE", "human_name", "ON", "child")

def test_remove_property_recursively():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("child")
    schema.create_type("human_name")
    schema.make_parent("human", "child")
    schema.add_property("human", "name", "string")
    schema.remove_property("human", "name")
    assert len(schema.changelog) == 8
    assert schema.changelog[6] == ("REMOVE", "PROPERTY", "name", "ON", "human")
    assert schema.changelog[7] == ("REMOVE", "PROPERTY", "name", "ON", "child")

def test_get_parent_ids():
    schema = Schema(data_path=None)
    schema.create_type("thing")
    schema.create_type("organisation")
    schema.create_type("higher_education_institution")
    schema.create_type("liberal_arts_college")
    schema.make_parent("higher_education_institution", "liberal_arts_college")
    schema.make_parent("organisation", "higher_education_institution")
    schema.make_parent("thing", "organisation")
    assert schema.get_parent_ids("liberal_arts_college", parents=set()) == set(["higher_education_institution", "organisation", "thing"])
    assert schema.get_parent_ids("organisation", parents=set()) == set(["thing"])

def test_get_parent_properties():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_parent("human", "child")
    schema.add_property("human", "name", "string")
    schema.add_property("child", "age", "integer")
    assert schema.get_parent_properties("child") == [("human", "name")]

def test_check_if_property_is_from_a_parent():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_parent("human", "child")
    schema.add_property("human", "name", "string")
    assert schema.check_if_property_is_from_a_parent("child", "name")

def test_raise_if_property_is_from_a_parent():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_parent("child", "human")
    schema.add_property("human", "name", "string")
    with pytest.raises(AssertionError) as exc_info:
        schema.raise_if_property_is_from_a_parent("child", "name")
    assert exc_info.value.args[0] == 'Property name is an inherited property for type child.'

def test_edit_property_if_property_is_from_a_parent():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_parent("human", "child")
    schema.add_property("human", "name", "string")
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_property("child", "name", "integer")
    assert exc_info.value.args[0] == 'Property name is an inherited property for type child.'

def test_remove_property_if_property_is_from_a_parent():
    schema = Schema(data_path=None)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_parent("human", "child")
    schema.add_property("human", "name", "string")
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_property("child", "name")
    assert exc_info.value.args[0] == 'Property name is an inherited property for type child.'
