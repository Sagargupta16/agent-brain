---
name: cap-historical-charts-at-today
description: "Historical time-series charts must not emit data rows past today; cap at the shared date-range hook, or per series, and leave projection pages alone"
type: feedback
source: "observed 2026-07-04 on a React analytics dashboard with fiscal-year, yearly and monthly views"
created: 2026-07-04
modified: 2026-10-07
status: active
visibility: public
---

For any historical chart (line, area, bar, composed over date or month keys), the data series must not extend past today. Reference lines and goal markers at future dates ARE fine; only the data series is capped.

**Why:** the fiscal-year, yearly and monthly modes of a shared date-range helper returned the full calendar end of the window (a fiscal year running to next March while it was only July). Downstream aggregations emitted zero rows for months past today, which renders as a flat-zero tail on line and area charts and corrupts divisor math (average per day). Separately, a year-in-review hook hard-coded all 12 month labels, so the monthly bar chart showed empty bars for the rest of the year.

**How to apply:**

- **Hook-level fix** (preferred when the caller graph is wide): wrap the range emit point with a `capEndDateAtToday()` helper inside the shared date-range function. It cascades to every analytics endpoint and query hook with no per-caller changes.
- **Site-level fix** (for pre-computed in-memory series): a generic `capSeriesToToday<T>(rows, key)` that compares ISO strings, handles `Date` values, and auto-detects month keys (`YYYY-MM`, length 7) vs day keys (`YYYY-MM-DD`).
- **Fiscal-year month slicing:** `((nowMonth - (fyStart - 1) + 12) % 12) + 1` -- shift to a zero-based fiscal month, mod 12 to handle the wrap, +1 to include the current month.
- **Projection pages** (retirement, multi-year tax planning, FIRE calculators) build their own future ranges and never call the historical helper. Leave them alone.

Related: [[money-cells-in-flex-rows]], [[multi-agent-fanout-workflow]].
