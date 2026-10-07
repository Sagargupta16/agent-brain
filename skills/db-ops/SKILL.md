---
name: db-ops
description: >-
  Database work on the user's apps with a read-only-first posture. Inspect
  schema and live data (Neon or another hosted Postgres via its MCP server or
  CLI, local SQLite or Postgres via the repo's own CLI), answer what tables
  and columns exist and whether prod and local point at the same database,
  then on ask author and run migrations (Alembic for Python backends, Drizzle
  for TypeScript ones) against an empty database and a seeded copy, verifying
  row counts before and after. Use when the user says "now see the neon db of
  this project", "did we use the same DB as the other app by mistake?", "why
  is drizzle pushing .sql?", "migrate the local db as well to test", "give me
  the complete schema list", or "DB migrated to new table". Never runs UPDATE
  or DELETE against production without an explicit, specific go-ahead, never
  prints a connection string, and never queries across all users when the
  ask is about one account.
---

# db-ops

Schema, migrations and "which database is this actually pointing at". A
platform skill such as `neon-postgres` (if installed) covers provider
specifics; this skill is the procedure around it.

## Read first

- Your always-on rules, if you keep them. Secrets and boundaries: "can you
  look at prod" is not authorization to write to prod; never query all
  users' rows for a one-account question; tools that "get connection string"
  (for example a Neon connection-URI tool) return a live password inline, so
  never call them, refer to `DATABASE_URL` by name.
- The repo `CLAUDE.md` for its database facts (dialect per environment,
  migration tool, conventions such as an empty `downgrade()`), plus
  `brain recall <repo> database` for anything learned before.
- A provider skill, if installed, for pooled vs direct connections,
  branching, scale-to-zero and instant restore.

## Procedure

1. Identify the database before anything else, read-only: which env var the
   app reads (`DATABASE_URL`, `NEON_DATABASE_URL`, a SQLite path), where it is
   set for dev (`.env.example` names only, never values) and prod (hosting
   env, names only via the platform CLI or MCP), and whether two apps share
   one database project. Print `app | env | host label | dialect | shared with`.
2. Schema inventory: `alembic current` and `alembic history` (Python) or
   `drizzle-kit` introspection (TypeScript); list tables, columns, indexes,
   foreign keys. For a hosted provider use its read tools; for SQLite
   `sqlite3 <db> .schema`. Never a `SELECT` without `LIMIT` on prod.
3. Answer the question asked with that inventory. "Why is drizzle pushing
   .sql" means `drizzle-kit push` is applying a diff directly instead of
   generating a migration file; show the config line that causes it and stop.
4. Migration, only on ask:
   - write it with an up and a down; Alembic autogenerate then read the diff,
     never trust autogenerate blind; Drizzle `generate` then read the SQL
   - run it against an empty database, then against a seeded copy of dev
   - `SELECT count(*)` per affected table before and after; print both
   - one migration per change; never hand-edit migration history
5. Data corrections (recompute a derived column, backfill): dev first, print
   the affected row count, and on prod only after the user names the table
   and the change ("yes update X in prod"); wrap in a transaction, count
   before and after, keep the rollback statement in the receipt.
6. Receipt.

## Output

```
| app | env | host | dialect | shared with |
| <app> | prod | neon (label from the provider) | postgres | none |

| table | rows before | rows after | migration | verified |
| users | 1,204 | 1,204 | 0007_add_index | count + alembic current |

rollback: <exact command or "not applicable">
not done: <prod writes awaiting the user's named go-ahead>
```

## Must not

- Never run UPDATE, DELETE, DROP or TRUNCATE against production without an
  explicit go-ahead that names the table and the change.
- Never print or log a connection string, password or token; env var names
  only; never call a connection-URI tool.
- Never query across all users when the ask is about one account; filter by
  the identity from the first query.
- Never hand-edit applied migration files or the alembic/drizzle history table.
- Never `drizzle-kit push` or `alembic upgrade head` against prod as a way to
  "see if it works"; dev and the seeded copy are for that.
- Never chain commands with a double ampersand; one per line.

## Non-goals

Provider platform specifics (a provider skill, if installed), prod health
checks (`prod-check`), merging the migration PR (`ship`), SQL performance
tuning beyond an index suggestion, and edits to personal data files
(spreadsheets, exports) that are data, not a database.
