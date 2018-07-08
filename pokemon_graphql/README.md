# An overview of types

The types in this GraphQL schema can broadly be categorised under the following categories:

 - PokemonSpecies
 - Pokemon
 - Items (including Berries)
 - Moves
 - Game-related data
 - Locations

Pokemon are to PokemonSpecies as Jersey and Angus are to cows: variations within a species. An example is Gyarados, which commonly exists in a red form, but is also found in a rarer blue form called Gyarados-Mega. Another example is Wormadam; Wormadam is the species which can be found in three different varieties, Wormadam-Trash, Wormadam-Sandy and Wormadam-Plant

Items encompass different objects that affect gameplay, such as berries, apricorns, or Pokéballs.


## Pagination

You can page through a connection using `first`/`last` and provide a cursor to `before`/`after` to offset the results. Cursors are provided on the `edge` and in a connection's `pageInfo`. Cursors, like global IDs, should be treated as opaque strings. Their encoded structure may change at any time, so relying on it is strongly discouraged.

## Resource Names

Many resources have `name` identifiers. They are included as a convenience when assembling queries in GraphiQL. Ideally, the end product should display the translated name text and not use the `name` identifier.
