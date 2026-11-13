# HouseholdBot

[English](README.md) · **Polski**

HouseholdBot to otwarta wtyczka do Claude, która prowadzi domowe sprawy
papierowe w zwykłej rozmowie. Czyta listy, rachunki, umowy i polisy,
archiwizuje je w folderze należącym do gospodarstwa, pilnuje każdego terminu,
odnowienia i daty wypowiedzenia z uwzględnieniem świąt w danym kraju, a na
początek tygodnia przygotowuje krótki przegląd. Niczego nie zapisuje, nie
wysyła i nie płaci bez zgody domownika.

Projekt przenosi na sprawy domowe strukturę otwartych wtyczek branżowych
Anthropic ([knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins),
zwłaszcza small-business, oraz
[claude-for-legal](https://github.com/anthropics/claude-for-legal)): router i
wywiad startowy, wspólne reguły zapisane w każdym skillu, plik profilu,
rejestry z pochodzeniem każdej daty, bramki zgody i agenta, który tylko
odczytuje terminy. Dodaje warstwę dowodową: małe skrypty liczą daty i
sprawdzają rejestry, dzięki czemu model ocenia, a skrypty potwierdzają wynik.

## Języki

HouseholdBot mówi po **angielsku** (domyślnie) i po **polsku**. Konfiguracja
zaczyna się od wyboru języka, a później język zmienia się jednym poleceniem:
„po polsku” albo „in English”. Od języka zależą odpowiedzi, przegląd
tygodnia, zapis dat i kwot (`pt. 20.11.2026`, `1 240,00 zł` albo
`Fri 20 Nov 2026`, `PLN 1,240.00`), szablon profilu i dziennik zgód.
Dokumenty zachowują swój język: anglojęzyczna rodzina w Polsce dostaje polskie
pisma objaśnione po angielsku, z cytatem oryginału, a pisma do polskich
urzędów po polsku, z tłumaczeniem na angielski. Nowy język wymaga plików w
`core/i18n/` oraz `core/templates/<język>/`.

## Zawartość repozytorium

```
.claude-plugin/marketplace.json   marketplace (jedna wtyczka)
householdbot/                     wtyczka
  skills/<skill>/SKILL.md         trzydzieści jeden skilli, każdy samowystarczalny
  skills/<skill>/shared/          generowane kopie reguł, pakietów krajowych, skryptów i szablonów
  agents/                         deadline-watcher (tylko odczyt), document-reader (bez narzędzi zapisu)
evals/                            testy zachowania dla `claude plugin eval`, syntetyczne gospodarstwo;
                                  poza paczką wtyczki, uruchamiane przez scripts/eval.py
core/                             źródła wszystkiego, co trafia do skills/*/shared/
  rules/                          reguły, których przestrzega każdy skill
  locale/PL.md, PL.json           polski pakiet krajowy
  i18n/en.json, pl.json           języki: formaty dat i kwot, notatki, wpisy dziennika
  scripts/dates.py, record.py,    warstwa dowodowa (biblioteka standardowa Pythona)
    statement.py
  money/categories.json           kategorie wydatków dla wyciągów bankowych
  templates/en/, templates/pl/    profil gospodarstwa i opis rejestrów w każdym języku
scripts/sync.py                   kopiuje core/ do skilli
scripts/validate.py               kontrole repozytorium
tests/                            testy jednostkowe skryptów
docs/development-plan.md          plan etapów (po polsku)
```

Każdy skill ma własną kopię tego, czego potrzebuje, ponieważ na claude.ai i w
aplikacjach mobilnych do piaskownicy trafia wyłącznie folder skilla.

## Użycie

Szczegóły zawiera [QUICKSTART.pl.md](QUICKSTART.pl.md). W Claude Code:

```
/plugin marketplace add <ścieżka do tego repozytorium>
/plugin install householdbot@householdbot
/householdbot:household-onboard
```

## Rozwój

```
python scripts/sync.py                       # po każdej zmianie w core/
python scripts/validate.py                   # kontrole repozytorium
python -m unittest discover -s tests         # testy warstwy dowodowej
claude plugin validate ./householdbot --profile directory --strict
python scripts/eval.py --scaffold --allow-tools Write Edit --no-publish   # testy na kopii w build/
```

[CONTRIBUTING.md](CONTRIBUTING.md) opisuje dodawanie skilli, pakietów
krajowych i języków. [CLAUDE.md](CLAUDE.md) zawiera wskazówki do pracy nad
repozytorium w Claude Code. Oba dokumenty są po angielsku.

## Stan

Wersja 0.3 obejmuje rdzeń, pieniądze i korespondencję oraz dom, rodzinę i
codzienność, po angielsku i po polsku: konfigurację, archiwizację dokumentów,
wyszukiwanie, terminy, przegląd tygodnia, zmiany profilu i naprawę rekordu;
pocztę, rachunki, umowy, abonamenty, wyciągi bankowe, listę do rozliczenia PIT,
odpowiedzi na pisma, reklamacje, wypowiedzenia i przegląd miesiąca; dom,
samochód, ubezpieczenia, dokumenty tożsamości i podróże, szkołę, dokumenty
medyczne, plik awaryjny, zdarzenia życiowe, kalendarz rodzinny, posiłki,
zakupy, obowiązki domowe i przegląd roczny; razem z polskim pakietem
krajowym. Ostatni etap doda kolejne kraje, pulpit, tworzenie własnych skilli
i obserwatora terminów działającego bez udziału domowników.
Historię zmian zawiera [CHANGELOG.md](CHANGELOG.md).

## Licencja

Apache License 2.0, zgodnie z plikami [LICENSE](LICENSE) i [NOTICE](NOTICE).
HouseholdBot jest niezależnym projektem, niepowiązanym z Anthropic i
nieposiadającym jego rekomendacji.
