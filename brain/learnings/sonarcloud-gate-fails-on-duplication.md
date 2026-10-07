---
name: sonarcloud-gate-fails-on-duplication
description: "SonarCloud Code Analysis can fail with 0 open issues because new_duplicated_lines_density is over 3%; find the block via the measures API, often a copied test fixture"
type: reference
source: "observed 2026-09-30 on a pull request in a public Python repo"
created: 2026-09-30
modified: 2026-10-07
status: active
visibility: public
---

A red `SonarCloud Code Analysis` check does not mean there are issues to fix. The issues API returned `total 0` while the gate was `ERROR` on `new_duplicated_lines_density 4.2 GT 3`.

**Why:** fixing the two reported code smells left the check red; the cause was a quality-gate condition, not an issue. The duplicates were a security guard (a ref-validation regex plus a `git show` call) copied into three scripts, then a git test fixture copied between two test files.

**How to apply:**

- Read the gate first: `curl -s "https://sonarcloud.io/api/qualitygates/project_status?projectKey=<key>&pullRequest=<n>"` and look for conditions whose status is not `OK`.
- Locate duplicated files: `curl -s "https://sonarcloud.io/api/measures/component_tree?component=<key>&pullRequest=<n>&metricKeys=new_duplicated_lines,duplicated_blocks&qualifiers=FIL"`. The `duplications/show` endpoint returned nothing for a PR.
- Fix by sharing the code (a small module, or `tests/conftest.py` for fixtures), not by excluding files from analysis. Tests count toward the metric.

Related: [[github-pr-checks-stall-causes]].
