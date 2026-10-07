---
name: airflow-test-patterns
description: "Apache Airflow contribution test patterns -- template rendering fixture, serialization trap, db_test marker, PR requirements"
type: reference
source: "learned from upstream Apache Airflow test PR review"
created: 2026-10-07
modified: 2026-10-07
status: active
visibility: public
---

- **Template rendering tests:** use the `create_task_instance_of_operator` fixture.
- **Never combine `dag_maker` with `@pytest.mark.need_serialized_dag` for template tests.** Serialization breaks params, so the test fails for reasons unrelated to the change.
- **DB tests:** mark them with `@pytest.mark.db_test`.
- **PR requirements:** fill the PR template, tick the AI-disclosure checkbox, and add a `Generated-by:` line if the change was AI-assisted.

**Why:** these are non-obvious and each cost a review round.

**How to apply:** read this before writing any Airflow test PR, alongside the upstream contributing docs.
