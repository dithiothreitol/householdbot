# Quickstart

**English** · [Polski](QUICKSTART.pl.md)

Ten minutes from install to the first filed document.

## 1. Install

**Claude Code**

```
/plugin marketplace add <path or GitHub repository of HouseholdBot>
/plugin install householdbot@householdbot
```

**Cowork (Claude desktop app)**: add the marketplace in the plugin settings,
install HouseholdBot, and give the session access to the folder you want to
use for household papers.

**claude.ai and the mobile apps**: the skills work in chat once the plugin is
installed for your account and code execution is on. A chat cannot open a
folder on your computer, so keep the household folder in a connected Google
Drive, or save the files HouseholdBot gives you into your folder yourself.

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
| "from now on in Polish" | switches the household's language |

## Python

Three bundled scripts count dates, check the registers and add up bank
exports to the cent. Claude Code and
Cowork run them with Python 3 when it is installed; claude.ai runs them in its
code sandbox. Without Python, HouseholdBot follows the same rules by hand and
marks computed dates "verify".
