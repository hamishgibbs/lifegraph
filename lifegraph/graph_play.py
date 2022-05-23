from graph import Graph

def chad_schema():
    graph = Graph(data_path="./data")
    graph.schema.create_type("country")
    graph.schema.create_type("natural_resource")
    graph.schema.create_type("oil_production_observation")
    graph.schema.add_property("natural_resource", "name", "string")
    graph.schema.add_property("country", "name", "string")
    graph.schema.add_property("oil_production_observation", "date", "date")
    graph.schema.add_property("oil_production_observation", "barrels", "integer")
    graph.schema.close()

def chad_graph():
    graph = Graph(data_path="./data")
    graph.create_from_type("country")
    graph.schema.create_type("natural_resource")
    graph.schema.create_type("oil_production_observation")
    graph.schema.add_property("natural_resource", "name", "string")
    graph.schema.add_property("country", "name", "string")
    graph.schema.add_property("oil_production_observation", "date", "date")
    graph.schema.add_property("oil_production_observation", "barrels", "integer")
    graph.schema.close()


def main():
    chad()

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
