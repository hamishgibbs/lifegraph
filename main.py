"""
The Swedish government has confirmed it intends to apply for membership of Nato, \
joining neighbouring Finland in a dramatic decision that marks one of the biggest \
strategic consequences of Russia’s invasion of Ukraine to date.
"""

"""
Swedish Government

Sweden (@country) -> continent -> Europe
Finland (@country) -> continent -> Europe

GS (@government) -> country -> Sweden
GF (@government) -> country -> Finland

GS (@government) -> confirmed -> Application1

Application1 (@eumembershipapplication) -> by -> GS
Application1 (@eumembershipapplication) -> to -> EU
Application1 (@eumembershipapplication) -> applicationStatus -> intended

Application2 (@eumembershipapplication) ->  by -> GF
Application2 (@eumembershipapplication) -> to -> EU
"""

"""
What european countries are applying to the EU?

@eumembershipapplication (constraint: "@eumembershipapplication -> to -> EU")
-> by ->
@government (constraint: "@government -> country -> @country -> continent -> Europe")

What countries are applying to the EU?

@eumembershipapplication (constraint: "@eumembershipapplication -> to -> EU")
-> by ->
@government

When did sweden start to apply for EU membership?

@eumembershipapplication (constraint: @eumembershipapplication -> by -> @government (constraint: @government -> country -> Sweden))
-> start_date -> @date

returns unknown - this means you have reached the edge of your graph

"""
"""
The things that need to happen:

remembering all questions that have been asked and their answers
Show if they fail to resolve with a certain change in the schema

Ensure that every change to the schema is recorded
Check that all data contains all keys (can have a type or be unknown)
Ensure that every inherited type has all the keys of its parent (recorded explicitly in the JSON to start)


add @person -> name -> string
    if type doesn't exist
        CREATED @person
    if this property doesn't exist on this type
        ADDPROPERTY name TO @person
        if this type is a parent of other types ADDPROPERTY to children

remove @company -> country
    if this property is not inherited from a parent
        REMOVEPROPERTY country FROM @company

change @person -> country -> geo_container
    if this property is not inherited from a parent
    CHANGEPROPERTY country FROM @company TO geo_container

"rename" @person -> country -> region
    this should propagate to the data

makeparent -> @human -> @child

removeparent -> @human -> @child

editparent -> @human -> @child

1. set up cli to edit schema files
    write command
    check command
    edit schema
    edit any other schema necessary


Then need to audit data relative to current schema (and apply changes to data when the schema is changed)
Then need to come up with way of getting data into the schema

migration of some data to a different schema representation may be interesting at some point
"""
