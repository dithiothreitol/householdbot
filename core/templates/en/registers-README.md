# Registers

Two JSON files index this household's papers and dates. HouseholdBot writes
them through `record.py`, which checks every entry before it is written, keeps
the previous version in `.history/`, and logs each approved change in
`../log/decisions.md`. You can open and read both files at any time; edit them
by hand only if you are comfortable with JSON, and run a check afterwards
("check my household record").

Both files start with `"schema_version": 1`.

## documents.json

One entry per filed document.

| Field | Meaning |
|---|---|
| `id` | `doc-YYYY-NNNN`, assigned when filed |
| `title` | issuer and what it is, e.g. "Example Insurance: OC policy 2026/27" |
| `type` | e.g. `utility-bill`, `insurance-policy`, `contract`, `tax-decision`, `identity-document` |
| `category` | `home`, `vehicle`, `money`, `tax`, `insurance`, `utilities`, `health`, `children`, `identity`, `work`, `daily`, `other` |
| `issuer` | who sent or issued it |
| `concerns` | members, homes or vehicles it is about |
| `document_date`, `received_date` | dates as `YYYY-MM-DD`; the received date is often unknown |
| `file` | path of the filed original inside this folder |
| `sha256` | fingerprint of the original, used to spot the same file filed twice |
| `key_facts` | facts read from it, each with `page` and a short `quote` |
| `obligations` | ids of the obligations it created |
| `supersedes` | id of the document it replaces |
| `keep_until` | a date, `"permanent"`, or empty |
| `status` | `filed`, `action-needed`, `superseded` |

## obligations.json

One entry per deadline, renewal, payment, expiry or dated task.

| Field | Meaning |
|---|---|
| `id` | `ob-YYYY-NNNN` |
| `series` | shared by every occurrence of one recurring obligation; different obligations from the same document get different series |
| `title`, `kind` | what it is; `kind` is `payment`, `renewal`, `filing`, `response`, `appointment`, `expiry` or `task` |
| `owner`, `subject`, `counterparty` | who handles it, what it concerns, who it is with |
| `due_date` | the deadline as the source or the rule gives it |
| `do_by` | the date the household plans to; reminders use this one |
| `do_by_note` | why `do_by` differs from `due_date` |
| `transit_buffer_days` | days allowed for the payment or letter to arrive (1 for a bank transfer, 5 for domestic post); the next occurrence keeps it |
| `lead_time_days` | start this many days before `do_by` |
| `recurrence`, `recurrence_day` | `none`, `monthly`, `yearly`, `every 2 months`, or free text |
| `amount`, `currency` | `"286.40"` and `PLN` |
| `auto_renews`, `notice` | for contracts: whether it renews, and the notice period, method and transit days |
| `source` | the document, page and quote it came from |
| `provenance` | `stated in document`, `calculated from document`, `country pack rule — verify`, `household pack — verify`, `model calculation — verify`, `told by household member` |
| `law` | the act and article for a statutory date |
| `status`, `done_date` | `open`, `done`, `cancelled`, `lapsed` |

Personal identifiers (PESEL, account and card numbers, document numbers,
passwords) are never written here. An entry says where they are instead:
"policy number: see page 1".

## chores.json

Written by `chores.py`, created only when the household starts a chore
rotation.

| Field | Meaning |
|---|---|
| `people` | who takes part: `name`, `share` (relative capacity; adults 1, children 0.5 by default), `birth_year` for children, `active` |
| `chores` | `id` (`ch-001`), `title`, `per_week` (times in a week it happens), `every_weeks` (1 every week, 2 every other week), `effort` (1 to 5 points each time), `min_age`, `who` (only these people; empty = everyone old enough), `fixed` (always this person), `first_week`, `active`, `notes` |
| `plans` | saved weeks: `week` (`2026-W47`), `assignments` (chore, person, count, effort), `approved_by`, `saved` |

## lists/

Plain Markdown the household can read and edit: `shopping.md` (one section
per shop or aisle), `staples.md` (items bought most weeks) and
`meals-<YYYY>-W<NN>.md` (the week's meals). They hold no health reasons, only
what to buy and cook.
