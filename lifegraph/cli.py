import sys
from schema import Schema

def free_text_entry(text):

    text_split = text.split(" ")
    lead_text = " ".join(text_split[0:2])

    if "new type" == lead_text:
        schema.create_type(id=text_split[-1])
    if "new property" == lead_text:
        schema.add_property(
            id=text_split[-3],
            property=text_split[-2],
            value_id=text_split[-1])
    if "edit property" == lead_text:
        schema.edit_property(
            id=text_split[-3],
            property=text_split[-2],
            value_id=text_split[-1])
    if "drop property" == lead_text:
        schema.remove_property(
            id=text_split[-2],
            property=text_split[-1])
    if "make parent" == lead_text:
        schema.make_parent(
            parent_id=text_split[-2],
            id=text_split[-1])
    if "edit parent" == lead_text:
        schema.edit_parent(
            id=text_split[-2],
            parent_id=text_split[-1])
    if "drop parent" == lead_text:
        schema.remove_parent(
            id=text_split[-1])

    schema.close()

if __name__ == "__main__":
    data_path = "./data"
    schema = Schema(data_path=data_path)
    free_text_entry(sys.argv[1])
