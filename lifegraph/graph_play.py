import json
from graph import Graph

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

    print(graph.categorical_aggregation_paths([eor1, eor2, eor3, eor4]))


    #print(json.dumps(graph.graph, indent=4))

def main():
    chad_graph()

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
