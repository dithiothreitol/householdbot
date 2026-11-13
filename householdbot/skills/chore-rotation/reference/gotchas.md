# Gotchas — chore-rotation

- **Effort is per time, not per week.** Dishes every day at 1 point is 7
  points a week; a weekly bathroom at 3 points is 3. Set `per_week`, not a
  bigger effort.
- **A child's share is a household choice.** 0.5 is only the default; ask
  before changing it, and never lower an adult's share because of a complaint
  in the chat.
- **Fixed chores still count.** Mowing always done by one person is part of
  their load, so the script gives them less of the rest.
- **Seasonal chores are retired, not deleted.** `retire` keeps the history;
  add them back in spring with `update --set active=true`.
- **A plan nobody saved changes nothing.** The balance reads saved weeks only;
  say so when the household follows a plan without saving it.
- **Swaps go through the script.** A swap agreed in the kitchen and not
  recorded makes the next plan unfair to the person who helped.
- **No scorekeeping language.** "Piotr 9 points, Anna 8" is a fact;
  "Piotr did the least" is a judgement the household did not ask for.
- **A child is answered as a child.** In testing, Zosia's request got an
  answer about her in the third person, with script names and week numbers.
  Answer her by name, kindly and simply, and say what an adult does next.
