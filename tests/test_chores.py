"""Unit tests for core/scripts/chores.py: fair, repeatable chore plans."""
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "core" / "scripts"))
sys.path.insert(0, str(ROOT / "evals" / "fixtures"))
import chores  # noqa: E402
import make_household  # noqa: E402

TODAY = "2026-11-13"
MONDAY = date(2026, 11, 16)


def run(*argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = chores.main([str(a) for a in argv])
    return code, json.loads(buf.getvalue())


def register(people, chore_list, plans=None):
    data = chores.empty()
    data["people"] = people
    data["chores"] = [dict(id=f"ch-{i + 1:03d}", **c) for i, c in enumerate(chore_list)]
    data["plans"] = plans or []
    return data


ADULTS = [{"name": "Anna", "share": 1.0}, {"name": "Piotr", "share": 1.0}]
CHILD = {"name": "Zosia", "share": 0.5, "birth_year": 2016}


class Fairness(unittest.TestCase):
    def test_same_input_same_plan(self):
        data = register(ADULTS + [CHILD], [{"title": "Dishes", "per_week": 7, "effort": 1},
                                            {"title": "Bins", "per_week": 2, "effort": 1, "min_age": 8}])
        self.assertEqual(chores.plan(data, MONDAY, 4), chores.plan(data, MONDAY, 4))

    def test_equal_shares_stay_within_one_effort(self):
        data = register(ADULTS + [{"name": "Ola", "share": 1.0}],
                        [{"title": f"Job {i}", "per_week": 1 + i % 3, "effort": 1 + i % 3} for i in range(9)])
        res = chores.plan(data, MONDAY, 4)
        self.assertLessEqual(res["spread"], 3)
        loads = res["normalized_load"].values()
        self.assertLessEqual(max(loads) - min(loads), 3)

    def test_share_scales_the_load(self):
        data = register(ADULTS + [CHILD], [{"title": "Dishes", "per_week": 7, "effort": 1},
                                            {"title": "Tidy", "per_week": 3, "effort": 2}])
        res = chores.plan(data, MONDAY, 4)
        self.assertAlmostEqual(res["totals"]["Zosia"] * 2, res["totals"]["Anna"], delta=3)

    def test_old_imbalance_is_paid_back(self):
        past = [{"week": "2026-W46", "start": "2026-11-09", "assignments": [
            {"chore": "ch-001", "person": "Anna", "count": 6, "effort": 6}]}]
        data = register(ADULTS, [{"title": "Dishes", "per_week": 6, "effort": 1}], past)
        week = chores.plan(data, MONDAY, 1)["weeks"][0]
        self.assertEqual(week["load"]["Piotr"], 6)
        self.assertEqual(week["load"]["Anna"], 0)


class Limits(unittest.TestCase):
    def test_min_age_keeps_a_child_off(self):
        data = register(ADULTS + [CHILD], [{"title": "Bathroom", "per_week": 2, "effort": 3, "min_age": 14},
                                            {"title": "Dishes", "per_week": 7, "effort": 1}])
        res = chores.plan(data, MONDAY, 4)
        for wk in res["weeks"]:
            self.assertNotIn("ch-001", [s["chore"] for s in wk["by_person"]["Zosia"]])

    def test_fixed_person_always_gets_it(self):
        data = register(ADULTS, [{"title": "Mowing", "per_week": 1, "effort": 3, "fixed": "Piotr"}])
        for wk in chores.plan(data, MONDAY, 3)["weeks"]:
            self.assertEqual([s["chore"] for s in wk["by_person"]["Piotr"]], ["ch-001"])

    def test_every_other_week(self):
        data = register(ADULTS, [{"title": "Windows", "per_week": 1, "effort": 2, "every_weeks": 2,
                                  "first_week": "2026-W47"}])
        counts = [sum(len(v) for v in wk["by_person"].values()) for wk in chores.plan(data, MONDAY, 4)["weeks"]]
        self.assertEqual(counts, [1, 0, 1, 0])

    def test_nobody_eligible_is_reported(self):
        data = register([CHILD], [{"title": "Car wash", "per_week": 1, "effort": 2, "min_age": 16}])
        wk = chores.plan(data, MONDAY, 1)["weeks"][0]
        self.assertEqual(wk["unassigned"][0]["chore"], "ch-001")

    def test_weekly_chore_moves_between_equal_people(self):
        data = register(ADULTS, [{"title": "Bathroom", "per_week": 1, "effort": 3},
                                 {"title": "Hoover", "per_week": 1, "effort": 3}])
        owners = [next(n for n, v in wk["by_person"].items() if any(s["chore"] == "ch-001" for s in v))
                  for wk in chores.plan(data, MONDAY, 4)["weeks"]]
        self.assertEqual(len(set(owners)), 2)


class Register(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="hb-chores-"))
        self.home = self.tmp / "household"
        make_household.write(self.home, date.fromisoformat(TODAY))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_init_reads_members_and_writes_after_approval(self):
        code, out = run("init", self.home, "--today", TODAY, "--dry-run")
        self.assertTrue(out["dry_run"])
        self.assertFalse((self.home / "registers" / "chores.json").exists())
        names = {p["name"]: p for p in out["people"]}
        self.assertEqual(names["Zosia"]["birth_year"], 2016)
        self.assertEqual(names["Zosia"]["share"], 0.5)
        code, out = run("init", self.home, "--today", TODAY)
        self.assertEqual(code, 1)
        self.assertIn("--approved-by", out["errors"][0])
        code, out = run("init", self.home, "--today", TODAY, "--approved-by", "Anna")
        self.assertEqual(code, 0)
        self.assertTrue((self.home / "registers" / "chores.json").exists())

    def test_add_plan_save_balance(self):
        run("init", self.home, "--today", TODAY, "--approved-by", "Anna")
        code, out = run("add", self.home, "--json", '{"title": "Zmywanie", "per_week": 7}',
                        "--today", TODAY, "--approved-by", "Anna")
        self.assertEqual(out["entry"]["id"], "ch-001")
        code, out = run("save-plan", self.home, "--from", "2026-11-16", "--weeks", "2",
                        "--today", TODAY, "--approved-by", "Anna")
        self.assertEqual(code, 0)
        code, out = run("balance", self.home, "--weeks", "8", "--today", "2026-11-30")
        self.assertEqual(sum(out["load"].values()), 14)
        self.assertEqual(out["weeks_saved"], ["2026-W47", "2026-W48"])
        log = (self.home / "log" / "decisions.md").read_text(encoding="utf-8")
        self.assertIn("zapisano plan obowiązków na 2026-W47, 2026-W48", log)

    def test_validation_names_the_problem(self):
        run("init", self.home, "--today", TODAY, "--approved-by", "Anna")
        code, out = run("add", self.home, "--json", '{"title": "Odkurzanie", "per_week": 1, "fixed": "Kasia"}',
                        "--today", TODAY, "--dry-run")
        self.assertEqual(code, 1)
        self.assertIn("Kasia", out["errors"][0])

    def test_swap_moves_the_load(self):
        run("init", self.home, "--today", TODAY, "--approved-by", "Anna")
        run("add", self.home, "--json", '{"title": "Odkurzanie", "per_week": 1, "effort": 3}',
            "--today", TODAY, "--approved-by", "Anna")
        code, out = run("save-plan", self.home, "--from", "2026-11-16", "--today", TODAY, "--approved-by", "Anna")
        owner = next(n for n, v in out["plan"]["weeks"][0]["by_person"].items() if v)
        other = "Piotr" if owner != "Piotr" else "Anna"
        code, out = run("swap", self.home, "--week", "2026-W47", "--chore", "ch-001", "--from", owner,
                        "--to", other, "--today", TODAY, "--approved-by", "Anna")
        self.assertEqual(code, 0)
        code, out = run("balance", self.home, "--today", "2026-11-20")
        self.assertEqual(out["load"][other], 3)
        self.assertEqual(out["load"][owner], 0)


    def test_balance_without_plans_is_absent_not_zero(self):
        run("init", self.home, "--today", TODAY, "--approved-by", "Anna")
        code, out = run("balance", self.home, "--today", TODAY)
        self.assertIn("absent, not zero", out["note"])


if __name__ == "__main__":
    unittest.main()
