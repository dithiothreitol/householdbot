# Gotchas — household-doctor

- **The newest file is not always right.** A conflict copy can be newer and
  still miss entries added on the main file. Merge by entry, not by file.
- **Two devices, one id.** Both members added "the next" obligation offline,
  so both used the same number for different things. The merge renumbers the
  copy's entry; references to it must follow.
- **OneDrive, Drive, Dropbox and iCloud name copies differently:**
  `obligations-LAPTOP.json`, `obligations (1).json`,
  `obligations (Anna's conflicted copy 2026-11-13).json`, `obligations 2.json`.
- **A file in `documents/` without an entry is not an error to delete.** It is
  a paper waiting to be indexed.
- **A register that does not parse** after a hand edit: find the line and
  column from the error, show it, and fix that spot. The previous version is
  in `registers/.history/`.
- **Archiving is not tidying the index.** Only closed obligations move;
  documents stay.
- **Quoting the bad value repeats the leak.** A PESEL found in a register is
  reported by entry and field. Quoting it "so the member can see it" copies
  it into the chat, which is exactly what the check exists to prevent.
