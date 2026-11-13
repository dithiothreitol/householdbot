# Quickstart

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

Choose the quick setup (about two minutes): your country, who lives with you,
and what takes the most time. Choose where the household folder lives; a
folder in a synced drive lets two adults share it. HouseholdBot shows the
profile and creates the folder only after you say yes.

## 3. File one paper

Send a photo or PDF of a bill, a policy or a letter, or paste an email. You
get back what it is, what it says, what it wants by when, and a proposal for
where to file it. Say yes, and it is filed with its deadline.

## 4. Use it

| Say | What happens |
|---|---|
| "what's due" / "co mamy do zapłacenia" | deadlines by urgency, overdue first |
| "I paid it" / "zapłaciłam" | closes the item and prepares next month's |
| "where is the car insurance" / "gdzie jest polisa" | the document, the fact, the page |
| "I got this on Tuesday, how long do I have?" | the deadline with holidays counted |
| "weekly brief" / "przegląd tygodnia" | one page on the week |
| "we sold the car" | the profile change and the reminders it closes |
| "check my record" | a health check of the folder |

## Python

Two bundled scripts count dates and check the registers. Claude Code and
Cowork run them with Python 3 when it is installed; claude.ai runs them in its
code sandbox. Without Python, HouseholdBot follows the same rules by hand and
marks computed dates "verify".
