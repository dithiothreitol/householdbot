# The dashboard as one HTML file

A page the household opens in any browser, offline, and prints on A4 or
Letter. It holds the same content as the page shown in chat, nothing more,
and it is saved only after that page was shown and a member said yes.

## Rules

- **One file.** `<!doctype html>`, `<html lang="pl">` or `"en"` (the
  household's language), `<meta charset="utf-8">`, a viewport line, a
  `<title>`, and one `<style>` block. Nothing else in the head.
- **Nothing runs and nothing loads.** No `<script>`, no `on…=` attributes,
  no `<link>`, no `@import`, no web fonts, no `<img>`, `<iframe>`, `<object>`
  or `<form>`, no `url(…)` in the styles. The page works with no network.
- **No links from the record.** An address, a payment link or a web page
  named in a register or a document stays plain text, or is left out.
- **Every value from the record is text.** Titles, notes, names, key facts and
  list items are escaped before they go into the page: `&` becomes `&amp;`
  first, then `<` `&lt;`, `>` `&gt;`, `"` `&quot;` and `'` `&#39;`. A value
  that contains markup is shown as the characters it is.
- **Urgency in words as well as marks.** "overdue", "next 7 days", "start now"
  print in black and white; an emoji or a colour is extra.
- **The same facts as the chat page.** Dates with weekdays, amounts with
  their currency, provenance tags in the household's language (the
  `provenance_local` of the script's rows), neutral health titles, no
  identifiers, and the *not tracked* lines.
- **The footer says what it is:** when it was made (weekday and date), from
  which record (the profile's label), that it is a snapshot and the record is
  the source, and that nothing on it was paid, sent or changed by making it.

## Skeleton

Replace every `{…}`; repeat a row or a section as needed; delete a section
the household does not use only when its *not tracked* line says so.

```html
<!doctype html>
<html lang="{en or pl}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{Household dashboard / Stan gospodarstwa}, {today with weekday}</title>
<style>
  body { font: 15px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
         color: #1a1a1a; background: #fff; margin: 0 auto; max-width: 960px; padding: 16px; }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .asof { color: #555; margin: 0 0 16px; }
  section { border: 1px solid #ccc; border-radius: 6px; padding: 10px 14px;
            margin: 0 0 12px; break-inside: avoid; }
  h2 { font-size: 16px; margin: 0 0 8px; }
  table { width: 100%; border-collapse: collapse; }
  th, td { text-align: left; padding: 4px 6px; border-bottom: 1px solid #e3e3e3;
           vertical-align: top; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  .band { font-weight: 600; white-space: nowrap; }
  .tag, .gap { color: #555; font-size: 13px; }
  .gap { font-style: italic; }
  footer { color: #555; font-size: 13px; margin-top: 16px; }
  @page { margin: 15mm; }
  @media print {
    body { max-width: none; padding: 0; font-size: 11pt; }
    section { border-color: #999; }
  }
</style>
</head>
<body>
<h1>{Household dashboard: label}</h1>
<p class="asof">{As of / Stan na} {today with weekday}</p>

<section>
  <h2>{Overdue and the next 7 days}</h2>
  <table>
    <tr><th>{Last day}</th><th>{What}</th><th>{Who}</th><th>{Amount}</th></tr>
    <tr><td><span class="band">{overdue}</span> {weekday and date}<br>{plan by weekday and date, when earlier}</td>
        <td>{title, escaped} <span class="tag">{tag when not "stated in document"}</span></td>
        <td>{first name}</td><td class="num">{amount with currency}</td></tr>
  </table>
  <p>{Soon: count, nearest item. Coming: count, nearest item.}</p>
  <p>{Start now: …} {Date unknown: each item with its question}</p>
</section>

<section>
  <h2>{Payments this month}</h2>
  <table><!-- pay by, payee, amount --></table>
  <p><strong>{total per currency}</strong> {what it covers}</p>
</section>

<section><h2>{What ends}</h2><!-- documents, vehicle dates, guarantees --></section>
<section><h2>{Insurance}</h2><!-- one row per policy --></section>
<section><h2>{Health and school}</h2><!-- neutral titles only --></section>
<section><h2>{Everyday}</h2><!-- chores, meals, shopping --></section>
<section><h2>{The record's health}</h2><!-- validate, pack age --></section>

<section>
  <h2>{Not tracked}</h2>
  <p class="gap">{one line per area: not tracked / not in the record, and what would start it}</p>
</section>

<footer>{Made on weekday and date from the record "label". A snapshot: the record
is the source. Making this page paid, sent and changed nothing.}</footer>
</body>
</html>
```

## Before the write

Check the finished HTML text once: no `<script`, `<link`, `<img`, `http` or
`url(` anywhere; no `<meta>` besides the charset and viewport lines of the
skeleton; every `<` inside a value escaped; no identifier and no health
detail; the path is `reviews/dashboard-<YYYY-MM-DD>.html`, with `-2` or `-3`
when that name is taken. `record.py save` checks the same and keeps the
characters of the household's language as they are, since the page declares
`utf-8`.
