# A note on Tests

GraphQL APIs are incredibly flexible. Results can be ordered, filtered, and paged through almost however the client wishes. But that flexibility comes with a down-side: testing each and every possible query becomes much more difficult. The tests in this suite do not attempt to cover every single case, because writing that many tests would take forever. Rather, the tests serve to ensure that everything roughly works as it should, and that changing something in one place hasn't broken something somewhere else.

## What's not covered

In particular, the tests do not cover every `orderBy` and `where` clause. Internally, these use Django model `filter`/`order_by` methods, so if a particular field argument doesn't work, it probably means I made a typo somewhere and that it only breaks if you add that field argument. _Some_ of the field arguments are tested, but not every one.

## What is covered

Everything else is fully tested, to the best of my knowledge. Every field and field resolver is covered in a test. Every Relay node is retrieved by a node ID.
