**Relational Document Database** 📝

- always operates in terms of JSON objects, but using relational model
- join / aggregates / ... transform shape of final set of JSON objects representing rows
- data stored as proper tables, but with unified types between SQL and JSON
- queries abstracted using query builder to iron out differences between underlying SQLite and our model
