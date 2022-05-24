import json
from graph import Graph
from statistics import mean

def agg_fun_mean(vals):
    return mean(vals)

def chad_graph():
    graph = Graph(data_path=None)
    # schema definition
    graph.schema.create_type("country")
    graph.schema.create_type("continent")
    graph.schema.create_type("estimated_oil_reserves")
    graph.schema.add_property("country", "name", "string")
    graph.schema.add_property("country", "continent", "continent")
    graph.schema.add_property("continent", "name", "string")
    graph.schema.add_property("estimated_oil_reserves", "date", "date")
    graph.schema.add_property("estimated_oil_reserves", "barrels", "integer")
    graph.schema.add_property("estimated_oil_reserves", "country", "country")

    # graph definition
    country1 = graph.create_from_type("country")
    country2 = graph.create_from_type("country")
    continent1 = graph.create_from_type("continent")
    graph.edit_property(country1, "name", "Chad")
    graph.edit_property(country2, "name", "Equatorial Guinea")
    graph.edit_property(continent1, "name", "Africa")
    graph.edit_property(country1, "continent", continent1)
    graph.edit_property(country2, "continent", continent1)
    eor1 = graph.create_from_type("estimated_oil_reserves")
    eor2 = graph.create_from_type("estimated_oil_reserves")
    eor3 = graph.create_from_type("estimated_oil_reserves")
    eor4 = graph.create_from_type("estimated_oil_reserves")
    eor5 = graph.create_from_type("estimated_oil_reserves")
    eor6 = graph.create_from_type("estimated_oil_reserves")

    graph.edit_property(eor1, "date", "2019")
    graph.edit_property(eor1, "barrels", 10_000_000)
    graph.edit_property(eor1, "country", country1)

    graph.edit_property(eor2, "date", "2020")
    graph.edit_property(eor2, "barrels", 18_000_000)
    graph.edit_property(eor2, "country", country1)

    graph.edit_property(eor3, "date", "2019")
    graph.edit_property(eor3, "barrels", 9_000_000)
    graph.edit_property(eor3, "country", country2)

    graph.edit_property(eor4, "date", "2018")
    graph.edit_property(eor4, "barrels", 8_000_000)
    graph.edit_property(eor4, "country", country2)

    agg_ids = [eor1, eor2, eor3, eor4]
    agg_paths = graph.categorical_aggregation_paths(agg_ids)
    agg_path_i = 0
    agg_result = graph.categorical_aggregation(
        ids=agg_ids,
        value_property="barrels",
        aggregation_fun=agg_fun_mean,
        depth=agg_paths.iloc[agg_path_i]["depth"],
        pointing_property=agg_paths.iloc[agg_path_i]["pointing_property"],
        aggregation_type=agg_paths.iloc[agg_path_i]["aggregation_type"])
    print(agg_result)
    graph.edit_property(eor5, "date", "2018")
    graph.edit_property(eor5, "barrels", 1_000_000)
    graph.edit_property(eor5, "country", country1)

    graph.edit_property(eor6, "date", "2017")
    graph.edit_property(eor6, "barrels", 1_000_000)
    graph.edit_property(eor6, "country", country2)

    agg_ids = [eor1, eor2, eor3, eor4, eor5, eor6]
    agg_paths = graph.categorical_aggregation_paths(agg_ids)
    agg_result = graph.categorical_aggregation(
        ids=agg_ids,
        value_property="barrels",
        aggregation_fun=agg_fun_mean,
        depth=agg_paths.iloc[agg_path_i]["depth"],
        pointing_property=agg_paths.iloc[agg_path_i]["pointing_property"],
        aggregation_type=agg_paths.iloc[agg_path_i]["aggregation_type"])

    print(agg_result)

    #print(json.dumps(graph.graph, indent=4))
    # need to think / figure out how to handle missingness(unknownness) natively
    # need to add generalisation (same hierarchy level)
    # handle date aggregation - yes (multivariate aggregations? - maybe not.)
    # also how to persist results of aggregation
    # then - schema changes should propagate to the graph

def time_with_children():
    graph = Graph(data_path=None)
    # agg by country, gender, continent, and planet
    graph.schema.create_type("human_gender_group")
    graph.schema.create_type("estimated_time_to_raise_a_child")
    graph.schema.create_type("country")
    graph.schema.create_type("continent")
    graph.schema.create_type("planet")
    graph.schema.add_property("human_gender_group", "name", "string")
    graph.schema.add_property("country", "name", "string")
    graph.schema.add_property("country", "continent", "continent")
    graph.schema.add_property("continent", "name", "string")
    graph.schema.add_property("planet", "name", "string")
    graph.schema.add_property("continent", "planet", "planet")
    graph.schema.add_property("estimated_time_to_raise_a_child", "time_minutes", "integer")
    graph.schema.add_property("estimated_time_to_raise_a_child", "country", "country")
    graph.schema.add_property("estimated_time_to_raise_a_child", "human_gender_group", "human_gender_group")

    gender1 = graph.create_from_type("human_gender_group")
    gender2 = graph.create_from_type("human_gender_group")
    graph.edit_property(gender1, "name", "Male")
    graph.edit_property(gender2, "name", "Female")

    country1 = graph.create_from_type("country")
    country2 = graph.create_from_type("country")
    continent1 = graph.create_from_type("continent")
    continent2 = graph.create_from_type("continent")
    planet1 = graph.create_from_type("planet")
    graph.edit_property(country1, "name", "United Kingdom")
    graph.edit_property(country2, "name", "United States")
    graph.edit_property(continent1, "name", "Europe")
    graph.edit_property(continent2, "name", "North America")
    graph.edit_property(country1, "continent", continent1)
    graph.edit_property(country2, "continent", continent2)
    graph.edit_property(continent1, "planet", planet1)
    graph.edit_property(continent2, "planet", planet1)

    etrc1 = graph.create_from_type("estimated_time_to_raise_a_child")
    etrc2 = graph.create_from_type("estimated_time_to_raise_a_child")
    etrc3 = graph.create_from_type("estimated_time_to_raise_a_child")
    etrc4 = graph.create_from_type("estimated_time_to_raise_a_child")

    graph.edit_property(etrc1, "time_minutes", 55)
    graph.edit_property(etrc1, "country", country1)
    graph.edit_property(etrc1, "human_gender_group", gender1)

    graph.edit_property(etrc2, "time_minutes", 32)
    graph.edit_property(etrc2, "country", country1)
    graph.edit_property(etrc2, "human_gender_group", gender2)

    graph.edit_property(etrc3, "time_minutes", 57)
    graph.edit_property(etrc3, "country", country2)
    graph.edit_property(etrc3, "human_gender_group", gender1)

    graph.edit_property(etrc4, "time_minutes", 20)
    graph.edit_property(etrc4, "country", country2)
    graph.edit_property(etrc4, "human_gender_group", gender2)

    print(json.dumps(graph.graph, indent=4))
    aggregation_ids = [etrc1, etrc2, etrc3, etrc4]
    possible_aggregations = graph.categorical_aggregation_paths(aggregation_ids)
    print(possible_aggregations)
    aggregations = possible_aggregations.drop(["n_groups", "aggregation_proportion"], axis=1).to_dict('records')
    print(json.dumps(aggregations[0], indent=4))

    print(graph.categorical_aggregation(
        ids = aggregation_ids,
        value_property = "time_minutes",
        aggregation_fun = agg_fun_mean,
        aggregations = [aggregations[3]]))


def main():
    time_with_children()

if __name__ == "__main__":
    main()

# playt around and take notes on how this is working
# get a better idea of the ideal use case and then get at it again
# good job so far
# getting data in is pretty hard at the moment
# and remembering what is in the schema is also hard
# and how do we handle uncertainty?
# and how can we handle pointing to multiple entities?
# the goal would be to say - know the oil reserves of some countries and their ranking imperfectly and get a
# global estimate based on systematic generalisations that can be improved with the addition of more data
