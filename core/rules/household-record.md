# The household record — one folder of plain files

A business has a ledger and a document system. A household has a drawer and
an inbox. HouseholdBot keeps a small record of its own, so that a fact read
once is never read again: a folder of plain files that the household owns,
can open without Claude, and can share between its members.

Every skill follows these rules before it reads or writes the record.

---

## Layout

```
<household folder>/
  household-profile.md      who lives here, what they own, how they decide
  registers/
    documents.json          index of every filed document
    obligations.json        every deadline, renewal, payment and dated task
    README.md               what the fields mean
    .history/               the previous versions of both registers, kept by record.py
  documents/<YYYY>/         the filed originals (scans, PDFs, saved emails)
  inbox/                    papers waiting to be filed, if the household uses it
  briefs/                   saved weekly briefs
  archive/                  closed obligations of past years
  log/decisions.md          what was approved, by whom, when
  packs/                    the household's own country pack, where none is bundled (optional)
  reviews/                  saved dashboards (optional)
  skills/                   the household's own skills, when kept with the record (optional)
```

Both registers are JSON with a `schema_version`. `record.py` (in the skill's
`shared/scripts/`) creates, checks and writes them. The profile templates ship
in `shared/templates/en/` and `shared/templates/pl/`; a Polish profile has
Polish headings that map one to one onto the English ones, and every skill
reads either. Household data never goes into the plugin folder: it is
replaced on every update.

The household chooses where the folder lives. A folder inside a synced drive
(Google Drive, OneDrive, Dropbox, iCloud) is how two adults share one record
without any server.

---

## Finding the record

**No shell is not no record.** The record is plain files. When the scripts
cannot run, open `household-profile.md` and `registers/*.json` with the Read
tool and answer from them; never say the record could not be read because a
script did not start.

Look in this order and stop at the first hit. `record.py locate` runs steps 1
and 2. Run it as `record.py locate --start "<the session's working folder>"`,
by the script's full path, from that folder: started inside the plugin's own
folder it finds nothing and says so in its `hint`. Before saying the household
is not set up, look for `household-profile.md` in the working folder yourself.

1. **The working folder.** The current folder, or a folder the user attached
   to the session, or one of its direct subfolders, contains
   `household-profile.md`.
2. **The pointer.** `~/.claude/plugins/config/householdbot/location.md` holds
   one line: the absolute path of the household folder on this machine.
   Confirm `household-profile.md` exists there before trusting it.
3. **Connected document storage.** Only when the user says the record lives
   there: find the folder by the name the user gives and work through the
   connector.
4. **Not found.** Say once that the household is not set up and that
   `/householdbot:household-onboard` takes two minutes. A skill that can still
   do useful one-off work (reading a single letter, computing a single
   deadline) does it, and says plainly that nothing was saved.

A profile that still contains `[PLACEHOLDER]` markers counts as not set up for
the sections that carry them. `[DEFAULT]` markers are working values chosen by
the quick setup: use them, and name the default when it shapes an answer.

---

## Writing to the record

1. **Read before write.** Re-read the file immediately before changing it.
   Another member may have changed it since the session started. `record.py`
   always loads the file fresh.
2. **Preview, then wait.** A writing command (`add`, `update`, `complete`,
   `merge`, `archive`, `migrate`, `save`, `export`, `init`, `set-pointer`;
   the writing commands of `chores.py` and `statement.py` too) only previews:
   it checks the change, stores exactly that change and prints `preview`
   (the lines the log will get), `files` and a `confirm` token. Nothing is
   written. Show the household in plain words what will be added or changed
   and where, and wait for a yes (approval gates). The entry goes to the
   script on standard input (`--file -` with a here-document, as the
   untrusted-content rule shows); no file is written to prepare it, and text
   from a document never goes on the command line. Without a shell, the entry
   is shown in plain words and nothing is written before the yes.
3. **Commit with the approver's name.** After the yes:
   `record.py commit "<root>" --confirm <token> --approved-by "<the approver's name only>"`
   (a name such as `Anna`, never their words; `chores.py commit` and
   `statement.py commit` do the same). Commit applies the previewed change and
   nothing else, keeps the previous file in `registers/.history/` and appends
   one line per change to `log/decisions.md`. It refuses a token that is
   unknown, older than 30 minutes, or whose files changed since the preview:
   preview again and show the new change. The old one-call form
   (`add … --approved-by`) is refused. In Claude Code and Cowork the host then
   asks the member to confirm in its own permission prompt, which shows the
   preview line; that prompt is the member's yes reaching the record.
4. **One preview per register per yes.** Several entries of one register go
   into one preview: `add --file -` takes a JSON list, `complete` takes
   `--id` more than once. Two previews of the same register cannot both be
   committed, because the first commit changes the file the second one
   checked. Previews of different registers (a document and its obligations)
   are committed one after the other after the same yes.
5. **"Change" is not a yes.** An edit asked for before the yes ("change the
   title", "add the court's name") makes a new preview, shown again; the old
   token is left to expire.
6. **Files go through `save`.** A brief, a page, a list, a pack, a skill or
   an export is written with
   `record.py save "<root>" --to <folder>/<file> --file -` (the content on
   standard input; `--replace` for a file updated in place, such as a list,
   with the old version kept in `registers/.history/`), then committed the
   same way. `save` writes only into `briefs/`, `reviews/`, `lists/`,
   `packs/`, `skills/`, `exports/`, `drafts/` and `household-profile.md`,
   refuses identifiers, and refuses a page with a script, a link, an image
   or a web address. The host's own write tool is not used inside the
   household folder.
7. **Touch one entry.** Add or update the entries concerned. Do not
   reorder, reformat or rewrite the rest of the file.
8. **Nothing is deleted.** An entry that no longer applies changes `status`
   (`superseded`, `cancelled`, `done`, `lapsed`). An original document is never
   overwritten or removed; a name clash gets a numeric suffix.
9. **Identifiers.** Documents are `doc-YYYY-NNNN`, obligations are
   `ob-YYYY-NNNN`, where `YYYY` is the year the entry was created. The script
   assigns the next free number.
10. **Conflict copies stop writes.** If a synced drive left a conflict copy of a
   register (`obligations (1).json`, `obligations (Anna's conflicted copy).json`,
   `obligations-LAPTOP.json`), writing could lose an edit. The script refuses;
   `household-doctor` merges.

**Without Python.** When the script cannot run, edit the JSON file directly
under the same rules: re-read it, append or change one entry with every field
of the schema, keep the file valid JSON, append the log line by hand, and say
that the write was made without the checking script and that
`household-doctor` will check it next time.

---

## Sessions without a file system

Chat on the web and on phones cannot read or write a local folder.

- If a document-storage connector is connected and the household folder lives
  there, read and write through the connector under the same rules.
- Otherwise work from what the user uploads or pastes, produce the new or
  changed register entries as text or a file for the user to add to the
  folder, and say that nothing was saved by the plugin itself.

Never tell a user something was filed when it was only shown.

---

## What the record is not

- Not a copy of sensitive identifiers. The register points to the document
  and page that hold them (personal data).
- Not a ledger. Amounts in `obligations.json` describe what is due, not what
  was paid from which account.
- Not a memory of conversations. It holds facts with a source, not chat
  history.
