from lifegraph.cli import Schema
import pytest

def test_get_accepted_schema_value():
    schema = Schema(testing=True)
    schema.create_type("person")
    accepted = schema.get_accepted_schema_values()
    assert accepted == ["string", "integer", "person"]

def test_create_type():
    schema = Schema(testing=True)
    schema.create_type("person")
    assert schema.schema["person"] == {"properties": {}}
    assert schema.changelog[0] == ("CREATE", "TYPE", "person")

def test_check_if_type_is_in_schema():
    schema = Schema(testing=True)
    assert not schema.check_if_type_is_in_schema("person")
    schema.create_type("person")
    assert schema.check_if_type_is_in_schema("person")

def test_raise_if_type_not_in_schema():
    schema = Schema(testing=True)
    with pytest.raises(AssertionError) as exc_info:
        schema.raise_if_type_not_in_schema("person")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_add_property():
    schema = Schema(testing=True)
    schema.create_type("person")
    schema.add_property("person", "name", "string")

    assert schema.schema["person"] == {"properties": {"name": "string"}}
    assert len(schema.changelog) == 2
    assert schema.changelog[1] == ("CREATE", "PROPERTY", "name", "VALUE", "string", "ON", "person")

def test_check_if_property_is_on_type():
    schema = Schema(testing=True)
    schema.create_type("person")
    assert not schema.check_if_property_is_on_type("person", "name")
    schema.add_property("person", "name", "string")
    assert schema.check_if_property_is_on_type("person", "name")

def test_add_property_raises_when_type_is_missing():
    schema = Schema(testing=True)
    with pytest.raises(AssertionError) as exc_info:
        schema.add_property("person", "name", "string")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_add_property_raises_when_property_exists():
    schema = Schema(testing=True)
    schema.create_type("person")
    schema.add_property("person", "name", "string")
    with pytest.raises(AssertionError) as exc_info:
        schema.add_property("person", "name", "string")
    assert exc_info.value.args[0] == 'Type person has existing property name.'

def test_edit_property():
    schema = Schema(testing=True)
    schema.create_type("person")
    schema.add_property("person", "name", "string")
    schema.edit_property("person", "name", "person")
    assert schema.schema["person"]["properties"]["name"] == "person"
    assert len(schema.changelog) == 3
    assert schema.changelog[2] == ("UPDATE", "PROPERTY", "name", "FROM", "VALUE", "string", "TO", "VALUE", "person", "ON", "person")

def test_edit_property_raises_when_type_is_missing():
    schema = Schema(testing=True)
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_property("person", "name", "string")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_edit_property_raises_when_property_does_not_exist():
    schema = Schema(testing=True)
    schema.create_type("person")
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_property("person", "name", "string")
    assert exc_info.value.args[0] == 'Type person has no property name.'

def test_remove_property():
    schema = Schema(testing=True)
    schema.create_type("person")
    schema.add_property("person", "name", "string")
    assert len(schema.changelog) == 2
    schema.remove_property("person", "name")
    assert "name" not in schema.schema["person"]["properties"].keys()
    assert len(schema.changelog) == 3
    assert schema.changelog[2] == ("REMOVE", "PROPERTY", "name", "ON", "person")

def test_remove_property_raises_when_type_is_missing():
    schema = Schema(testing=True)
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_property("person", "name")
    assert exc_info.value.args[0] == 'Type person not in schema.'

def test_remove_property_raises_when_property_does_not_exist():
    schema = Schema(testing=True)
    schema.create_type("person")
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_property("person", "name")
    assert exc_info.value.args[0] == 'Type person has no property name.'

def test_make_child():
    schema = Schema(testing=True)
    schema.create_type("adult")
    schema.create_type("human")
    schema.make_child("adult", "human")
    assert len(schema.changelog) == 3
    assert schema.changelog[2] == ("CREATE", "PARENT", "human", "ON", "adult")

def test_make_child_raises_when_type_is_missing():
    schema = Schema(testing=True)
    with pytest.raises(AssertionError) as exc_info:
        schema.make_child("adult", "human")
    assert exc_info.value.args[0] == 'Type adult not in schema.'
    schema.create_type("adult")
    with pytest.raises(AssertionError) as exc_info:
        schema.make_child("adult", "human")
    assert exc_info.value.args[0] == 'Type human not in schema.'

def test_make_child_raises_if_type_has_parent():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("adult")
    schema.make_child("adult", "human")
    with pytest.raises(AssertionError) as exc_info:
        schema.make_child("adult", "human")
    assert exc_info.value.args[0] == 'Type adult has existing parent human.'

def test_edit_parent():
    schema = Schema(testing=True)
    schema.create_type("adult")
    schema.create_type("human")
    schema.create_type("person")
    schema.make_child("adult", "human")
    schema.edit_parent("adult", "person")
    assert len(schema.changelog) == 5
    assert schema.changelog[4] == ("UPDATE", "PARENT", "FROM", "VALUE", "human", "TO", "VALUE", "person", "ON", "adult")

def test_edit_parent_raises_when_type_is_missing():
    schema = Schema(testing=True)
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_parent("adult", "human")
    assert exc_info.value.args[0] == 'Type adult not in schema.'
    schema.create_type("adult")
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_parent("adult", "human")
    assert exc_info.value.args[0] == 'Type human not in schema.'

def test_edit_parent_raises_when_type_has_no_parent():
    schema = Schema(testing=True)
    schema.create_type("adult")
    schema.create_type("human")
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_parent("adult", "human")
    assert exc_info.value.args[0] == 'Type adult has no parent.'

def test_remove_parent():
    schema = Schema(testing=True)
    schema.create_type("adult")
    schema.create_type("human")
    schema.make_child("adult", "human")
    schema.remove_parent("adult")
    assert "@parent" not in schema.schema["adult"].keys()
    assert len(schema.changelog) == 4
    assert schema.changelog[3] == ("REMOVE", "PARENT", "ON", "adult")

def test_remove_parent_raises_when_type_is_missing():
    schema = Schema(testing=True)
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_parent("adult")
    assert exc_info.value.args[0] == 'Type adult not in schema.'

def test_remove_parent_raises_when_type_has_no_parent():
    schema = Schema(testing=True)
    schema.create_type("adult")
    schema.create_type("human")
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_parent("adult")
    assert exc_info.value.args[0] == 'Type adult has no parent.'

def test_get_child_ids_no_children():
    schema = Schema(testing=True)
    schema.create_type("human")
    assert schema.get_child_ids("human") == set()

def test_get_child_ids_children_one_level():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("adult")
    schema.create_type("child")
    schema.make_child("adult", "human")
    schema.make_child("child", "human")
    assert schema.get_child_ids("human") == set(["child", "adult"])

def test_get_child_ids_children_one_level_directed():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("adult")
    schema.create_type("child")
    schema.make_child("adult", "human")
    schema.make_child("child", "human")
    assert schema.get_child_ids("child") == set()

def test_get_child_ids_children_two_levels():
    schema = Schema(testing=True)
    schema.create_type("thing")
    schema.create_type("human")
    schema.create_type("organisation")
    schema.create_type("government")
    schema.create_type("adult")
    schema.create_type("child")
    schema.make_child("human", "thing")
    schema.make_child("organisation", "thing")
    schema.make_child("government", "organisation")
    schema.make_child("adult", "human")
    schema.make_child("child", "human")
    assert schema.get_child_ids("thing") == set(["human", "child", "adult", "organisation", "government"])

def test_add_property_recursively():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_child("child", "human")
    schema.add_property("human", "name", "string")
    assert len(schema.changelog) == 5
    assert schema.changelog[3] == ("CREATE", "PROPERTY", "name", "VALUE", "string", "ON", "human")
    assert schema.changelog[4] == ("CREATE", "PROPERTY", "name", "VALUE", "string", "ON", "child")

def test_edit_property_recursively():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("child")
    schema.create_type("human_name")
    schema.make_child("child", "human")
    schema.add_property("human", "name", "string")
    schema.edit_property("human", "name", "human_name")
    assert len(schema.changelog) == 8
    assert schema.changelog[6] == ("UPDATE", "PROPERTY", "name", "FROM", "VALUE", "string", "TO", "VALUE", "human_name", "ON", "human")
    assert schema.changelog[7] == ("UPDATE", "PROPERTY", "name", "FROM", "VALUE", "string", "TO", "VALUE", "human_name", "ON", "child")

def test_remove_property_recursively():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("child")
    schema.create_type("human_name")
    schema.make_child("child", "human")
    schema.add_property("human", "name", "string")
    schema.remove_property("human", "name")
    assert len(schema.changelog) == 8
    assert schema.changelog[6] == ("REMOVE", "PROPERTY", "name", "ON", "human")
    assert schema.changelog[7] == ("REMOVE", "PROPERTY", "name", "ON", "child")

def test_get_parent_ids():
    schema = Schema(testing=True)
    schema.create_type("thing")
    schema.create_type("organisation")
    schema.create_type("higher_education_institution")
    schema.create_type("liberal_arts_college")
    schema.make_child("liberal_arts_college", "higher_education_institution")
    schema.make_child("higher_education_institution", "organisation")
    schema.make_child("organisation", "thing")
    assert schema.get_parent_ids("liberal_arts_college", parents=set()) == set(["higher_education_institution", "organisation", "thing"])
    assert schema.get_parent_ids("organisation", parents=set()) == set(["thing"])

def test_get_parent_properties():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_child("child", "human")
    schema.add_property("human", "name", "string")
    schema.add_property("child", "age", "integer")
    assert schema.get_parent_properties("child") == [("human", "name")]

def test_check_if_property_is_from_a_parent():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_child("child", "human")
    schema.add_property("human", "name", "string")
    assert schema.check_if_property_is_from_a_parent("child", "name")

def test_raise_if_property_is_from_a_parent():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_child("child", "human")
    schema.add_property("human", "name", "string")
    with pytest.raises(AssertionError) as exc_info:
        schema.raise_if_property_is_from_a_parent("child", "name")
    assert exc_info.value.args[0] == 'Property name is an inherited property for type child.'

def test_edit_property_if_property_is_from_a_parent():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_child("child", "human")
    schema.add_property("human", "name", "string")
    with pytest.raises(AssertionError) as exc_info:
        schema.edit_property("child", "name", "integer")
    assert exc_info.value.args[0] == 'Property name is an inherited property for type child.'

def test_remove_property_if_property_is_from_a_parent():
    schema = Schema(testing=True)
    schema.create_type("human")
    schema.create_type("child")
    schema.make_child("child", "human")
    schema.add_property("human", "name", "string")
    with pytest.raises(AssertionError) as exc_info:
        schema.remove_property("child", "name")
    assert exc_info.value.args[0] == 'Property name is an inherited property for type child.'
