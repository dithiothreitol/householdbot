# Quickstart

**English** · [Polski](QUICKSTART.pl.md)

Ten minutes from install to the first filed document.

## 1. Install

**Claude Code** (terminal or IDE)

```
/plugin marketplace add dithiothreitol/householdbot
/plugin install householdbot@householdbot
```

A local copy of this repository works too: give its path to
`/plugin marketplace add`.

**Claude desktop app, Code tab**: in a local session choose **+ > Add
plugins** and add the same marketplace.

**Cowork (Claude desktop app)**: add the marketplace under **Customize >
Plugins**, or download `householdbot.plugin` from the latest release and choose
**Upload plugin**. Give the session access to the folder you want to use for
household papers.

**claude.ai (web)**: install the plugin for your account, or upload single
skills from the release (`skills/<skill>.zip`) in the skills settings, and turn
on code execution so the scripts can run. A chat cannot open a folder on your
computer, so keep the household folder in a connected Google Drive, or save the
files HouseholdBot gives you into your folder yourself.

**Phone**: plugins are not installed on a phone. Remote Control lets the
phone drive a Claude Code session on your computer, which has the plugin.

## 2. Set up

```
/householdbot:household-onboard
```

The first line asks for the language: English is the default, and "po polsku"
switches to Polish. Then choose the quick setup (about two minutes): your
country, who lives with you, and what takes the most time. Choose where the
household folder lives; a folder in a synced drive lets two adults share it.
HouseholdBot shows the profile and creates the folder only after you say yes.

## 3. File one paper

Send a photo or PDF of a bill, a policy or a letter, or paste an email. You
get back what it is, what it says, what it wants by when, and a proposal for
where to file it. Say yes, and it is filed with its deadline. A letter in
another language is explained in yours, with the original quoted.

## 4. Use it

| Say | What happens |
|---|---|
| "what's due" | deadlines by urgency, overdue first |
| "I paid it" | closes the item and prepares next month's |
| "where is the car insurance" | the document, the fact, the page |
| "I got this on Tuesday, how long do I have?" | the deadline with holidays counted |
| "weekly brief" | one page on the week |
| "we sold the car" | the profile change and the reminders it closes |
| "check my record" | a health check of the folder |
| "what do we need to pay" | the payment list with its total; you pay, then say "paid" |
| sends a bank export (CSV) | the month on one page: income, spending, categories, price rises |
| "answer this letter" / "cancel this contract" | a draft in the recipient's language, the date to send by, nothing sent |
| "monthly review" | mail, papers, bills, next month and money in one pass |
| "we bought a car" / "we're moving" | every statutory step with its date, one approval at a time |
| "plan our meals" / "add milk to the list" | a week of meals, then one shopping list grouped by shop |
| "who does what this week" | a fair chore plan by share and age; an adult approves it |
| "what's on this week" | the family's calendars side by side, clashes named |
| "what can we shred" | papers past their keeping date; you shred, nothing is deleted for you |
| "from now on in Polish" | switches the household's language |
| "dashboard" / "everything at a glance" | one page on the whole household: deadlines, money, documents, what is not tracked |
| "make this a skill" | your own skill for a task you repeat, written after your yes |
| "build a country pack for Germany" | a pack from official sources, checked and kept in your folder |

## A weekly brief on a schedule

- **Cowork**: create a weekly scheduled task (Scheduled, in the sidebar) that
  says "weekly brief". Scheduled tasks can use installed plugins; a task that
  needs the household folder on your computer runs only while the computer is
  on.
- **Claude desktop app, Code tab**: a desktop scheduled task in the household
  folder runs while the app is open and the computer is awake.
- **Without a computer that is on**: the managed-agent cookbook
  (`managed-agent-cookbooks/deadline-watcher`) runs the weekly deadline check
  on Anthropic's platform from a copy of the registers. Read its README for
  what is uploaded.
- **Anywhere else** nothing runs by itself: say "weekly brief" on Monday, or
  let HouseholdBot put the dates into your calendar.

## Python

Four bundled scripts count dates, check the registers, add up bank exports
to the cent and plan chores. Claude Code and Cowork run them with Python 3 when
it is installed; claude.ai runs them in its code sandbox. Without Python, HouseholdBot follows the same rules by hand and
marks computed dates "verify".
