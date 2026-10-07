---
name: money-cells-in-flex-rows
description: "Amounts in narrow flex rows or table cells truncate unless they use shrink-0 text-right tabular-nums whitespace-nowrap plus a fixed width; codify it in one Money component"
type: feedback
source: "observed 2026-07-04 on a React + Tailwind finance dashboard"
created: 2026-07-04
modified: 2026-10-07
status: active
visibility: public
---

Every amount rendered inside a narrow flex row or a table cell should use the amount-cell rule set:
`shrink-0 text-right tabular-nums whitespace-nowrap font-medium` (`font-semibold` for hero weight), plus a fixed `w-*` when the parent is a flex row.

**Why:** a three-column page used a generic `DataTable` whose `<td>` had no `whitespace-nowrap` and no `table-layout: fixed`. At about 33% viewport width the digits truncated, so `12,913.24` rendered as `12,91`. Two other components had already solved it with a hand-rolled row: `flex items-center gap-2` on the row, `flex-1 min-w-0` on the name and meta block, `shrink-0 w-24 text-right tabular-nums whitespace-nowrap` on the amount. That is the canonical pattern for money in any narrow container.

**How to apply:** codify it once in a primitive instead of repeating the classes:

```tsx
<Money value={amount} width="md" />                   // default font-medium
<Money value={hero}   width="lg" bold className="text-sm" />
<Money value={other}  width="md" muted />              // muted color for rollup rows
```

- Widths map to responsive fixed classes (`sm|md|lg|xl`, for example `w-20 sm:w-24` up to `w-32 sm:w-40`).
- Omit `width` for free-flow contexts (headers, tooltips, hero KPIs). The caller-picks-width contract is intentional; forcing a default width breaks dashboard headers.
- Once the primitive exists, a hand-rolled amount span is drift: migrate it on touch.

Related: [[cap-historical-charts-at-today]].
