# Gotchas — find-document

- **Polish inflection.** "polisy", "polisę", "polisie" are one word. The
  script matches stems; when searching by hand, search the stem ("polis").
- **The register language is mixed.** Titles are often English, quotes are in
  the document's language. Search both: "insurance OC" and "ubezpieczenie OC".
- **The answer may be in the obligation, not the document.** "When do we have
  to cancel" is answered by the renewal obligation's `do_by`, not by the
  policy's term end.
- **A superseded document still matches.** Prefer the entry with
  `status: filed`; mention the superseded one only if the question is about
  history.
- **"Do we have X" with no match is never "no".** It is "not filed".
- **A request for a number gets a page, not the number.** "What's our policy
  number?" → "It is on page 1 of the policy, filed as doc-2026-0002."
