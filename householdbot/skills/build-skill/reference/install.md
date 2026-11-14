# Installing the household's own skill

A skill is a folder: `SKILL.md`, and here `reference/gotchas.md` beside it in
a `reference` folder. The same folder works in every Claude app; only where it
goes differs. Give these steps in the household's language, for the surface
the member uses. Menu names change between app versions: when a step does
not match the screen, look for "Skills" in the app's settings.

## Claude Code

- **For every project on this computer:** the folder goes to
  `~/.claude/skills/<name>/` (on Windows `C:\Users\<user>\.claude\skills\<name>\`).
- **For one project only:** `.claude/skills/<name>/` inside that project's
  folder.
- Start a new session, then ask for the task with one of its phrases, or call
  it by name.

## Cowork (Claude desktop app)

- The skill can sit in `skills/<name>/` in the household folder, which the
  session can already read; this keeps it with the record and in the
  household's synced drive.
- To have it start by itself from its phrases, add it to the app the same way
  as in claude.ai below: Cowork uses the skills turned on for the account.
- Until then, the member can say "follow skills/<name>/SKILL.md" and Claude
  reads it from the folder.

## claude.ai and the Claude apps

1. Make a ZIP file of the folder `<name>` itself, so that `SKILL.md` sits
   directly inside the folder in the ZIP.
2. In Settings, open the Skills section (under Capabilities in current
   versions) and upload the ZIP. Code execution must be on.
3. Start a new chat and use one of the skill's phrases.

## Changing or removing it

- To change it, edit `SKILL.md` in the folder (or upload the new ZIP) and
  start a new session. `build-skill` can make the change: it shows the
  difference and writes after a yes.
- To remove it, delete the folder or turn the skill off in the settings. The
  household record is not touched either way.
