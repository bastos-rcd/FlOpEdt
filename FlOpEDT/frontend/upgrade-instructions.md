# Instructions to improve the code readability

The goal of this document is to give directions about how to refactor the current Vue CLI project.
It is a condensate of ideas which make use of stores to reduce the components' size and delegate the data handling.

## Stores and Django Rest Framework

In order to abstract the communications between the front and the Django Rest Framework, a generic class called `StoreAction`
has been created and is responsible for making the http requests.

By using this class a store can be used to represent each model of the Rest API. Typically, a model store contains a reference
to a list of objects of this model, defines a type to represent values obtained from the API and a type to represent the 
nested objects described by the foreign keys, uses internal actions to convert from and to both types and exposes an instance
of `StoreAction` using both types and the conversion actions. 

The files `src/stores/department.ts` and `src/stores/room.ts` are examples of how stores could be used to abstract the communications
with the Rest API.

In conclusion, a good improvement of the overall quality of the code would be to convert each model into a store abstracting the
interactions with the Rest API.

## Stores and views

This is another way stores can be used on top of the previous suggestion. Currently, all the data used by the `RoomReservation` view
is created, hold, and altered by the same Vue file, which makes it really large and barely maintainable. A way of leveraging this
is by using a store to handle the data. This store could hold the state of each selected element and be the preferred way of sending
data from a view to its components. The child components' props could then be linked to the store's state and the reactivity of this state
used to update the view.
