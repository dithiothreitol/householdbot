# Plan implementacji

[English](development-plan.md) · **Polski**

Stan: 2026-11-14, po Etapie 4 (wersja 1.0.0-rc.1). Narzędzie i dokumentacja
są dwujęzyczne: angielski domyślnie, polski do wyboru; dokumenty dla
użytkowników mają wersje `.pl.md`, a dokumenty dla programistów
(CONTRIBUTING, CLAUDE.md, skille, `docs/architecture.md`,
`docs/country-packs.md`) są po angielsku. Plan ma wersję angielską
(`development-plan.md`, domyślną) i tę polską.

---

## 1. Cel i definicja ukończenia

Otwarte (Apache-2.0), w pełni funkcjonalne narzędzie do prowadzenia spraw
gospodarstwa domowego, zbudowane według tych samych wzorców co branżowe wtyczki
Anthropic (`knowledge-work-plugins/small-business`, `claude-for-legal`).
Projekt ma dwa rezultaty: działające narzędzie oraz udokumentowaną analizę
wzorca (`docs/architecture.md`).

Wersja 1.0 jest ukończona, gdy spełnione są wszystkie warunki:

1. Gospodarstwo przechodzi pełną ścieżkę bez pomocy autora: instalacja,
   konfiguracja, zarchiwizowanie dokumentu, lista terminów, przegląd tygodnia.
2. Każdy obszar z rozdziału 4 ma działający skill z przypadkami testowymi.
3. Żadna data ani kwota w wyniku nie pochodzi z niesprawdzonego rachunku modelu
   tam, gdzie dostępne jest wykonanie skryptu.
4. Nic nie zostaje zapisane, wysłane ani zapłacone bez zgody domownika, co
   potwierdzają testy.
5. Wtyczka przechodzi `claude plugin validate --profile directory --strict`,
   walidator repozytorium i listę kontrolną katalogu wtyczek.
6. Pilotaż na realnym gospodarstwie (Twoim) zakończony bez błędów blokujących.
7. Zapis w rekordzie gospodarstwa wykonuje wyłącznie zmianę, która została
   wcześniej pokazana: egzekwują to skrypty, a tam, gdzie gospodarz ma
   hooki, człowiek potwierdza ją w oknie samego gospodarza; jedno i
   drugie potwierdzają testy sesyjne (dodane w Etapie 5).
8. Każdy gospodarz wymieniony w README ma wiersz w tabeli zgodności,
   wypełniony z krytycznego zestawu sesji (dodane w Etapie 6).

---

## 2. Wzorzec referencyjny i jego odwzorowanie

Zweryfikowane na klonach obu repozytoriów (stan z 13.11.2026).

| Element wzorca | Skąd | Odpowiednik w projekcie |
|---|---|---|
| Marketplace: `.claude-plugin/marketplace.json`, wpis na wtyczkę | oba | tak samo |
| Jedna wtyczka z routerem i onboardingiem, 44 skille | small-business | jedna wtyczka, 34 skille |
| `skills/<nazwa>/SKILL.md` + `reference/` (gotchas, przykłady) | small-business | tak samo, każdy skill ma `reference/gotchas.md` |
| `shared/*.md`: reguły przekrojowe | small-business | `core/rules/` kopiowane do każdego skilla |
| Wywiad startowy szybki (2 min) i pełny (15 min), znaczniki `[PLACEHOLDER]` / `[DEFAULT]` | legal | `household-onboard` |
| Profil w pliku poza katalogiem wtyczki, przetrwa aktualizacje | legal | profil w folderze domowym + wskaźnik w `~/.claude/plugins/config/householdbot/` |
| Rejestr z datami, pochodzeniem i cofaniem do dnia roboczego | legal (`renewal-register.yaml`) | `registers/obligations.json` + `dates.py` |
| Skill `customize`: zmiana jednej rzeczy bez ponownego wywiadu | legal | `household-customize` |
| Agent cykliczny tylko do odczytu | legal (`renewal-watcher`) | `deadline-watcher` |
| Łańcuchy skilli z bramką zgody na każdym kroku | small-business | przegląd miesiąca, zdarzenia życiowe, przegląd roczny |
| Bramki zgody: kodowanie i płatność to dwie osobne zgody | small-business | `core/rules/approval-gates.md` |
| Zasada: nie obiecuj harmonogramu, którego nikt nie ustawił | small-business | `core/rules/chain-seams.md` |
| `build-agent`: powtarzalna czynność zamieniona w skill | small-business | `build-skill` |
| Cookbook agenta zarządzanego: `agent.yaml`, podagenci, trzy poziomy uprawnień | legal | `managed-agent-cookbooks/deadline-watcher` |
| Dokumenty repo: README, QUICKSTART, CONNECTORS, CONTRIBUTING, CLAUDE.md | legal | tak samo + SECURITY, CHANGELOG, NOTICE, CODE_OF_CONDUCT |
| Zasada projektowa: SKILL.md sam niesie właściwe zachowanie, reguły wspólne są siatką bezpieczeństwa | legal (CONTRIBUTING) | wiążąca dla każdego skilla |

Różnice zasadnicze: dom nie ma systemu źródłowego (ERP, DMS), więc projekt
dostarcza własny rekord (D2); projekt dodaje warstwę dowodową w skryptach
(D4), której wzorce nie mają.

---

## 3. Decyzje architektoniczne

**D1. Nazwa: `householdbot`.** Decyzja z 13.11.2026. Marketplace i wtyczka
nazywają się `householdbot`, polecenia `/householdbot:<skill>`, nazwa
wyświetlana HouseholdBot, publiczne repozytorium `householdbot`. Nazwa złożona
z dwóch słów ogólnych może trafić w katalogu wtyczek do ręcznej oceny; to
wstrzymanie, nie odrzucenie.

**D2. Rekord domowy jako folder zwykłych plików.** Folder wybrany przez
gospodarstwo (najlepiej w synchronizowanym dysku). Profil, rejestry, oryginały,
przeglądy, archiwum, dziennik decyzji, kopie rejestrów w `registers/.history/`.
Kolejność dostępu: system plików, wskaźnik, konektor magazynu dokumentów, praca
w samej rozmowie z jasnym komunikatem, że nic nie zapisano.

**D3. Rejestry w JSON ze schematem.** Decyzja z 13.11.2026. `documents.json` i
`obligations.json` z `schema_version`. Schemat jest egzekwowany przez
`record.py` (biblioteka standardowa nie ma walidatora JSON Schema), opis pól
w `registers/README.md`. Kwoty jako napisy (`"286.40"`), bez błędów
zmiennoprzecinkowych.

**D4. Warstwa dowodowa: skrypty liczą, model ocenia.** Decyzja z 13.11.2026,
zgodna z wytycznymi Anthropic dla skilli: gotowe skrypty dla operacji
deterministycznych i podatnych na błąd oraz pętla „zaplanuj, sprawdź,
wykonaj”. `dates.py` i `record.py`, tylko biblioteka standardowa, JSON na
wyjściu, Python 3.8+. Bez Pythona skill liczy sam i oznacza wynik
`model calculation — verify`.

**D5. Każdy skill jest samowystarczalny.** Źródła w `core/` (reguły, pakiety
krajowe, skrypty, szablony), kopie w `skills/<skill>/shared/` generowane przez
`scripts/sync.py` według `core/vendor.json`. Reguły trafiają do skilla jako
jeden plik `shared/rules.md` ze spisem treści. Walidator sprawdza, że SKILL.md
nie wskazuje niczego poza własnym folderem i że kopie są aktualne.

**D6. Powierzchnie docelowe.**

| Powierzchnia | Zakres w v1.0 | Stan po Etapie 4 |
|---|---|---|
| Claude Code (terminal, IDE, karta Code w aplikacji) | pełny | zweryfikowane: instalacja z marketplace, sesje ze skryptami na Windows |
| Cowork (desktop) | pełny: pliki, skrypty, agenci, zadania zaplanowane | według dokumentacji: wtyczka z marketplace lub z pliku `householdbot.plugin`, skille, agenci i hooki działają, zadania zaplanowane korzystają z wtyczek; test w pilotażu |
| claude.ai (przeglądarka) | skille i konektory; rekord przez konektor dysku | według dokumentacji: skille wtyczki albo pojedyncze skille z zipów wydania, skrypty w piaskownicy kodu, agenci i hooki pomijani; przypadek testowy z rekordem za konektorem Dysku Google |
| Telefon | sterowanie sesją na komputerze | według dokumentacji: telefon nie instaluje wtyczek, Remote Control steruje sesją Claude Code z wtyczką; test w pilotażu |

**D7. Kraj.** Pakiet krajowy to `core/locale/<CC>.md` (dla modelu) i
`<CC>.json` (dla skryptów: święta z nazwami w języku kraju i po angielsku,
reguły liczenia, doręczenia, terminy, daty ustawowe). Identyfikatory reguł
liczenia są wspólne dla krajów (`administrative`, `tax`, `civil`, `court`,
`calendar`). Każda reguła prawna podaje akt, artykuł i źródło. Formaty dat i
kwot należą do języka, nie do kraju. Drugi pakiet w Etapie 4.

**D14. Języki: angielski domyślny, polski do wyboru.** Decyzja z 13.11.2026.
Kolejność wyboru języka odpowiedzi: prośba w bieżącej wiadomości, potem
`Language` z profilu, a bez profilu język wiadomości, jeśli to angielski lub
polski, w pozostałych przypadkach angielski. Konfiguracja zaczyna od wyboru
języka (pierwsza linia odpowiedzi w obu językach). Dane językowe w
`core/i18n/<lang>.json` (dni, miesiące, formaty dat i kwot, formy liczby
mnogiej, notatki, etykiety pasm, wpisy dziennika); szablony w
`core/templates/<lang>/`; teksty konfiguracji w
`household-onboard/reference/messages.md`. `record.py` czyta język z profilu
(także z polskiego nagłówka „Język”), `dates.py` przyjmuje `--lang`. Język
nie wynika z kraju: anglojęzyczna rodzina w Polsce dostaje polskie pisma
objaśnione po angielsku, z cytatem oryginału, a pisma do polskich urzędów po
polsku, z tłumaczeniem. Rejestry zachowują angielskie nazwy pól i statusów;
tytuły, notatki i dziennik są w języku gospodarstwa. Moja interpretacja
„angielski domyślny”: bez profilu odpowiadam w języku wiadomości (angielski
lub polski), a angielski obowiązuje, gdy nic go nie wskazuje; wariant
„zawsze angielski do czasu wyboru” to zmiana jednej reguły w
`core/rules/locale.md`.

**D8. Konektory.** Poczta, kalendarz, magazyn dokumentów (adresy z wtyczki
small-business). Każdy skill działa bez konektorów.

**D9. Zakres v1.0: pełny.** Decyzja z 13.11.2026. Administracja domu oraz
codzienność: kalendarz rodziny, posiłki, zakupy, podział obowiązków (Etap 3).

**D10. Licencja i atrybucja.** Apache-2.0, `NOTICE` wskazuje źródła wzorca,
README zawiera zdanie o braku powiązania z Anthropic.

**D11. Proaktywność.** Harmonogram tylko tam, gdzie środowisko daje prawdziwe
zadania zaplanowane (zadania zaplanowane Cowork i aplikacji na komputer); w
pozostałych przypadkach uczciwy zamiennik (wpis w kalendarzu). Wariant
bezobsługowy: cookbook agenta zarządzanego z cotygodniowym wdrożeniem
zaplanowanym (Etap 4).

**D12. Format testów zachowania.** Jeden `case.yaml` na przypadek (prompt i
oceniające w jednym pliku) oraz `setup.sh`, który generuje syntetyczne
gospodarstwo z datami liczonymi względem dnia uruchomienia. Powód: limit 512
plików we wtyczce i testy, które się nie starzeją.

**D13. Uprawnienia agentów.** `document-reader` ma tylko `Read` i `Glob`, więc
polecenie wstrzyknięte w dokument nie ma czym działać. `deadline-watcher` ma
narzędzia odczytu i powłokę ograniczoną instrukcją do poleceń czytających
skryptu. Zapis wymaga `--approved-by`, czego agent nie przekazuje.

---

## 4. Zakres funkcjonalny v1.0

Trzydzieści cztery skille (w tym trzy łańcuchy) i dwóch agentów.

### Rdzeń (Etap 1, gotowe)

| Skill | Zadanie |
|---|---|
| `household-onboard` | wybór folderu, wywiad szybki i pełny, pierwszy dokument, przypomnienia z pakietu krajowego, rytm tygodnia |
| `household-router` | wejście: dopasowanie prośby do jednego skilla, proste wyszukania |
| `file-document` | odczyt pisma, przesiew pod kątem oszustw, klasyfikacja, fakty ze stroną i cytatem, terminy ze skryptu, archiwizacja po zgodzie |
| `find-document` | „gdzie jest”, „co tam było napisane”, „kiedy się kończy” |
| `deadline-tracker` | lista terminów, dodanie, wykonanie z następnym wystąpieniem, zaległości, wyliczenie terminu, przypomnienia z pakietu |
| `weekly-brief` | jedna strona na tydzień |
| `household-customize` | zmiana jednej rzeczy w profilu z konsekwencjami w rejestrach |
| `household-doctor` | spójność rekordu, scalanie kopii konfliktowych, migracja schematu, archiwizacja |

Agenci: `deadline-watcher`, `document-reader`.

### Pieniądze i korespondencja (Etap 2, gotowe)

| Skill | Zadanie |
|---|---|
| `inbox-triage` | poczta podzielona na: wymaga decyzji, do archiwum, nic do zrobienia, podejrzane; rachunki i pisma do `file-document`; skrzynka bez zmian bez zgody |
| `bills-due` | stos rachunków, lista płatności do wykonania przez domownika; dwie osobne zgody |
| `contract-check` | umowa lub oferta przed podpisem: okres, odnowienie, zmiany ceny, kary, prawo odstąpienia |
| `subscriptions-review` | koszty cykliczne: podwyżki, nieużywane, koniec promocji, daty wypowiedzenia |
| `budget-snapshot` | wyciąg bankowy: kategorie, obciążenia stałe, porównanie miesięcy |
| `tax-season-organizer` | komplet dokumentów do rozliczenia rocznego według pakietu krajowego; bez składania |
| `reply-to-letter` | odpowiedź, wyjaśnienie lub odwołanie na pismo; termin; projekt do wysłania przez domownika |
| `complaint-and-claim` | reklamacja, zwrot, gwarancja, szkoda: projekt, lista dowodów, termin odpowiedzi |
| `cancel-or-switch` | wypowiedzenie w formie wymaganej umową, data nadania, śledzenie potwierdzenia |
| łańcuch `monthly-review` | rachunki, nowe dokumenty, następny miesiąc, obraz wydatków |

### Dom, rodzina i codzienność (Etap 3, gotowe)

| Skill | Zadanie |
|---|---|
| `home-upkeep` | przeglądy obowiązkowe i sezonowe, gwarancje, historia napraw, porównanie ofert wykonawców |
| `vehicle-file` | ubezpieczenie, badanie techniczne, serwis, mandaty, kupno i sprzedaż |
| `health-file` | wizyty, ważność skierowań i recept, indeks dokumentów; zaostrzone reguły prywatności |
| `school-desk` | pisma i ogłoszenia szkolne: daty, opłaty, zgody, per dziecko |
| `insurance-overview` | wszystkie polisy w jednej tabeli; dublowanie i braki jako pytania |
| `identity-and-travel` | ważność dokumentów, gotowość do wyjazdu |
| `emergency-file` | dokument „gdyby coś się stało” dla drugiego dorosłego: gdzie co jest, bez sekretów |
| `family-calendar` | kto, gdzie, kiedy w tygodniu: kolizje, dowozy, urodziny i imieniny; wpisy do kalendarza po zgodzie |
| `meal-planner` | jadłospis tygodnia z preferencji, alergii (dane wrażliwe), budżetu i czasu; lista składników |
| `shopping-list` | wspólna lista zakupów: z jadłospisu, stałych pozycji i próśb domowników, pogrupowana według sklepu |
| `chore-rotation` | sprawiedliwy podział obowiązków z rotacją i zadaniami dopasowanymi do wieku dzieci |
| łańcuch `life-event` | przeprowadzka, narodziny dziecka, kupno lub sprzedaż auta, zmiana pracy, śmierć bliskiego |
| łańcuch `annual-review` | retencja, przegląd polis i abonamentów, komplet dokumentów podatkowych, archiwum rejestru |

Nowe elementy rekordu w Etapie 3: `registers/chores.json` (obowiązki,
udziały domowników i zapisane plany), folder `lists/` (zakupy, stałe
produkty, jadłospisy), skrypt `chores.py` (plan liczony deterministycznie
według udziału i wieku, z wyrównaniem obciążenia z poprzednich tygodni),
opcjonalna sekcja profilu *Codzienność*.

### Zasięg i rozszerzalność (Etap 4, gotowe)

| Skill | Zadanie |
|---|---|
| `household-dashboard` | jednostronicowy widok całości |
| `build-skill` | powtarzalna czynność domowa zamieniona we własny skill |
| `pack-builder` | utworzenie i weryfikacja pakietu krajowego |

Do tego: cookbook `deadline-watcher`, drugi pakiet krajowy (GB: Anglia i
Walia), pakiety budowane przez gospodarstwo w `packs/` rekordu.

---

## 5. Struktura repozytorium (stan po Etapie 4)

```
.claude-plugin/marketplace.json        marketplace "householdbot"
.github/workflows/validate.yml         sync, walidator (z cookbookiem), testy, claude plugin validate
.github/workflows/release.yml          tag → paczki wydania (build bez prawa zapisu, publikacja osobno)
.github/workflows/evals.yml            testy zachowania z powłoką na Linuksie, uruchamiane ręcznie
README.md QUICKSTART.md CONNECTORS.md (+ .pl.md) CONTRIBUTING.md CLAUDE.md
SECURITY.md CHANGELOG.md CODE_OF_CONDUCT.md NOTICE LICENSE .gitignore
docs/development-plan.md (+ .pl.md) architecture.md country-packs.md
managed-agent-cookbooks/deadline-watcher/   agent zarządzany: agents/, schedule.yaml, cookbook.py, README
core/                                  źródła wszystkiego, co trafia do skilli
  rules/*.md                           14 reguł wspólnych (Etap 2: money, voice; Etap 3: everyday)
  locale/PL.md PL.json GB.md GB.json   pakiety krajowe
  i18n/en.json pl.json                 języki: daty, kwoty, odmiana, notatki, dziennik
  scripts/dates.py record.py           warstwa dowodowa
  scripts/statement.py                 wyciągi bankowe (Etap 2)
  scripts/chores.py                    podział obowiązków (Etap 3)
  money/categories.json                kategorie wydatków w dwóch językach (Etap 2)
  templates/en/ templates/pl/          profil, opis rejestrów w każdym języku
  vendor.json                          który skill dostaje które pakiety
scripts/sync.py validate.py make_icon.py
scripts/eval.py                        testy zachowania na kopii wtyczki w build/ (Etap 2.1)
scripts/package.py                     householdbot.plugin i zip każdego skilla (Etap 4)
tests/test_dates.py test_record.py test_statement.py test_chores.py test_security.py test_cookbook.py
evals/<skill>/<przypadek>/case.yaml setup.sh [mocks/gmail|google-calendar|google-drive/*.md]
evals/fixtures/make_household.py make_household_gb.py make_statement.py make_everyday.py seed.sh
householdbot/                          wtyczka
  .claude-plugin/plugin.json icon.png   .mcp.json   README(.pl).md   PRIVACY(.pl).md   LICENSE
  hooks/hooks.json
  agents/deadline-watcher.md document-reader.md
  skills/<skill>/SKILL.md reference/*.md
  skills/<skill>/shared/               kopie generowane (rules.md, locale/, i18n/, scripts/, templates/)
```

Liczba plików wtyczki: 147 po Etapie 1.1, 307 po Etapie 2 (z testami
zachowania w środku), 184 po Etapie 2.1, gdy testy wyszły poza paczkę, 297 po
Etapie 3 i 382 po Etapie 4 (34 skille, dwa pakiety krajowe). Każdy kolejny
pakiet dodaje 54 pliki (po dwa w 27 skillach), więc do progu 512, powyżej
którego katalog wtyczek ocenia ręcznie, mieszczą się jeszcze dwa pakiety.

---

## 6. Strategia weryfikacji

| Poziom | Co sprawdza | Narzędzie | Kiedy |
|---|---|---|---|
| 1. Struktura | manifesty, frontmatter, samowystarczalność skilli, aktualność kopii, limity katalogu, uprawnienia agentów, kształt testów, pakiety krajowe, identyfikatory i sekrety w plikach | `scripts/validate.py`, `claude plugin validate --profile directory --strict` | po każdej zmianie, w CI |
| 2. Rachunek | święta, terminy, cofanie, pasma, cykliczność, rejestry, scalanie, archiwizacja | `python -m unittest` | po zmianie skryptu, w CI |
| 3. Zachowanie | wyzwalanie skilli, poprawność wyniku, zatrzymanie na bramce, odporność na wstrzyknięcie i oszustwa | `claude plugin eval` przez `scripts/eval.py` | w trakcie: pojedyncze przypadki; na zamknięciu etapu pełny przebieg |
| 3b. Sesje (od Etapu 5) | ścieżki wieloturowe ze skryptami: bramka zapisu, wstrzyknięcie, identyfikatory, daty, język; kontrola stanu folderu gospodarstwa i wzorców, bez sędziego modelowego | `scripts/session_test.py` przez wiersz poleceń gospodarza | po zmianie skryptu albo bramki; na zamknięciu etapu cały zestaw dwa razy |
| 4. Użycie | pełna ścieżka wieloturowa, realne dokumenty | sesja `claude -p` na danych syntetycznych, pilotaż | po każdym etapie |

Ograniczenia ustalone w Etapie 1 i stan po Etapie 4:

- Na Windows `claude plugin eval` nie przydziela powłoki (brak piaskownicy
  systemowej), więc testy zachowania sprawdzają tu wariant bez Pythona.
  Ścieżkę ze skryptami sprawdzają testy jednostkowe i sesja wieloturowa.
  Workflow `evals.yml` uruchamia testy z powłoką na Linuksie (bubblewrap i
  socat); działa po utworzeniu repozytorium i dodaniu sekretu z kluczem API.
- Przypadki z zapisem po zgodzie wymagają historii rozmowy
  (`context.history_file`). Format tego pliku nie jest opisany w dokumentacji
  (wiadomo tylko, że to JSONL), a transkrypt z sesji lokalnej zawiera ścieżki
  użytkownika, więc zapis po zgodzie nadal sprawdza sesja wieloturowa.
- Raporty testów zostają lokalnie (`--no-publish`), koszt ograniczony
  `--max-cost-usd`.

Dane testowe są wyłącznie syntetyczne; generator tworzy identyfikatory w
czasie uruchomienia, a walidator odrzuca identyfikatory z poprawną sumą
kontrolną w plikach repozytorium.

### Protokół zamknięcia etapu

1. Poziomy 1 i 2 zielone, poziom 3 powyżej progu, sesja wieloturowa i
   pilotaż bez błędów blokujących.
2. Ten plan zaktualizowany: wykonane, odstępstwa, wnioski.
3. CHANGELOG i numer wersji.
4. Pamięć projektu zaktualizowana.
5. Commit; brak pracy w toku.

---

## 7. Etapy

Cztery etapy, każdy jako jedna sesja; Etapy 2 i 3 są od siebie niezależne.
Etapy 5 i 6 zostały dodane 14.11.2026 i są zaplanowane, każdy jako jedna
sesja, z pilotażem pomiędzy nimi.

### Etap 1. Rdzeń: rekord, dokumenty, terminy (wersja 0.1) ✅

Wykonane 13.11.2026:

- **A. Fundament.** Nazwa `householdbot` w manifestach i ścieżkach, ikona,
  README, PRIVACY i LICENSE we wtyczce, dokumenty repozytorium, `.gitignore`,
  CI.
- **B. Rekord.** Rejestry JSON z `schema_version`, szablon profilu, opis pól,
  kopie rejestrów przy każdym zapisie, dziennik decyzji zapisywany przez skrypt.
- **C. Warstwa dowodowa.** `dates.py` (święta stałe i ruchome, Wigilia od
  2025, reguły liczenia z przesunięciem ustawowym, `do_by` liczone od
  nieprzesuniętego końca, pasma, cykliczność z kotwicą dnia, daty ustawowe z
  pakietu). `record.py` (locate, init, validate z wykrywaniem identyfikatorów,
  next-id, add z kopiowaniem oryginału i odciskiem pliku, update, complete z
  następnym wystąpieniem, due, find z odmianą polską, show, conflicts, diff,
  merge kopii konfliktowej, archive, migrate). 48 testów jednostkowych.
- **D. Reguły wspólne.** Siedem poprawionych i cztery nowe:
  `absent-is-not-zero`, `storage-scope`, `chain-seams`, `output-style`.
- **E. Pakiet PL.** Weryfikacja w źródłach urzędowych: patrz rozdział 8.
- **F. Skille.** Osiem skilli rdzenia, każdy z `reference/gotchas.md`.
- **G. Agenci.** `deadline-watcher`, `document-reader`.
- **H. Generator i walidator.** `scripts/sync.py`, `scripts/validate.py`.
- **I. Testy zachowania.** 24 przypadki (po 3 na skill) na syntetycznym
  gospodarstwie: rachunek z bramką, dwa SMS-y z dopłatą do paczki, pismo z
  wstrzykniętym poleceniem, termin przez święto, brak dokumentu, numer polisy,
  zmiana konta bankowego z maila, kopia konfliktowa, PESEL w rejestrze, pusty
  rejestr, brak rekordu.

Odstępstwa od planu: kopie w `skills/<skill>/shared/` zamiast
`references/shared/`; schemat w `record.py` zamiast plików `*.schema.json`;
generator nazywa się `scripts/sync.py`; testy w formacie jednego
`case.yaml`; doszło polecenie `merge` (scalanie kopii konfliktowych) i
wykrywanie identyfikatorów w rejestrach.

Wyniki: patrz rozdział 8.

Twój udział (pilotaż, około 30 minut):

1. W Claude Code: `/plugin marketplace add <ścieżka do tego repozytorium>`,
   potem `/plugin install householdbot@householdbot`.
2. `/householdbot:household-onboard`, szybka konfiguracja, folder poza
   repozytorium (najlepiej na dysku synchronizowanym).
3. Trzy własne dokumenty: rachunek, polisa lub umowa, pismo urzędowe.
4. „co mamy do zrobienia”, „przegląd tygodnia”.
5. Uwagi do mnie: co było źle policzone, niejasne albo zbędne.

Pilotaż obejmuje też język: konfiguracja zaczyna się od wyboru, a polecenie
„po polsku” ustawia polski w profilu.

### Etap 1.1. Dwujęzyczność i dwa punkty pakietu PL (wersja 0.1.1) ✅

Wykonane 13.11.2026 na prośbę z tego samego dnia („dwujęzyczność, angielski
domyślny, możliwość wyboru języka”; „wprowadź rekomendacje”, czyli dwa punkty
pakietu PL zostawione do sprawdzenia).

- **Języki** według D14: `core/i18n/en.json` i `pl.json`, `dates.py --lang`,
  język z profilu w `record.py` (dziennik, kwoty, daty, notatki), szablony
  `templates/en|pl/`, teksty konfiguracji w obu językach, reguła wyboru
  języka, cytaty z tłumaczeniem, pisma do urzędów w języku urzędu, polska
  odmiana liczebników (1 dzień, 2 dni, 5 tygodni).
- **Dokumenty dla użytkowników** w obu językach: README, QUICKSTART, README i
  PRIVACY wtyczki, z przełącznikiem w pierwszej linii.
- **Pakiet PL:** list sądowy doręczony w ostatnim dniu drugiego 7-dniowego
  okresu, zwykle 15 dni po pierwszym awizo (KPC art. 139 § 1, rozporządzenie
  Dz.U. 2024 poz. 19, SN IV CKN 1026/00, potwierdzone przykładami z SO
  Gliwice); pierwsze prawo jazdy kat. B wydane od 4.09.2026 ważne tylko na
  okres próbny (2 lata, 3 lata przy uzyskaniu w wieku 17 lat).
- **Poprawki z testów:** pole `transit_buffer_days` dla płatności, żeby
  następne wystąpienie rachunku zachowało dzień zapasu na przelew;
  wstrzymana prośba o zmianę konta nie trafia do rekordu nawet jako
  ostrzeżenie, a jej numer nie jest powtarzany; opisy skilli lepiej
  rozpoznają pytania o termin i o zmianę języka.
- **Walidator** sprawdza zgodność kluczy plików językowych, szablony dla
  każdego języka, teksty konfiguracji w obu językach i polskie odpowiedniki
  dokumentów z wzajemnymi odnośnikami.
- **Testy:** 65 jednostkowych (w tym zgodność z orzecznictwem dla listu
  sądowego), 31 przypadków zachowania (7 nowych dla języków).

### Etap 2. Pieniądze i korespondencja (wersja 0.2) ✅

Wykonane 13.11.2026:

- **A. Skille.** Dziewięć skilli i łańcuch `monthly-review`, każdy z
  `reference/gotchas.md` i wariantem bez Pythona: `inbox-triage`,
  `bills-due`, `contract-check`, `subscriptions-review`, `budget-snapshot`,
  `tax-season-organizer`, `reply-to-letter`, `complaint-and-claim`,
  `cancel-or-switch`. Router kieruje do nich prośby po polsku i po angielsku.
- **B. `statement.py`.** Eksport CSV z banku: kodowanie UTF-8 lub
  Windows-1250, dowolny separator, wiersze wstępne, polskie i angielskie
  nazwy kolumn, jedna kolumna kwoty albo osobne obciążenia i uznania.
  Maskowanie numerów kont, kart i PESEL; sumy w `Decimal` według miesięcy i
  kategorii; kontrola salda bieżącego; miesiące bez transakcji zgłaszane jako
  brak; płatności cykliczne z odpowiednikiem miesięcznym i rocznym oraz
  podwyżki powyżej 5%; reguły kategorii gospodarstwa zapisywane po zgodzie.
  Kategorie w `core/money/categories.json` z etykietami w obu językach.
- **C. `record.py` i `dates.py`.** `due --kind/--category` z sumami według
  walut; daty ustawowe na ostatni dzień miesiąca (`MM-L`); `window` podaje,
  co dotrzymuje terminu (`met_by`) i co oznacza brak odpowiedzi (`silence`),
  gdy pakiet to określa; `locate` uruchomione w folderze wtyczki zwraca
  wskazówkę, a każdy skill uruchamia je z folderu roboczego sesji.
- **D. Reguły wspólne.** `money` (lista płatności, dwie osobne zgody,
  końcówka konta do wpłat porównywana z poprzednim rachunkiem, sumy wyłącznie
  ze skryptu) i `voice` (pisma w języku adresata, ton formalny,
  identyfikatory jako pola do uzupełnienia, nic nie jest wysyłane). W regule
  językowej doszły polskie formy bez rodzaju gramatycznego, dopóki domownik
  sam nie pokaże swoich.
- **E. Pakiet PL.** Cztery sekcje zweryfikowane w tekstach jednolitych z ELI
  Sejmu na 13.11.2026: rozliczenie roczne PIT, reklamacje i roszczenia,
  wypowiedzenia (forma i doręczenie), płatności. 24 nowe okna terminów i 3
  obowiązki cykliczne, każde z podstawą prawną. Szczegóły w rozdziale 8.
- **F. Dane testowe.** `make_statement.py` z trzema układami eksportu
  (polski bank z preambułą w Windows-1250, kolumny obciążeń i uznań,
  angielski z tabulatorem) i wariantem z luką; atrapa skrzynki z ośmioma
  wątkami (rachunek, zmiana konta z domeny podobnej do dostawcy, fałszywa
  dopłata do paczki, kod jednorazowy, zgoda szkolna, odnowienie OC).
- **G. Testy.** 86 jednostkowych (w tym 12 dla wyciągów i 5 dla `locate`),
  62 przypadki zachowania (31 nowych).

Odstępstwa od planu: atrapy poczty leżą w folderach przypadków
(`mocks/gmail/`), każdy przypadek ma własny zestaw wątków; wyciągi w PDF są
poza zakresem, skill prosi o eksport CSV; rachunek zapisuje cztery ostatnie
cyfry konta do wpłat, co jest jedynym wyjątkiem od zasady „identyfikatory
tylko jako wskaźniki” i służy wykrywaniu zmiany konta.

Kryteria akceptacji i ich spełnienie:

- ścieżka rachunek, lista płatności, dwie osobne zgody: sesja wieloturowa
  (rozdział 8) i przypadki `bills-due`
- pismo urzędowe z terminem i arytmetyką, projekt niewysłany: przypadki
  `reply-to-letter`, w tym bramka szkicu w skrzynce
- wyciąg co do grosza, brak danych jako brak: testy jednostkowe dla trzech
  układów i przypadek `statement-gap`
- wypowiedzenie z formą i czasem doręczenia: sesja wieloturowa i przypadki
  `cancel-or-switch`

Wyniki: patrz rozdział 8.

Twój udział (pilotaż): eksport CSV z własnego banku dla `budget-snapshot` i
`subscriptions-review`, bieżące rachunki w `bills-due`, dwa realne pisma w
`reply-to-letter` albo `complaint-and-claim`.

### Etap 2.1. Testy zachowania poza paczką wtyczki (wersja 0.2.1) ✅

Wykonane 13.11.2026 według Twojej decyzji z tego dnia („testy zachowania poza
paczką wtyczki”).

- Testy przeniesione z `householdbot/evals/` do `evals/` w katalogu głównym
  repozytorium. Paczka wtyczki nie zawiera żadnego pliku testowego: 184 pliki
  zamiast 307.
- `claude plugin eval` przyjmuje katalog testów tylko wewnątrz wtyczki
  (`--eval-dir must stay inside the plugin root`), dlatego `scripts/eval.py`
  kopiuje wtyczkę i testy do `build/eval/householdbot/` i uruchamia polecenie
  na kopii. Argumenty przechodzą bez zmian, wyniki trafiają do
  `evals/results/`. `build/` i `evals/results/` są w `.gitignore`.
- Walidator sprawdza testy w nowym miejscu i zgłasza błąd, gdy
  `householdbot/evals/` pojawi się ponownie. Testy jednostkowe biorą dane
  syntetyczne z `evals/fixtures/`.
- Sprawdzone: walidatory i 86 testów jednostkowych zielone, przypadek
  `household-router-parcel-scam` uruchomiony przez `scripts/eval.py` przechodzi
  (0,05 USD).

### Etap 3. Dom, rodzina i codzienność (wersja 0.3) ✅

Wykonane 13.11.2026 na polecenie „ruszaj dalej, pilotaż później”:

- **A. Skille.** Jedenaście skilli i dwa łańcuchy z rozdziału 4, każdy z
  `reference/gotchas.md` i wariantem bez Pythona. Pięć skilli
  administracyjnych (`home-upkeep`, `vehicle-file`, `insurance-overview`,
  `identity-and-travel`, `school-desk`) napisał agent według specyfikacji,
  po przeglądzie i poprawkach.
- **B. Warstwa dowodowa.** `chores.py` (rejestr obowiązków, plan według
  udziału i minimalnego wieku z wyrównaniem obciążenia z 8 zapisanych
  tygodni, zapis planu po zgodzie, zamiany uzgodnione między domownikami,
  bilans). `dates.py event` liczy wszystkie terminy ustawowe zdarzenia
  życiowego od dnia, w którym się wydarzyło; `dates.py events` je wymienia.
  `record.py retention` pokazuje dokumenty po terminie przechowywania i
  niczego nie zmienia; nowy status dokumentu `disposed`; `complete
  --from-done` liczy następny przegląd od dnia wykonania; `find` bez słów
  wymienia wszystkie wpisy danego typu.
- **C. Reguły.** Nowa reguła `everyday` (posiłki, zakupy, obowiązki,
  kalendarz); w regule danych osobowych produkty pomijane w jadłospisie i
  plik awaryjny; w bramkach zgody: zmiany dyktowane na listach, wpisy w
  kalendarzu jako zapis zewnętrzny, plany jako propozycje.
- **D. Profil i konfiguracja.** Opcjonalna sekcja *Codzienność* w obu
  szablonach, piąta część wywiadu (opcjonalna), opis `chores.json` i
  `lists/` w przewodniku po rejestrach.
- **E. Pakiet PL.** Dwie części zweryfikowane 13.11.2026 w tekstach jednolitych i
  ujednoliconych z ELI Sejmu, z nowelizacjami w mocy na ten dzień. *Life
  events*: kupno i sprzedaż samochodu, przeprowadzka, narodziny dziecka, zmiana
  pracy, śmierć bliskiej osoby (29 okien terminów, 6 zdarzeń, 32 kroki bez
  terminu ustawowego). *Health papers*, *Children and school*, *Keeping and
  shredding documents*, *Insurance a household must or may have*, *Home
  upkeep, further rules*, *Travel documents* (21 okien, 5 obowiązków
  cyklicznych, 12 okresów przechowywania z podstawą prawną albo oznaczeniem
  „sugerowany”). Odzwierciedlone zmiany z lat 2025–2026: zasiłek pogrzebowy
  7000 zł od 1.01.2026, 60 dni na rejestrację odziedziczonego pojazdu od
  24.12.2025, zwolnienie z PCC do 3000 zł od 3.11.2026, przywrócenie terminu
  SD-Z2 od 7.01.2026, centralna e-rejestracja od 1.01.2026, e-skierowania do
  sanatorium od 1.07.2025, czujki dymu i czadu (Dz.U. 2024 poz. 1716). 16
  nowych punktów nierozstrzygniętych (razem 20) opisanych bez twierdzenia i
  wypisanych w `PL.json` (`sources.uncertain`).
- **F. Dane testowe.** `make_everyday.py` (tryb `everyday`): sekcja
  *Codzienność* z jednym produktem pomijanym bez powodu, rejestr obowiązków z
  zapisanym tygodniem, listy, pralka z gwarancją, polisa domu, skierowanie
  dziecka, pismo ze szkoły, dowód osobisty bliski wygaśnięcia, rachunek po
  terminie przechowywania; atrapa kalendarza Google z kolizją.
- **G. Testy.** 107 jednostkowych (w tym 14 dla `chores.py`), 101 przypadków
  zachowania (39 nowych: 24 napisane przeze mnie, 15 zaproponowanych przez
  agenta i dopracowanych), sesja wieloturowa ze skryptami.

Odstępstwa od planu: skrypt do sumowania list zakupów nie powstał, bo
sumowanie ilości jest proste i pokazywane w odpowiedzi; imieniny nie mają
własnej bazy danych, gospodarstwo podaje daty do zapamiętania w profilu;
`scripts/eval.py --stage` pozwala uruchamiać przypadki równolegle.

Kryteria akceptacji i ich spełnienie:

- zdarzenie życiowe tworzy zobowiązania z datami i podstawą prawną:
  `dates.py event` i przypadki `life-event`, sesja wieloturowa (kupno auta)
- dane o zdrowiu i alergiach poza przeglądem i wpisem kalendarza: przypadki
  `family-calendar-neutral-title`, `health-file-neutral-register`,
  `school-desk-no-health-in-calendar`, `meal-planner-week-plan`; reguła
  danych osobowych
- `emergency-file` bez identyfikatora i hasła: przypadki
  `emergency-file-pin-refused` (z regułami wykluczającymi PIN i hasło) i
  `emergency-file-draft`
- rotacja obowiązków deterministyczna i równa: testy jednostkowe
  `test_chores.py`
- przegląd roczny proponuje usunięcia według okresów przechowywania i niczego
  nie usuwa: `record.py retention` (test), przypadki `annual-review`

Twój udział (pilotaż, razem z Etapami 1 i 2): jedno zdarzenie życiowe,
jadłospis z listą zakupów, przegląd polis.

### Etap 4. Zasięg, utwardzenie, publikacja (wersja 1.0.0-rc.1) ✅

Wykonane 14.11.2026 na polecenie „dalej” (po Etapie 3, z pilotażem
przesuniętym na później). Publikacja i pilotaż należą do Ciebie, dlatego
wersja to kandydat do wydania 1.0.

- **A. Skille.** `household-dashboard` (jedna strona o całym gospodarstwie:
  terminy według pasm, płatności miesiąca z sumami według walut, dokumenty z
  datą ważności, polisy, zdrowie i szkoła pod neutralnymi tytułami,
  codzienność, stan rekordu i wiersz „nie śledzimy” dla każdej luki; zapis w
  `reviews/` jako Markdown albo samodzielna strona HTML dopiero po zgodzie),
  `build-skill` (powtarzalna czynność gospodarstwa jako jego własny skill z
  regułami domu; zapis po zgodzie, bez nadpisywania istniejącego skilla) i
  `pack-builder` (własny pakiet krajowy ze źródeł urzędowych, sprawdzany przez
  `dates.py check-pack`, zapisywany w `packs/` rekordu). Trzy skille napisał
  agent według specyfikacji, po przeglądzie i poprawkach. Razem 34 skille.
- **B. Pakiet GB (Anglia i Walia).** Research w trzech równoległych częściach
  (kalendarz, terminy i podatki; prawa konsumenta, umowy, najem i oszustwa;
  zdarzenia życiowe, dokumenty, zdrowie i szkoła), każda reguła z aktem,
  przepisem i źródłem urzędowym. Potem osobny agent sprawdził w tekstach
  źródłowych około 40 najważniejszych twierdzeń i znalazł 4 błędy, wszystkie
  poprawione: przesuwanie terminu z weekendu przy rejestracji urodzenia i
  zgonu oraz przy wnioskach o świadczenia (przepisy go nie przewidują), dwie
  nieaktualne podstawy prawne przy zasiłku na dziecko i doręczenie sądowe
  liczone w dniach kalendarzowych zamiast roboczych (silnik dostał doręczenie
  w dniach roboczych i przesunięcie na następny dzień roboczy). Zawartość: święta bankowe z
  dniami zastępczymi, przeniesionymi i jednorazowymi, zgodne z oficjalną listą
  gov.uk dla lat 2019–2028 (test jednostkowy); 5 reguł liczenia, 10 reguł
  doręczenia, 92 okna terminów, 17 dat corocznych, 20 okresów przechowywania,
  6 zdarzeń życiowych; 46 punktów nierozstrzygniętych w `sources.uncertain`.
  Konfiguracja pyta gospodarstwo z Wielkiej Brytanii o część kraju; Szkocja i
  Irlandia Północna zaczynają bez pakietu.
- **C. Silnik dat.** Reguły świąt typu „pierwszy poniedziałek maja” i
  „ostatni poniedziałek sierpnia”, dni zastępcze, przeniesione i jednorazowe;
  terminy liczone od dnia zdarzenia włącznie („beginning with”:
  `start_inclusive`, `deadline --inclusive`); doręczenie liczone w dniach
  roboczych z przesunięciem na następny dzień roboczy; polecenie `check-pack`,
  z którego korzysta też walidator repozytorium; polecenie `windows`, które
  znajduje okno terminu w pakiecie po słowach; kwoty po angielsku z symbolem
  waluty (`£142.60`).
- **D. Pakiety własne i zasięg.** Pakiet gospodarstwa w `packs/` rekordu,
  oznaczony `household pack — verify`; pakiet dołączony do wtyczki ma zawsze
  pierwszeństwo; każdy pakiet podaje część kraju, którą obejmuje.
- **E. Wariant bezobsługowy.** `managed-agent-cookbooks/deadline-watcher` dla
  Claude Managed Agents, według aktualnej dokumentacji API: koordynator bez
  narzędzi, czytelnik rejestru z narzędziami odczytu, kalkulator uruchamiający
  skrypty wtyczki w piaskownicy bez sieci, pisarz raportu jako jedyny z prawem
  zapisu; cotygodniowe wdrożenie zaplanowane, budżet 3 USD na sesję. Przesyłany
  jest tylko wyciąg z profilu i otwarte zobowiązania, nigdy oryginały.
  Sprawdzenie offline (`cookbook.py check`, `--dry-run`, test jednostkowy) w
  walidatorze i w CI; prompt koordynatora jest kopią agenta wtyczki z dopiskiem
  dla trybu bez nadzoru i `check` wykrywa rozjazd. Napisał agent, po przeglądzie.
- **F. Przegląd bezpieczeństwa** przez osobnego agenta, z demonstracjami na
  danych syntetycznych: 7 ustaleń (1 wysokie, 3 średnie, 3 niskie), wszystkie
  poprawione. Tekst z dokumentów nie trafia już do wiersza poleceń (wcześniej
  `$(...)` w nazwie nadawcy, załącznika lub płatnika mógł się wykonać);
  `deadline-watcher` ma tylko narzędzia odczytu; `merge` przyjmuje wyłącznie
  kopie konfliktowe z listy, pokazuje każde zmienione pole i sprawdza wpisy;
  workflow wydania buduje z tokenem tylko do odczytu i przypiętymi
  narzędziami; dziennik decyzji zapisuje jedną bezpieczną linię na zmianę;
  zapisy odrzucają ścieżkę wyprowadzającą poza folder gospodarstwa; zapis
  odrzuca identyfikatory (IBAN dowolnego kraju, brytyjski sort code z numerem
  konta, numer NI, NIP, numer karty, PIN i hasło), a wyciągi je maskują.
  16 nowych testów jednostkowych.
- **G. Powierzchnie.** Macierz D6 ustalona na podstawie dokumentacji Claude
  Code i Claude (agent claude-code-guide, z adresami stron): Cowork instaluje
  wtyczkę z marketplace albo z pliku `.plugin` i ma zadania zaplanowane,
  które korzystają z wtyczek; claude.ai przyjmuje skille wtyczki albo
  pojedyncze skille z zipów i uruchamia skrypty w piaskownicy kodu; telefon
  nie instaluje wtyczek. Nowy przypadek testowy sprawdza rekord trzymany za
  konektorem Dysku Google, jak w czacie na claude.ai.
- **H. Wydanie.** `scripts/package.py` buduje `householdbot.plugin` i zip
  każdego skilla (bez pola `argument-hint`, którego claude.ai nie przyjmuje),
  powtarzalnie co do bajtu; `release.yml` buduje paczki z tagu i publikuje je
  w osobnym zadaniu; `evals.yml` uruchamia testy zachowania z powłoką na
  Linuksie na żądanie.
- **I. Dokumentacja.** `docs/architecture.md` (analiza wzorca),
  `docs/country-packs.md`, QUICKSTART o każdej powierzchni i przeglądzie
  tygodnia według harmonogramu, `CONNECTORS.pl.md`, README obu poziomów, plan
  po angielsku jako wersja domyślna i jego polskie tłumaczenie.
- **J. Testy.** 149 testów jednostkowych (42 nowe), 115 przypadków
  zachowania (14 nowych, w tym 5 dla gospodarstwa w Anglii), pełny przebieg z
  porównaniem bez wtyczki i sesja wieloturowa ze skryptami (wyniki w
  rozdziale 8). Paczka ma 382 pliki z 512, co zostawia miejsce na dwa kolejne
  pakiety krajowe.

Odstępstwa od planu: testy zachowania z powłoką i z historią rozmowy nie
zostały uruchomione, bo workflow na Linuksie czeka na repozytorium i klucz API,
a format `history_file` nie jest udokumentowany; zapis po zgodzie nadal
sprawdza sesja wieloturowa. Testy w Cowork i na telefonie, publikacja i
zgłoszenie do katalogu oraz pilotaż należą do Ciebie. Poprawki z pilotażu
wejdą do wersji 1.0.

Kryteria akceptacji z rozdziału 1: (1) pełna ścieżka bez pomocy autora:
pilotaż; (2) każdy obszar ma skill z przypadkami testowymi: spełnione; (3)
daty i kwoty ze skryptów tam, gdzie można je uruchomić: spełnione; (4) nic bez
zgody, potwierdzone testami: spełnione; (5) `claude plugin validate --profile
directory --strict`, walidator i lista kontrolna katalogu: spełnione; (6)
pilotaż: po Twojej stronie.

Twój udział:

1. Pilotaż Etapów 1–4 na prawdziwym, prywatnym folderze poza repozytorium (lista
   z Etapów 1–3 oraz pulpit i jeden pakiet sprawdzony przez `pack-builder`).
2. Cowork: wgranie `householdbot.plugin` (Add > Upload plugin) i jedno zadanie
   zaplanowane „przegląd tygodnia”. Telefon: Remote Control do sesji z wtyczką.
3. Zgoda na publikację. Po niej: publiczne repozytorium `householdbot` na
   koncie dithiothreitol, push gałęzi `main`, tag `v1.0.0-rc.1` (CI zbuduje
   wydanie), sekret `ANTHROPIC_API_KEY` z kluczem z limitem wydatków dla
   testów z powłoką, zgłoszenie w https://claude.ai/directory/manage
   (Submit new > Plugin bundle).

**Publikacja (14.11.2026, po zgodzie).** Publiczne repozytorium
https://github.com/dithiothreitol/householdbot z dwujęzycznym README
napisanym jako strona docelowa (słowa kluczowe w tytule i opisie, 20 tematów
GitHuba, odznaki, FAQ), szablonami zgłoszeń z wymogiem danych syntetycznych,
poufnym zgłaszaniem podatności i wydaniem v1.0.0-rc.1 zbudowanym przez CI
(paczka wtyczki, suma kontrolna, 34 zipy skilli, notatki po angielsku i po
polsku). CI na GitHubie przechodzi; obraz Ubuntu 26.04 nie ma już Pythona 3.9,
więc kontrola najstarszej wersji używa 3.10. Instalacja z publicznego
marketplace sprawdzona w odizolowanej konfiguracji.

**Wersja 1.0.0-rc.2 (ten sam dzień): Codex i ChatGPT.** Codex przyjmuje
wtyczki w formacie Claude, a OpenAI zaleca dla nowych paczek przenośny
manifest `plugin.json` (format Agent Plugins z rozszerzeniem
`extensions.com.openai`). Wtyczka ma teraz oba manifesty i oba pliki
marketplace (`.claude-plugin/` i `.agents/plugins/`), które walidator trzyma
w zgodzie. Codex CLI 0.153 instaluje ją poleceniami
`codex plugin marketplace add dithiothreitol/householdbot` i
`codex plugin add householdbot@householdbot` i pokazuje modelowi wszystkie 34
skille jako `householdbot:<skill>` (sprawdzone przez
`codex debug prompt-input` na odizolowanej konfiguracji, bez uruchamiania
modelu). Zostały: sesja w Codexie na danych syntetycznych, sekret
`ANTHROPIC_API_KEY`, zgłoszenia do katalogów Claude i OpenAI, pilotaż.

### Etap 5. Gwarancje w kodzie, poprawki, przypomnienia (wersja 1.0.0-rc.3, wykonany)

Zaplanowany 14.11.2026 na podstawie dwóch źródeł. Pierwszym jest sześcioturowa
sesja użycia na opublikowanej wersji rc.2 (polskie gospodarstwo, skrypty
dozwolone, 0,81 USD), która ujawniła usterki niewidoczne dla 115 przypadków
zachowania, ponieważ na Windows działają one bez powłoki. Drugim jest
porównanie z ogólnymi platformami agentów (Grok Bot, OpenBot), których agenci
działają bez pytania: na ich tle bramka zapisu tej wtyczki opiera się na samym
modelu, ponieważ `--approved-by` wpisuje model, a `hooks/hooks.json` jest
pusty.

Cel: obietnice z rozdziału 1 obowiązują dlatego, że egzekwują je skrypty,
niezależnie od modelu, który prowadzi skille; usterki są poprawione;
przypomnienia docierają na telefon bez konektora; pilotaż ma protokół. Jedna
sesja. Przed jej rozpoczęciem nic nie jest potrzebne z Twojej strony.

- **A. Poprawki z sesji użycia.**
  1. *„Po terminie” oznacza miniony ostatni dzień.* `record.py due` wyznacza
     pasmo z daty planu (`do_by`), więc płatność z minioną datą planu i
     ostatnim dniem w przyszłości występuje jako zaległa (rata podatku od
     nieruchomości z terminem w niedzielę 15.11.2026). Zmiana: pasmo
     `overdue` tylko wtedy, gdy `due_date` jest przed dniem dzisiejszym (dla
     wpisu bez `due_date`, gdy przed nim jest `do_by`); gdy minęła sama data
     planu, pasmo `now` z flagą `plan_passed: true`. Liczniki i sumy stosują
     tę samą regułę. `weekly-brief`, `household-dashboard`,
     `deadline-tracker`, `bills-due` i `household-router` wypisują pasmo ze
     skryptu, dodają „data planu minęła” na podstawie flagi i nie zmieniają
     nazwy pasma.
  2. *Ostatni dzień w dniu wolnym.* Wpis może wskazać regułę liczenia z
     pakietu (nowe pole opcjonalne `rule`; dotychczasowe wpisy pozostają
     poprawne, a `migrate` niczego do nich nie dopisuje). Dla takiego wpisu
     `due` zwraca `due_effective`, czyli zapisany ostatni dzień przesunięty
     według tej reguły, z notatką `moved_forward`. Daty ustawowe z
     `dates.py recurring` niosą regułę, a gospodarstwo testowe powstaje z
     nich.
  3. *Etykiety pochodzenia w języku gospodarstwa.* `core/i18n/<lang>.json`
     dostaje `tags` dla sześciu wartości (po polsku: „z dokumentu”, „podane
     przez domownika”, „wyliczone z dokumentu”, „reguła z pakietu krajowego,
     do sprawdzenia”, „pakiet gospodarstwa, do sprawdzenia”, „wyliczenie
     modelu, do sprawdzenia”). Skrypty zwracają `provenance_local` obok
     `provenance`; `core/rules/output-style.md` nakazuje wypisywać postać
     lokalną; rejestry zachowują wartości angielskie. Polskie przypadki
     zachowania, które oceniają słowo „verify”, przyjmują polską etykietę.
  4. *Notatki skryptów w jednym języku.* Łącznik w `due_note` (dziś „… with
     Kodeks cywilny …” w polskiej notatce) oraz stałe części `met_by` i
     `counted_from` pochodzą z i18n. Tekst pakietu, który istnieje tylko po
     angielsku (`title`, wolne notatki), wraca z polem `text_lang: "en"`, a
     reguła językowa nakazuje go w polskiej odpowiedzi tłumaczyć, a nie
     cytować.
  5. *Tabela przeglądu tygodnia.* Dwie kolumny, „zaplanuj do” i „ostatni
     dzień”, tak jak na pulpicie; bez jednej daty z dopiskiem w nawiasie
     (przegląd nazwał bezpieczną datę wypowiedzenia internetu, czw. 19.11,
     „ostatnim dniem”, podczas gdy ostatnim dniem był wt. 24.11).
  6. *Tytuły w języku gospodarstwa (D14).* `make_household.py --lang pl`
     zapisuje polskie tytuły (model przeniósł angielskie tytuły gospodarstwa
     testowego do nowego wpisu); `file-document` i `deadline-tracker` mówią
     jednym zdaniem, że tytuł powstaje w języku gospodarstwa.

- **B. Bramka zapisu w kodzie.**
  1. *Dwie fazy w `record.py`, `chores.py` i `statement.py`.* Polecenie
     zapisu bez `--confirm` tworzy wyłącznie podgląd: sprawdza zmianę,
     zapisuje dokładnie tę zmianę w `registers/.pending/<token>.json` i
     zwraca wiersze podglądu w języku gospodarstwa oraz żeton `confirm`
     wyliczony ze zmiany i stanu rejestru. `commit --confirm ŻETON
     --approved-by IMIĘ` wykonuje zapisaną zmianę i nic poza nią. Odmawia,
     gdy żeton jest nieznany, starszy niż 30 minut albo rejestr zmienił się
     od podglądu. Zapis jednym wywołaniem przestaje istnieć. Tekst z
     dokumentów trafia na standardowe wejście wyłącznie przy podglądzie.
  2. *Pliki obok rejestrów.* `record.py save` zapisuje plik w `reviews/`,
     `briefs/`, `drafts/` albo `exports/` w tych samych dwóch fazach i sam
     dopisuje linię dziennika. Skille przestają zapisywać te pliki
     narzędziem zapisu gospodarza i przestają dopisywać do
     `log/decisions.md` (dziś linię o zapisie pulpitu wpisuje model).
  3. *Czego dowodzi żeton.* Dowodzi, że zapis jest równy podglądowi, który
     powstał. Nie dowodzi, że podgląd przeczytał człowiek; to dodaje hook.
  4. *Hook.* `hooks/hooks.json` dostaje wpis `PreToolUse` dla poleceń
     powłoki zawierających `commit --confirm` trzech skryptów oraz dla
     narzędzi zapisu gospodarza w folderze gospodarstwa. Mały skrypt w
     Pythonie (interpreter wyszukiwany tak jak w `seed.sh`) odpowiada `ask`
     z pierwszym wierszem podglądu jako powodem, dzięki czemu domownik
     potwierdza w oknie samego gospodarza także w trybie, który sam
     przyjmuje edycje. Pokrycie: Claude Code i Cowork mają żeton i hook;
     claude.ai ma żeton (hooki są tam pomijane); Codex ma żeton i własny
     tryb zatwierdzania, opisany w QUICKSTART.
  5. *Skille i reguły.* Skille, które zapisują (dziś 15), oraz
     `core/rules/approval-gates.md` przechodzą na kolejność: podgląd, „tak”,
     commit. `scripts/validate.py` odrzuca tekst skilla z poleceniem zapisu
     w dawnej postaci jednego wywołania. Agenci pozostają bez powłoki albo
     tylko do odczytu, a `cookbook.py check` przechodzi.
  6. *Testy jednostkowe.* Żeton nieznany, przeterminowany i użyty ponownie;
     rejestr zmieniony między podglądem a zapisem; commit zapisuje zmianę z
     podglądu co do bajtu; ścieżka poza folder gospodarstwa nadal odrzucana;
     folder `.pending` nigdy nie zawiera identyfikatora, który zapis by
     odrzucił.

- **C. Przypomnienia bez konektora.** `record.py export --ics [--days N]
  [--member IMIĘ]` buduje `exports/householdbot.ics` przez `record.py save`:
  jedno wydarzenie całodniowe na otwarte zobowiązanie w dniu daty planu,
  ostatni dzień i etykieta pochodzenia w opisie, alarm z `lead_time_days`,
  stały `UID` zobowiązania, dzięki czemu ponowny import aktualizuje wpisy
  bez duplikatów, a zobowiązania zamknięte w ostatnich 30 dniach trafiają do
  pliku jako odwołane. Tytuły stosują reguły pulpitu: neutralne dla zdrowia,
  bez spraw przeznaczonych dla dorosłych, chyba że `--member` wskazuje
  dorosłego, bez identyfikatorów. RFC 5545: końce wierszy CRLF (jedyny
  wyjątek od reguły LF w repozytorium), łamanie po 75 oktetach, znaki
  specjalne. `deadline-tracker` i `family-calendar` proponują eksport, gdy
  kalendarz nie jest podłączony; QUICKSTART dostaje część „Przypomnienia w
  telefonie”. Testy jednostkowe: łamanie i znaki specjalne, stałe UID,
  neutralne tytuły, wpisy odwołane.

- **D. Testy sesyjne (poziom weryfikacji 3b).** `scripts/session_test.py`
  uruchamia sesje wieloturowe z `evals/sessions/<nazwa>.yaml` przez wiersz
  poleceń gospodarza na syntetycznym gospodarstwie, z powłoką. Kontrole są
  deterministyczne: wzorce dla każdej odpowiedzi i stan folderu gospodarstwa
  po każdej turze (niezmieniony skrót rejestru, wpis z podanymi polami,
  liczba linii dziennika, obecność albo brak pliku). Bez sędziego
  modelowego. Gospodarz jest adapterem: w tym etapie `claude -p --plugin-dir
  … --resume`, kolejne w Etapie 6. Limit kosztu na przebieg; raporty trafiają
  do `evals/results/sessions/` (poza commitami). Zestaw krytyczny, około 18
  sesji w czterech grupach:
  - *bramka*: dokument zapisany po „tak”; zgoda udzielona z góry; „zmień” to
    jeszcze nie zgoda; „nie” niczego nie zapisuje; rachunek zamknięty i jego
    następne wystąpienie;
  - *bezpieczeństwo*: polecenie ukryte w dokumencie; `$(...)` w nazwie
    nadawcy (plik-znacznik nie może powstać); identyfikator w dokumencie
    (nieobecny w rejestrach, dzienniku i odpowiedziach); pulpit na lodówkę
    bez sprawy sądowej oraz bez skryptów i linków w HTML; numery kont
    zamaskowane w wyciągu;
  - *daty*: sprzeciw od nakazu zapłaty (26.11, plan 23.11, przywołany
    artykuł); termin wypadający w Wigilię (28.12, plan 23.12); potwierdzenie
    doręczenia pozwu w Anglii w okresie świątecznym; ostatni dzień w
    niedzielę przy minionej dacie planu; eksport `.ics`;
  - *język*: polskie etykiety i tytuły; gospodarstwo anglojęzyczne w Polsce;
    dwie kolumny przeglądu tygodnia.
  Rozdział 6 dostaje ten poziom i jego miejsce w protokole zamknięcia.

- **E. Przegląd pakietów po stronie repozytorium.** `scripts/pack_review.py`
  zgłasza każdy pakiet, którego data `reviewed` jest starsza niż sześć
  miesięcy, oraz liczbę punktów w `sources.uncertain`. Workflow
  `pack-review.yml` uruchamia go pierwszego dnia miesiąca i otwiera albo
  aktualizuje jedno zgłoszenie na pakiet (przypięte akcje, wyłącznie
  `issues: write`). `docs/country-packs.md` dostaje procedurę przeglądu:
  źródła do otwarcia, co uruchomić ponownie (`check-pack`, testy
  jednostkowe pakietu), sposób zapisania daty i osoby przeglądającej.

- **F. Protokół pilotażu.** `docs/pilot.md` i `docs/pilot.pl.md`:
  przygotowanie (prywatny folder poza repozytorium, wersja rc.3, kopia
  folderu); dwanaście scenariuszy z Etapów 1–5 (konfiguracja, trzy zapisane
  dokumenty, lista terminów, pismo urzędowe z terminem, wyciąg bankowy,
  szkic wypowiedzenia, przegląd tygodnia, pulpit, plik `.ics` w telefonie,
  jedno zdarzenie życiowe, Cowork z zaplanowanym przeglądem, Remote Control
  z telefonu); mierniki (zapisy bez zgody: 0; błędne daty: 0, przy czym
  każda wyliczona data jest porównana z `dates.py` albo ze źródłem; minuty
  do pierwszego przeglądu tygodnia; liczba poprawek wyniku modelu na
  scenariusz); błędy blokujące i nieblokujące; szablon notatek, który
  przyjmuje wyłącznie opis własnymi słowami, nigdy prawdziwe dane; warunek
  zakończenia, czyli warunki 1 i 6 z rozdziału 1.

- **G. Dokumenty i wydanie.** README i QUICKSTART (bramka w trzech krokach,
  przypomnienia), PRIVACY (folder `.pending`, kto widzi plik `.ics`),
  SECURITY (czego dowodzi bramka i co pozostawia gospodarzowi),
  `docs/architecture.md` (wniosek: gwarancja przeniesiona z promptu do
  skryptu), CHANGELOG, dwujęzyczne notatki wydania, oba manifesty w wersji
  1.0.0-rc.3, ten plan w obu językach, pamięć projektu, commit. Push, tag i
  wydanie po Twoim „tak”.

Akceptacja:

1. Testy jednostkowe zielone razem z nowymi; `scripts/validate.py` 0 błędów
   i 0 ostrzeżeń; `claude plugin validate ./householdbot --profile directory
   --strict`; `scripts/package.py --skills` buduje paczkę poniżej 450 plików.
2. Zestaw sesyjny: każda sesja z grup „bramka” i „bezpieczeństwo” przechodzi
   w dwóch przebiegach z rzędu; grupy „daty” i „język” przechodzą w co
   najmniej 90%.
3. Testy zachowania (Windows, bez powłoki): przypadki każdego zmienionego
   skilla powtórzone; pełny przebieg na zamknięciu z wynikiem co najmniej
   100 na 115, bez porażki w przypadkach bramki.
4. Zapis jednym wywołaniem jest niemożliwy, co pokazują testy jednostkowe i
   `scripts/validate.py`.

Koszt wywołań modelu: zestaw sesyjny około 5 USD na przebieg (około 15 USD
z iteracjami), powtórki zmienionych skilli około 6 USD, pełny przebieg na
zamknięciu około 17 USD; limit 40 USD.

Twój udział po etapie: pilotaż według `docs/pilot.md` na wersji rc.4; „tak”
dla pushu, tagu i wydania; opcjonalnie sekret `ANTHROPIC_API_KEY`, dzięki
któremu `evals.yml` uruchomi 115 przypadków z powłoką na Linuksie.

**Wykonane 14.11.2026** (w tej samej sesji co plan, po „tak”). Zgodnie z
Twoim poleceniem z tego samego dnia nie uruchomiłem niczego, co wywołuje
model: żadnego testu sesyjnego, testu zachowania, przebiegu w Codexie ani
subagenta. Wszystko poniżej sprawdzają testy jednostkowe, walidatory i
kontrole offline.

- **A.** Pasma liczone od ostatniego dnia, z `plan_passed` i `plan_note`;
  opcjonalne pole `rule` i `last_day` w `record.py due`; `rule` przy każdej
  dacie ustawowej z `dates.py recurring`; `tags` w i18n oraz
  `provenance_local` w `due`, `window`, `event`, `deemed` i `recurring`.
  Angielski łącznik w polskiej notatce pochodził z pól `law` samego pakietu,
  a nie z szablonu: 73 podstawy prawne pakietu PL brzmią teraz po polsku
  („i”, „w zw. z”, nazwy rozporządzeń), test jednostkowy tego pilnuje, a
  tekst pakietu, który istnieje tylko po angielsku, ma znacznik
  `text_lang: "en"`. Dwie kolumny dat w przeglądzie tygodnia i na liście
  terminów; polskie tytuły i notatki w polskim gospodarstwie testowym, którego
  rata podatku wskazuje regułę `tax`.
- **B.** Dwie fazy we wszystkich trzech skryptach przez jeden obiekt
  `Change` w `record.py` (`chores.py` i `statement.py` z niego korzystają i
  dostały `commit`); `init --profile-file -` tworzy cały rekord jedną zmianą;
  `save` dla plików; hook (`hooks/gate.sh` znajduje Pythona, `hooks/gate.py`
  decyduje) w formie powłoki z `"onFailure": "continue"`; 26 skilli i reguły
  przepisane na kolejność podgląd, „tak”, commit; `scripts/validate.py`
  odrzuca zapis jednym wywołaniem i sprawdza hook. Dodane po drodze: kilka
  wpisów jednego rejestru w jednym podglądzie (`add` przyjmuje listę JSON,
  `complete` przyjmuje `--id` wiele razy), ponieważ drugi podgląd tego
  samego rejestru staje się nieaktualny po commicie pierwszego; plan
  obowiązków zachowuje zatwierdzającego dzięki znacznikowi, który `commit`
  zastępuje imieniem.
- **C.** `record.py export --ics` zgodnie z planem.
- **D.** `scripts/session_test.py` i 18 sesji. Sesje są w JSON, a nie w
  YAML, dzięki czemu program korzysta tylko z biblioteki standardowej;
  `--check` zakłada każde gospodarstwo i rozwiązuje każdą wartość bez
  modelu; identyfikatory w sesjach bezpieczeństwa powstają w trakcie
  przebiegu.
- **E.** `scripts/pack_review.py` i `pack-review.yml` (akcje przypięte do
  wersji, tak jak w pozostałych workflowach); procedura w
  `docs/country-packs.md`.
- **F.** `docs/pilot.md` i `docs/pilot.pl.md`.
- **G.** README, QUICKSTART, README wtyczki i PRIVACY w obu językach,
  SECURITY, `docs/architecture.md` (wnioski 23 i 24), CHANGELOG, dwujęzyczne
  notatki wydania, oba manifesty w wersji 1.0.0-rc.3.

Akceptacja: (1) spełniona: 198 testów jednostkowych zielonych (49 nowych),
`scripts/validate.py` 0 błędów i 0 ostrzeżeń, `claude plugin validate
--strict` przechodzi dla wtyczki i marketplace, `scripts/package.py --skills`
buduje 385 plików razem z hookiem; (2) i (3) czekają na płatne przebiegi;
(4) spełniona.

Czeka na Twoje „tak”: płatna weryfikacja (zestaw sesyjny dwa razy, około
10 USD; testy zachowania zmienionych skilli, około 6 USD; pełny przebieg,
około 17 USD), potem push, tag i wydanie rc.3, a następnie pilotaż.

**Wydanie i rc.4, 14.11.2026.** Po Twoim „tak” wersja rc.3 została
wypchnięta, otagowana i wydana (36 plików), bez płatnej weryfikacji.
Pięcioturowa sesja na rc.3 do materiałów na LinkedIn i X (1,03 USD, za
zgodą) pokazała to, czego nie wykryły kontrole bez modelu: `record.py save`
odrzucał `<meta charset>`, którego wymaga szablon strony przeglądu, więc
model usuwał znacznik i zapisywał polskie litery jako kody HTML;
`chores.py --help` i `statement.py --help` nadal pokazywały zapis jednym
wywołaniem, a pierwszy taki zapis modelu skrypt zgodnie z założeniem
odrzucił; po „zmień … i zapisz” model utworzył nowy podgląd i zatwierdził
go jednym poleceniem, w turze podglądu. Wersja 1.0.0-rc.4 usuwa dwie
pierwsze usterki w kodzie (strona może deklarować kodowanie i viewport,
każdy inny `<meta>` jest odrzucany; pomoc każdego polecenia zapisu uczy
dwóch kroków, a `scripts/validate.py` czyta także skrypty), a trzecią
w regułach i w skillu przeglądu: podgląd i jego commit nigdy nie dzielą
tury ani polecenia. Czy model się tego trzyma, sprawdza sesja
`gate-change-is-not-yes`; zgodnie z Twoim poleceniem nie została
uruchomiona, więc pierwszym sprawdzianem będzie pilotaż.

### Etap 6. Dowolny klient i model, wydanie (wersja 1.0.0, planowany)

Zaplanowany 14.11.2026. Cel: warstwa dowodowa i bramka docierają do klientów,
którzy nie są gospodarzami wtyczek; gospodarze wymienieni w README są
zmierzeni, a nie założeni; wybór modelu, także lokalnego, należy do
gospodarstwa. Jedna sesja, po pilotażu.

Decyzje stojące za etapem (rozdział 11): projekt nie dostarcza własnego
środowiska agenta ani wyboru modeli, ponieważ model wybiera gospodarz, a
wartością projektu jest wiedza o sprawach domowych i skrypty; serwer MCP
działa wyłącznie lokalnie, ponieważ rekord pozostaje w folderze
gospodarstwa.

Potrzebne z Twojej strony przed sesją: notatki z pilotażu; `codex login` na
komputerze roboczym; zgoda na zainstalowanie na nim OpenCode i OpenClaw;
model dla OpenCode (jeden model przez API oraz jeden model lokalny przez
Ollama, jeśli sprzęt go udźwignie).

- **A. Poprawki z pilotażu.** Najpierw błędy blokujące, każdy z testem
  jednostkowym albo sesją, która odtwarza go na danych syntetycznych.

- **B. Lokalny serwer MCP.** `mcp/householdbot_mcp.py`, tylko biblioteka
  standardowa, transport stdio, jeden folder gospodarstwa ustalony przy
  starcie (`--root` albo wskaźnik). Narzędzia odczytu, oznaczone jako tylko
  do odczytu: `due`, `find`, `show`, `validate`, `deadline`, `window`,
  `windows`, `holidays`, `band`, `statement_summary`, `chore_plan`.
  Narzędzia zapisu w dwóch fazach z Etapu 5: `preview_change` zwraca
  podgląd i żeton, a `commit_change` przyjmuje żeton oraz imię
  zatwierdzającego i jest oznaczone jako niszczące, dzięki czemu klient
  pyta swojego użytkownika. Żadne narzędzie nie przyjmuje ścieżki poza
  folderem; tekst dokumentu podróżuje jako argument narzędzia, nigdy w
  wierszu poleceń. Instrukcje serwera niosą w skrócie reguły bramki i
  treści niezaufanej. Skille nadal wywołują skrypty przez powłokę; serwer
  jest opcją dla klientów bez wtyczki (Claude Desktop, Cursor, Gemini CLI,
  Codex, OpenCode), z przykładem konfiguracji każdego z nich w CONNECTORS.
  Testy jednostkowe z klientem stdio: lista narzędzi, odczyt, podgląd i
  commit, odrzucona ścieżka, odrzucony żeton. Bez trybu HTTP: agent w
  chmurze (Grok Bot i podobne) nie sięga do folderu.

- **C. Gospodarze.** Dla Codexa, OpenCode i OpenClaw, na podstawie
  dokumentacji każdego gospodarza i uruchomienia na komputerze roboczym:
  jak wczytuje Agent Skills albo wtyczkę, jak uruchamia skrypty, jak prosi
  o zatwierdzenie, czy ma hooki. `scripts/package.py --skills-dir` buduje
  zwykłe drzewo `skills/` dla gospodarzy, którzy przyjmują foldery skilli,
  a nie wtyczki Claude. `core/rules/output-style.md` nazywa skill tak, jak
  robi to dany gospodarz. Jeden adapter na gospodarza w
  `scripts/session_test.py`. Część „Gdzie działa” w README oraz QUICKSTART
  dostają ścieżkę instalacji każdego gospodarza i jego bramkę (żeton i
  hook, żeton i zatwierdzanie gospodarza albo sam żeton). Gemini CLI
  dochodzi wtedy, gdy nie wymaga niczego poza zwykłym drzewem `skills/`.
  Aplikacja ChatGPT na komputer pozostaje opisana na podstawie
  dokumentacji.

- **D. Tabela zgodności.** Zestaw krytyczny przebiega dwa razy dla każdej
  pary gospodarza i modelu: Claude Code z Sonnetem i z Haiku; Codex z
  modelem domyślnym; OpenCode z wybranym modelem przez API i z modelem
  lokalnym; OpenClaw ze skonfigurowanym modelem. `docs/compatibility.md` i
  jego polska wersja podają datę, wersje i odsetek zaliczonych sesji w
  grupach (bramka, bezpieczeństwo, daty, język). Para jest „obsługiwana”,
  gdy każda sesja z grup „bramka” i „bezpieczeństwo” przechodzi w obu
  przebiegach; w pozostałych przypadkach „działa z ograniczeniami”, z
  nazwami niezaliczonych sesji. README nie wymienia gospodarza bez wiersza
  w tabeli.

- **E. Dokumenty i wydanie.** README i QUICKSTART w obu językach, CONNECTORS
  (serwer MCP), `docs/architecture.md` (tabela jako wynik badawczy),
  CHANGELOG, dwujęzyczne notatki wydania, oba manifesty w wersji 1.0.0, ten
  plan, pamięć projektu, commit. Push, tag i wydanie po Twoim „tak”;
  zgłoszenia do katalogów Claude i OpenAI należą do Ciebie.

Akceptacja: warunki 1–8 z rozdziału 1; testy jednostkowe, walidator i paczka
jak w Etapie 5; zestaw sesyjny dla Claude Code z Sonnetem przechodzi na
końcowej wersji tak jak w Etapie 5.

Koszt wywołań modelu: około 60 USD łącznie u dostawców (pięć płatnych par
po dwa przebiegi; model lokalny nie kosztuje).

Jeśli pilotaż nie zakończy się przed sesją, etap zamyka wersja 1.0.0-rc.4
bez części A, a wersja 1.0.0 zostaje oznaczona po pilotażu samym protokołem
zamknięcia.

---

## 8. Stan po Etapach 1–5

**Wersja 1.0.0-rc.4 (poprawki z sesji demonstracyjnej na rc.3).**

| Poziom | Wynik |
|---|---|
| 1. Struktura | `scripts/validate.py` (kontrola zapisu jednym wywołaniem czyta także skrypty): 0 błędów, 0 ostrzeżeń; `claude plugin validate --profile directory --strict` przechodzi dla wtyczki i marketplace |
| 2. Arytmetyka | 202 testy jednostkowe zielone (4 nowe): strona z kodowaniem i viewportem zapisana bajt w bajt, każdy inny `<meta>` odrzucony, szkielet strony przeglądu ze skilla przechodzi kontrolę zapisu, pomoc poleceń zapisu bez `--approved-by` |
| 3b. Sesje | 18 sesji gotowych (`--check`); nieuruchomione, zgodnie z Twoim poleceniem |
| 3. Zachowanie | nieuruchamiane |
| 4. Użycie | pięcioturowa sesja na rc.3 (1,03 USD), która wykryła usterki, opisana w Etapie 5 |

**Wersja 1.0.0-rc.3 (Etap 5, gwarancje w kodzie).**

| Poziom | Wynik |
|---|---|
| 1. Struktura | `scripts/validate.py` (nowa kontrola: brak zapisu jednym wywołaniem w skillach, regułach i agentach; obecność hooka): 0 błędów, 0 ostrzeżeń; `claude plugin validate --profile directory --strict` przechodzi dla wtyczki i marketplace; 385 plików wtyczki z 512 |
| 2. Rachunek | 198 testów jednostkowych zielonych (49 nowych): bramka (podgląd co do bajtu, żeton nieznany, użyty ponownie, przeterminowany, zmieniony i nieaktualny, zatwierdzający sprawdzany przy commicie, odrzucony wpis bez śladu w `.pending`, oryginały kopiowane przy commicie, zapisy zbiorcze), `save` (ścieżki, strony, identyfikatory, zastąpienie z kopią), eksport kalendarza (łamanie i znaki specjalne RFC 5545, stałe UID, neutralne tytuły, wpisy odwołane), pasma i ostatnie dni, etykiety, podstawy prawne pakietu PL, hook (8) i program sesji z gospodarzem skryptowym (7) |
| 3b. Sesje | 18 sesji gotowych (`--check`: każde gospodarstwo założone, każda wartość rozwiązana); nieuruchomione, bez wywołań modelu |
| 3. Zachowanie | w tym etapie nieuruchamiane |
| 4. Użycie | sześcioturowa sesja na rc.2, od której zaczął się etap (0,81 USD, opisana w Etapie 5) |

**Wersja 1.0.0-rc.1 (Etap 4, zasięg, utwardzenie, publikacja).**

| Poziom | Wynik |
|---|---|
| 1. Struktura | `scripts/validate.py` (nowe kontrole: każdy pakiet przez `dates.py check-pack`, agent `deadline-watcher` tylko z narzędziami odczytu, cookbook przez `cookbook.py check`, numer wersji z oznaczeniem wydania próbnego): 0 błędów, 0 ostrzeżeń; `claude plugin validate --profile directory --strict`: przechodzi dla wtyczki i marketplace; 382 pliki wtyczki z 512; `scripts/package.py --skills` buduje paczkę wtyczki i 34 zipy skilli, dwa kolejne budowania dają identyczne sumy SHA-256 (paczka 5,8 MB) |
| 2. Rachunek | 149 testów jednostkowych zielonych (42 nowych): święta bankowe Anglii i Walii zgodne z listą gov.uk dla lat 2019–2028, dni zastępcze i reguły „n-ty dzień tygodnia miesiąca”, terminy liczone od dnia zdarzenia włącznie, doręczenie w dniach roboczych, `check-pack`, wyszukiwanie okien terminów, pakiet GB (rejestracja urodzenia bez przesunięcia z weekendu, potwierdzenie doręczenia pozwu przez Boże Narodzenie, kwoty w funtach), 16 testów bezpieczeństwa i 5 testów cookbooka |
| 3. Zachowanie | 115 przypadków (Sonnet, sędzia Sonnet, bez powłoki). Pilot 14 nowych przypadków: 8/14. Pełny przebieg z porównaniem bez wtyczki: z wtyczką 98/115, średnio 0,95; bez wtyczki 19/115, średnio 0,64; ocena treści przez sędziego zaliczona w 98 przypadkach z wtyczką i w 20 bez niej; 25,11 USD. Ponowna ocena 17 porażek przez osobnego agenta: 10 realnych, 7 zgodnych z rubryką. Powtórki po poprawkach: 20/34, potem 6/18 i kontrola regresji 24/28. Przebieg końcowy: 103/115, średnio 0,97, 17,26 USD; ostatnia powtórka po poprawkach: 21/29, 4,38 USD; zmiana konta po poprawce 3/3, 0,36 USD |
| 4. Użycie | sesja `claude -p` ze skryptami (Windows), 7 tur na danych syntetycznych gospodarstwa z Anglii, około 0,79 USD: pulpit (płatności do końca miesiąca £225.80 za 3 płatności, jedna po terminie; wiersz „nie śledzimy” dla każdej luki) zapisany po zgodzie Emmy jako strona HTML w `reviews/`; terminy pozwu w sądzie hrabstwa ze skryptu (potwierdzenie doręczenia pon. 28.12.2026 z przesunięciem na wt. 29.12 i planem na czw. 24.12; obrona pon. 11.01.2027) i dwa przypomnienia zapisane po zgodzie Jamesa; skill gospodarstwa do odczytów liczników: zgoda dana przed pokazaniem szkicu niczego nie zatwierdziła, zapis do `skills/meter-readings/` w folderze gospodarstwa dopiero po zgodzie na pokazany szkic, nic w folderze domowym użytkownika; rekord bez błędów walidacji. Ujawniła trzy usterki, poprawione: zapis strony i skilla bez wiersza w dzienniku decyzji; okno terminu obrony uznane za brak w pakiecie po zbyt szerokim przeszukaniu (nowe polecenie `dates.py windows`); wpis przygotowany w pliku zamiast na standardowym wejściu (wzór polecenia z here-documentem w `deadline-tracker`) |

**Przebiegi testów zachowania w Etapie 4.**

| Przebieg | Wynik | Co ujawnił |
|---|---|---|
| pilot (14 nowych przypadków) | 8/14, 2,22 USD | dwie prośby nie uruchomiły skilla: terminy z pozwu (odpowiedź z pamięci z błędną datą) i instalacja skilla (próba zapisu bez `build-skill`); atrapa Dysku Google z niespójnymi datami opłaconych rachunków; trzy rubryki zbyt dosłowne |
| pulpit, powtórka | 0/3 przed zmianą rubryki | rubryka wymagała liczby dni przy każdej dacie; ponowna ocena przez osobnego agenta uznała odpowiedzi za zgodne z sednem, więc rubryka opisuje sedno |
| pełny, z porównaniem bez wtyczki | z wtyczką 98/115 (0,95), bez wtyczki 19/115 (0,64); 25,11 USD | 10 porażek realnych: pulpit nazwał datę planowaną ostatnim dniem wypowiedzenia OC i opisał 7 dni jako „ten tydzień”; błędny dzień tygodnia przy przeszłej dacie rozpoczęcia wniosku; po śmierci ojca odpowiedź bez zdania współczucia (reguła „bez frazesów” konkurowała z nim); jadłospis z imionami przy upodobaniach obok wykluczonego produktu; sprawdzanie pakietu bez Pythona pominęło niezdefiniowaną regułę liczenia; polisa domu bez zakresu, bo odpowiedź nie otworzyła polisy; `build-skill` nie powiedział, gdzie zapisze skill; zamiana obowiązków bez propozycji przygotowania; prośba o numer paszportu bez uruchomienia skilla. 7 odpowiedzi spełnia rubryki: rubryka z datą uruchomienia, słowo „once” czytane dosłownie, wymóg wskazania skilla, o który prośba nie pytała, data przyszła w treści prośby |
| powtórki po poprawkach (17 przypadków po 2 razy) | 20/34, 5,99 USD | osiem przypadków w pełni naprawionych (`build-skill` mówi, gdzie zapisze skill, zamiana obowiązków, pozew, dokumenty tożsamości, numer paszportu, polisa domu z zakresem z samej polisy, lista zakupów, przegląd domu); pulpit nazywał już dobrze ostatni dzień, ale pisał „folderu inbox/ nie ma, więc nic nie czeka” |
| druga powtórka (9 przypadków po 2 razy) i kontrola regresji (28 przypadków zmienionych skilli) | 6/18 i 24/28; 7,92 USD | sędzia widzi tylko ostatnią odpowiedź, bez prośby domownika: rubryka odwołania karała datę decyzji i kwotę z wklejonej decyzji jako niepodane, rubryka śmierci wymagała zdania o poradach, choć odpowiedź nie dotyczyła spadku, a rubryka pisma ze szkoły brała szkołę wskazaną w rejestrze za podanie odbiorcy wpłaty; angielskie przykłady ze skilla przepisane dosłownie na polską stronę pulpitu; trzy błędne dni tygodnia liczone ręcznie na jednym pulpicie; sprawdzanie pakietu bez Pythona nadal pomija niezdefiniowaną regułę liczenia |
| końcowy | 103/115, średnio 0,97, 17,26 USD | odwołanie, pismo ze szkoły, jadłospis, skill czynszu, akta auta i narodziny w Anglii przechodzą; ponowna ocena 12 porażek: 6 realnych. Prośba „zmarł mój tata, nie wiem, od czego zacząć” uruchamiała router (fraza „od czego zacząć”), który nie znał reguły o zdaniu współczucia; odpowiedź dla gospodarstwa anglojęzycznego o polskiej decyzji w całości po polsku; lista płatności nazwała ratę z minioną datą planowaną „po terminie”; `build-skill` zadał same pytania przy opisanym zadaniu; szkic pakietu bez źródeł podał regułę liczenia jako ustaloną; ręczne sprawdzanie pakietu pominęło niezdefiniowaną regułę liczenia |
| powtórka po poprawkach (8 przypadków po 2 razy, 13 przypadków zmienionych skilli po 1 razie) | 21/29, 4,38 USD; zmiana konta po poprawce 3/3, 0,36 USD | `build-skill` ze szkicem od razu, pakiet Szkocji z regułą liczenia oznaczoną do zbadania i odpowiedź po angielsku wokół polskiego szkicu: po 2/2; śmierć ojca, lista płatności, przeprowadzka i ręczne sprawdzanie pakietu: po 1/2; pulpit 0/2 przy odpowiedziach, które ponowna ocena uznaje za zgodne z rubryką (długa strona, oceny sędziów niespójne); przypadek zmiany konta pokazał pełny numer konta w cytacie z rachunku, więc reguła danych osobowych obejmuje teraz cytaty |

**Porównanie z wtyczką i bez niej.** Bez wtyczki przechodzi w całości 19
przypadków: bramki i odmowy, które model zachowuje sam (nie usuwa papierów,
rozpoznaje oszustwo z paczką i z nowym numerem konta, nie powtarza numeru
polisy, nie udaje skrzynki ani kalendarza, których nie ma), oraz proste
czynności na plikach (dopisanie do listy zakupów, odczyt z rejestru, kopia
konfliktowa). Różnica pojawia się tam, gdzie odpowiedź zależy od rekordu i
pakietu: terminy z dniem tygodnia i podstawą prawną, kwoty z rejestru,
dokumenty, których brakuje, zgoda przed zapisem. Wtyczka podwaja koszt
odpowiedzi (16,63 wobec 8,48 USD), bo czyta profil, rejestry i pakiet.

**Wnioski z Etapu 4.**

1. Skill wygrywa z wiedzą ogólną modelu tylko wtedy, gdy opis zawiera słowa
   domownika. Pytanie o terminy pozwu brzmi jak wiedza ogólna, więc bez frazy
   „how long do we have to reply” model odpowiadał z pamięci i podał złą datę.
   Opis, który już zawiera odpowiedź („nie przechowuje numerów dokumentów”),
   też pozwala pominąć skill; fraza z samą prośbą („numer paszportu”) temu
   zapobiega.
2. Tekst spoza rekordu nie trafia do wiersza poleceń, a wzór polecenia z
   here-documentem w skillu działa lepiej niż sam zakaz: bez wzoru przed oczami
   model przygotował wpis w pliku.
3. Identyfikatory rozpoznaje się po formacie i sumie kontrolnej, nie po
   słowach kluczowych: IBAN dowolnego kraju po długości dla kraju, numer karty
   po algorytmie Luhna. Walidator przestał brać zwykłe zdania za numery kont.
4. Pakiet zebrany przez agentów wymaga osobnej weryfikacji w tekstach
   źródłowych: 4 błędy na około 40 twierdzeń, wszystkie tego samego rodzaju,
   czyli reguła ogólna zastosowana tam, gdzie akt stanowi inaczej (przesunięcie
   z weekendu, doręczenie w dniach roboczych).
5. „Nie ma w pakiecie” wolno powiedzieć dopiero po wyszukiwaniu, które mogło
   trafić. Zbyt szerokie przeszukanie dało długi wynik czytany w części i
   fałszywy brak; wyszukiwanie po słowach w skrypcie daje krótką i pełną
   odpowiedź.
6. Data planowana i data ostateczna mają różne nazwy na każdej powierzchni
   (lista, pulpit, strona HTML). Nazwanie planu „ostatnim dniem” zabiera
   domownikowi dni.
7. Każdy zapis w folderze gospodarstwa, nie tylko w rejestrze, zostawia wiersz
   w dzienniku decyzji; skill, który pisze narzędziem Write, musi mieć to w
   instrukcji, bo skrypt robi to za niego tylko przy rejestrach.
8. Reguły jednego skilla nie mogą ze sobą konkurować: „bez frazesów” wypierało
   „jedno zdanie współczucia”. Reguła o pierwszym zdaniu stoi teraz w bramkach.
9. Porównanie z wersją bez wtyczki pokazuje, gdzie jest wartość: rekord, pakiet
   i daty z dniem tygodnia. Bramki model w dużej części zachowuje sam.
10. Sędzia czyta rubrykę dosłownie („says once”, wymóg wskazania skilla, data
    uruchomienia zapisana w rubryce). Rubryka opisuje sedno i nie zawiera daty
    uruchomienia; prośba w przypadku testowym nie podaje przyszłej daty jako
    przeszłej.
11. `claude -p --resume` podaje koszt sesji narastająco. Sumowanie wartości z
    kolejnych tur zawyżyło koszty sesji Etapów 2 i 3; poprawione na 0,80 i
    0,91 USD.
12. Sędzia z `focus: last_message` widzi tylko ostatnią odpowiedź, bez prośby
    domownika, rekordu i pakietu. Rubryka podaje więc fakty z prośby, na
    których opiera ocenę (decyzję wklejoną w wiadomości), a warunek, który
    może nie mieć zastosowania („spadek za zdaniem o poradach”), mówi, kiedy
    go nie ma.
13. Fraza wyzwalająca jednego skilla bywa częścią prośby do innego: „nie wiem,
    od czego zacząć” po śmierci ojca uruchamiała router. Reguła, która musi
    zadziałać zawsze (zdanie współczucia), stoi także w routerze.
14. Przykłady cytowane w skillu po angielsku model przepisuje dosłownie na
    stronę w innym języku; skill mówi, że każda etykieta jest w języku
    gospodarstwa, i podaje tłumaczenie.
15. Ścieżka bez Pythona to słaby punkt testów na Windows: dni tygodnia
    liczone ręcznie na długiej stronie i ręczne sprawdzanie pakietu bywają
    błędne, a te same kroki ze skryptem są deterministyczne i pokryte testami
    jednostkowymi.
16. Reguła identyfikatorów obejmuje cytaty. Odpowiedź, która dowodziła zmiany
    konta, zacytowała linię rachunku z pełnym numerem; sędzia treści ją
    przepuścił, a złapał ją dopiero grader wzorca. Bramki na identyfikatory
    sprawdza się wzorcem, nie sędzią.

**Wersja 0.3.0 (Etap 3, dom, rodzina i codzienność).**

| Poziom | Wynik |
|---|---|
| 1. Struktura | `scripts/validate.py` (nowe kontrole: zdarzenia życiowe wskazują istniejące okna, okresy przechowywania mają podstawę albo oznaczenie „sugerowany”): 0 błędów, 0 ostrzeżeń; `claude plugin validate --profile directory --strict`: przechodzi dla wtyczki i marketplace; 297 plików wtyczki z 512 |
| 2. Rachunek | 107 testów jednostkowych zielonych, w tym 14 dla `chores.py` (deterministyczność, równe obciążenie według udziału, próg wieku, stała osoba, co drugi tydzień, wyrównanie z poprzednich tygodni, zamiany, bilans), zdarzenie życiowe liczone z jednej daty, dokumenty po terminie przechowywania, `complete --from-done`, lista dokumentów danego typu, imię zatwierdzającego zamiast cytatu, wpis ze standardowego wejścia w UTF-8 |
| 3. Zachowanie | 101 przypadków (Sonnet, sędzia Sonnet, bez powłoki). Przebiegi pełne: 78/101 (0,92), 78/101 (0,93), końcowy 97/101, średnio 0,99, 15,18 USD; powtórki porażek po poprawkach opisane niżej |
| 4. Użycie | sesja `claude -p` ze skryptami (Windows), 8 tur na danych syntetycznych, około 0,91 USD: kupno używanego auta od osoby prywatnej (`dates.py event`: PCC-3 do czw. 26.11.2026, rejestracja do pon. 14.12.2026 z planem na pt. 11.12.2026), dwa przypomnienia zapisane po zgodzie Piotra; plan obowiązków na tydzień 2026-W47 policzony i zapisany przez `chores.py` po zgodzie Anny; jadłospis na 7 dni w budżecie (208 zł szacunkowo z rozpisaną sumą) zapisany do `lists/meals-2026-W47.md`, lista zakupów uzupełniona po osobnej zgodzie; przegląd papierów: rachunek z 2018 r. do zniszczenia i propozycje terminów przechowywania z podstawą; rekord i rejestr obowiązków bez błędów. Ujawniła jedną usterkę: imię zatwierdzającego zapisane razem z cytatem jego wiadomości (poprawione w `record.py`, test) |

**Przebiegi testów zachowania w Etapie 3.**

| Przebieg | Wynik | Co ujawnił |
|---|---|---|
| pilot 1 (6 przypadków) | 4/6, 0,72 USD | rachunek w danych testowych z terminem przechowywania niezgodnym z regułą 6 lat z profilu; jadłospis wstrzymany do odpowiedzi o zawartość lodówki; zbyt ostra reguła sprawdzająca wzmiankę o produkcie pomijanym |
| pilot 2 (11 przypadków) | 10/11, 1,44 USD | bez powłoki odpowiedź uznała, że nie odczyta rekordu (zasada „brak powłoki to nie brak rekordu” trafiła do reguły wspólnej) |
| pilot 3 (7 przypadków, część B pakietu) | 4/7, 1,32 USD | `insurance-overview` nie uruchomił się przy „jakie ubezpieczenia musimy mieć, doradź” i odpowiedź doradzała produkty; tytuł z nazwą specjalizacji oferowany jako opcja; zbyt szczegółowa rubryka |
| pilot 4 (8 przypadków, część A pakietu) | 4/6 ocenionych, 2 przerwane błędem uwierzytelnienia | po śmierci ojca odpowiedź bez zdania współczucia na początku; rubryka mandatu karała za pytanie o zatwierdzającego |
| pełny 1 | 78/101, średnio 0,92, 15,67 USD | lista 31 skilli przekroczyła budżet opisów, więc część skilli nie była widoczna; bez powłoki profil nie był czytany; naruszenia bramek: zgodę daną z góry potraktowano jako zgodę na jadłospis, składniki z przepisu dopisano do listy bez zgody, PIN wrócił w odpowiedzi, przegląd roczny zmieniał rejestr przy prośbie o usunięcie rachunków, szkic w Gmailu powstał przed akceptacją treści |
| pełny 2 | 78/101, średnio 0,93, 14,75 USD | krótsze opisy zgubiły frazy wyzwalające i cztery prośby nie uruchomiły skilla; plik awaryjny pytał po jednym pytaniu bez szkicu z rekordu; przegląd poczty odmówił, bo profil oznaczał pocztę jako niepodłączoną, i porównał adres konta sesji z domownikami; wpis przygotowywany w pliku przed zgodą; teczka zdrowia prosiła o skierowanie, które było w rejestrze; pismo ze szkoły czytane ze streszczenia w rejestrze; dochody spoza pakietu opisane przepisami z pamięci; „nie podano” zamienione na „brak” w porównaniu ofert; w pakiecie błąd przy wspólnym rozliczeniu (ryczałt od najmu prywatnego go nie wyklucza, art. 6 ust. 8 ustawy o PIT) |
| próba (4 przypadki bez skilla) | 4/4, 0,57 USD | po przywróceniu fraz każdy przypadek uruchomił właściwy skill (`household-customize`, `life-event`, `vehicle-file`, `deadline-tracker`) |
| pełny 3 (końcowy) | 97/101, średnio 0,99, 15,18 USD | odpowiedź o OC bez wskazania dokumentu w rejestrze (reguła cytowania: id, tytuł, strona); przy wyjeździe ocena paszportu wymieszana z terminem jego odnowienia; dwie oceny sędziego niespójne między przebiegami |
| powtórki 4 porażek (po 2 razy) | 5/8, 1,59 USD | rachunki 2/2, OC 2/2 po regule cytowania; wyjazd 1/2 przed poprawką skilla; pismo ze szkoły 0/2 przy odpowiedziach spełniających rubrykę, więc rubryka przepisana na punkty |
| powtórki po poprawkach (2 przypadki po 2 razy) | 3/4, 1,12 USD | wyjazd 2/2 po oddzieleniu oceny ważności od terminu odnowienia; pismo ze szkoły 1/2 przy rubryce w punktach: odpowiedź oceniona negatywnie spełnia rubrykę w mojej ocenie, sędziowie podzielili się 1 do 2 |

**Wnioski z Etapu 3.**

1. Plan, który skrypt liczy deterministycznie, można przedstawić rodzinie
   jako fakt w liczbach; spory o sprawiedliwość przenoszą się na udziały i
   progi wieku, które ustala dorosły.
2. Dane o zdrowiu wymagają reguły także dla tytułów: tytuł wpisu, przypomnienia
   i wydarzenia czytają osoby spoza sprawy.
3. Agent piszący skille według specyfikacji i wzorców przyspiesza etap; jego
   rubryki bywają zbyt szczegółowe i wymagają uproszczenia do sedna.
4. Dane testowe z kilku generatorów muszą być spójne z regułami profilu
   (okres przechowywania), bo model słusznie zgłasza niezgodność.
5. Zdanie o syntetycznym rekordzie w każdej rubryce i lista tego, co nie jest
   błędem, utrzymują ocenę sędziego stabilną.
6. Lista skilli ma budżet znaków. Przy 31 skillach opisy muszą być krótkie
   (około 300 znaków, frazy wyzwalające na początku), a skrócenie nie może
   zgubić fraz dla próśb, które nie brzmią jak zadanie: „od teraz po polsku”,
   „do kiedy odwołanie”. Bez nich model odpowiada sam, bez skilla.
7. Krok 0 czyta `household-profile.md` narzędziem Read, a skrypt `locate`
   uruchamia dopiero, gdy profilu nie ma. Brak powłoki nie oznacza braku
   rekordu.
8. Wpis przygotowany w pliku to też zapis przed zgodą: wpis trafia do skryptu
   na standardowym wejściu albo w `--json`, a bez powłoki tylko się go pokazuje.
9. Narzędzie podłączone w sesji należy do domownika. Konto, na którym działa
   sesja, nie jest danymi gospodarstwa: nie rozstrzyga, czyja jest skrzynka, i
   nie trafia do odpowiedzi.
10. Sędzia nie widzi pakietu krajowego, więc reguły przypisane pakietowi muszą
    być w rubryce wymienione jako dopuszczalne. Gdy wyniki nie mają uzasadnień
    sędziego, ponowna ocena przez osobnego agenta (sama rubryka i odpowiedź)
    wskazuje, które porażki są realne.
11. Rejestr streszcza dokument, więc szczegóły (sala, miejsce, godzina) bierze
    się z samego pisma, a prośba o zapisanie papieru zaczyna się od sprawdzenia,
    czy już jest w rejestrze.

**Wersja 0.2.0 (Etap 2, pieniądze i korespondencja).**

| Poziom | Wynik |
|---|---|
| 1. Struktura | `scripts/validate.py`: 0 błędów, 0 ostrzeżeń; `claude plugin validate --profile directory --strict`: przechodzi dla wtyczki i marketplace; 307 plików wtyczki z 512 |
| 2. Rachunek | 86 testów jednostkowych zielonych: wyciągi w trzech układach co do grosza, maskowanie, saldo bieżące, luka w danych, podwyżki, reguły kategorii, `locate` z folderu wtyczki, okna terminów po stronie firmy, każde okno pakietu liczone bez błędu |
| 3. Zachowanie | 62 przypadki (Sonnet, sędzia Sonnet, bez powłoki). Przebieg 1: 51/62, średnio 0,95, 6,68 USD. Przebieg końcowy: 58/62, średnio 0,98, 7,85 USD. Powtórki po poprawkach: cztery porażki po 3 razy, potem 13 przypadków skilli zmienionych po przebiegu końcowym: 16 z 17 przebiegów zielonych (szczegóły niżej) |
| 4. Użycie | sesja `claude -p` ze skryptami (Windows): lista płatności 731,60 zł z progiem dwojga dorosłych i końcówką konta, pierwsza zgoda bez zapisu, „zapłaciłam” jako próba z drugą zgodą, zapis z „zgoda: Anna” i następne wystąpienia (woda do pt. 08.01.2027, cofnięte z soboty; prąd do czw. 17.12.2026); wcześniejsza sesja: wyciąg z zakresem i sumami zgodnymi z danymi testowymi, wypowiedzenie internetu (ostatni dzień pon. 23.11.2026, nadać do śr. 18.11.2026) z trzema wpisami po zgodzie; razem około 0,80 USD (dwie sesje) |

**Przebiegi testów zachowania w Etapie 2.**

| Przebieg | Wynik | Co ujawnił |
|---|---|---|
| 1 | 51/62, średnio 0,95, 6,68 USD | bez powłoki model nie znajdował pakietu krajowego i podawał przepisy z pamięci; szkic maila podpisany nazwiskiem z konta, na którym działała sesja; szkic w Gmailu utworzony przed pokazaniem treści; odwołanie zaadresowane do wójta; przegląd miesiąca bez dni tygodnia; wyciąg testowy niespójny z rekordem; dwa gradery Etapu 1 nie znały nowego skilla `bills-due` |
| 2 (11 porażek) | 9/11, 1,84 USD | poprawki działają; odpowiedź o reklamacji do ubezpieczyciela przypisała uznanie milczenia do złego artykułu, bo pakiet podawał artykuły zbiorczo |
| końcowy | 58/62, średnio 0,98, 7,85 USD | lista płatności bez wskazania, skąd wziąć numer konta do wody; trzy oceny sędziego niespójne między przebiegami |
| 3 (4 przypadki po 3 razy) | `budget-snapshot` 3/3, `vague-start` 3/3, `bills-due` 1/3, odwołanie 0/3; 1,51 USD | rubryki w punktach, ze zdaniem o syntetycznym rekordzie, stabilizują ocenę; przy odwołaniu model raz wpisywał numer decyzji podany przez domownika, raz nie, a raz wpisał go i napisał, że go pominął, więc reguła numerów spraw została ujednolicona |
| 4 (skille zmienione po przebiegu końcowym) | 16 z 17 przebiegów: `bills-due-payment-list` 3/3, odwołanie 2/3, pozostałe 11 przypadków `bills-due`, `reply-to-letter`, `cancel-or-switch`, `complaint-and-claim` zielone; 2,51 USD | jedyna porażka spełnia rubrykę w mojej ocenie; realny drobiazg: bez powłoki odpowiedź uznała, że nie znajdzie rekordu, zamiast przeczytać profil (dopisane do gotchas) |

**Wnioski z Etapu 2.**

1. Skill podaje ścieżkę każdego pliku, którego potrzebuje (pakiet krajowy).
   Bez powłoki model nie szuka i uznaje, że pliku nie ma.
2. Skrypt uruchomiony z folderu skilla nie widzi rekordu, dlatego skille
   wołają go z folderu roboczego sesji z `--start`.
3. Model widzi nazwisko właściciela konta i konfiguracji gita, więc podpis
   pisma pochodzi wyłącznie z profilu albo jest polem do uzupełnienia.
4. Okno terminu po stronie firmy potrzebuje własnych pól: co dotrzymuje
   terminu i co oznacza milczenie. Reguła ogólna dla oświadczeń domownika
   była myląca.
5. Każdy nowy skill przejmuje część próśb, więc gradery `skill-used`
   starszych przypadków poszerza się razem z dodaniem skilla.
6. Rubryka w punktach, z listą tego, co nie jest błędem, stabilizuje sędziego.
   Przy długich polskich odpowiedziach ocena tej samej jakości wahała się od
   0/3 do 3/3.
7. Dane testowe z różnych generatorów muszą się zgadzać (dostawca, kwoty,
   własność domu); model słusznie zgłaszał rozbieżności.

**Pakiet PL, uzupełnienie z Etapu 2.** Cztery sekcje zweryfikowane 13.11.2026
w tekstach jednolitych z ELI Sejmu, z nowelizacjami w mocy na ten dzień:
Ordynacja podatkowa od 1.10.2026 (Dz.U. 2026 poz. 846), Prawo energetyczne
(Dz.U. 2026 poz. 516 i 900), KC art. 77 § 2 (forma dokumentowa wypowiedzenia
umowy zawartej w formie pisemnej, dokumentowej albo elektronicznej). Cztery
punkty nierozstrzygnięte, opisane w pakiecie bez twierdzenia i wypisane w
`PL.json` (`sources.uncertain`): automatyczne złożenie zeznania przez Twój
e-PIT dla PIT-28; skutek milczenia przy reklamacji usługi płatniczej; skutek
milczenia przy reklamacji rozliczeń energii; krótsze niż ustawowe
wypowiedzenie najmu lokalu w umowie.

**Wersja 0.1.1 (Etap 1.1, dwujęzyczność).**

| Poziom | Wynik |
|---|---|
| 1. Struktura | `scripts/validate.py` z nowymi kontrolami języków: 0 błędów, 0 ostrzeżeń; `claude plugin validate --profile directory --strict`: przechodzi; 147 plików wtyczki z 512 |
| 2. Rachunek | 65 testów jednostkowych zielonych |
| 3. Zachowanie | 31 przypadków (Sonnet, sędzia Sonnet, bez powłoki). Przebieg 1: 28/31, średnio 0,96, 2,87 USD; ujawnił notatkę z numerem konta proponowaną przy podejrzanym mailu i dwa przypadki słabego wyzwalania skilli. Przebieg końcowy: 30/31, średnio 0,99, 2,84 USD; jedyna porażka to router bez Pythona, który pomylił dni tygodnia przy odpowiedzi z rejestru. Po dopisaniu reguły liczenia dnia tygodnia od dzisiejszej daty ten przypadek przechodzi 3/3 |
| 4. Użycie | sesja `claude -p` ze skryptami dla gospodarstwa anglojęzycznego: daty `Fri 13 Nov 2026`, kwoty `PLN 286.40`, zamknięcie rachunku jako próba z pytaniem o zatwierdzającego; ujawniła brak dnia zapasu w następnym wystąpieniu rachunku (poprawione polem `transit_buffer_days`) |

**Wersja 0.1.0 (Etap 1).**

| Poziom | Wynik |
|---|---|
| 1. Struktura | `scripts/validate.py`: 0 błędów, 0 ostrzeżeń; `claude plugin validate --profile directory --strict`: przechodzi dla wtyczki i marketplace; instalacja z marketplace w odizolowanej konfiguracji: przechodzi |
| 2. Rachunek | 52 testy jednostkowe zielone |
| 3. Zachowanie | 24 przypadki, model Sonnet, sędzia Sonnet, bez powłoki (Windows). Przebieg końcowy na wersji z commita: 24/24, średnio 1,00, 2,21 USD |
| 4. Użycie | sesja wieloturowa `claude -p` ze skryptami (Windows), 10 tur na danych syntetycznych: konfiguracja, trzy dokumenty zapisane po zgodach, lista terminów, przegląd tygodnia; rekord bez błędów walidacji, daty zgodne z pakietem, 12 wpisów w dzienniku z imieniem zatwierdzającego; około 0,93 USD |

**Przebiegi testów zachowania w Etapie 1.**

| Przebieg | Wynik | Co ujawnił |
|---|---|---|
| 1 (sędzia Haiku) | 15/24, średnio 0,84, 1,74 USD | brak wariantu bez Pythona w kroku 0 `household-doctor`; atrapa `python3` zawiesiła dwa skrypty przygotowujące; rubryki zależne od daty uruchomienia i zbyt dosłowne |
| 2 (sędzia Sonnet) | 20/24, średnio 0,95, 2,20 USD | `household-doctor` wypisał PESEL przy zgłaszaniu błędu; onboarding nie potwierdził kraju podanego w pierwszej wiadomości; sędzia brał identyfikatory rejestru za numer polisy |
| 3 (zmienione grupy) | 8/8, 0,77 USD | poprawki działają |
| końcowy | 24/24, średnio 1,00, 2,21 USD | wersja z commita |

**Sesja wieloturowa** sprawdziła ścieżkę ze skryptami: OC wypowiadane dzień
przed końcem okresu z 5 dniami na pocztę, odwołanie od decyzji do
19.11 bez zapasu (liczy się nadanie na Poczcie Polskiej), opłata 14 dni od
uprawomocnienia, rachunek z dniem na przelew cofnięty z niedzieli na piątek.
Ujawniła jedną usterkę: ta sama seria dla dwóch różnych zobowiązań z jednego
pisma. Poprawione w `file-document`, opisie rejestrów i komunikacie
walidatora.

**Wnioski z Etapu 1.**

1. Każdy krok, który woła skrypt, potrzebuje wariantu bez Pythona, łącznie ze
   znalezieniem rekordu. Bez tego skill poprawnie odmawia pracy, ale nic nie
   daje.
2. Zasada „nie powtarzaj identyfikatora” musi obejmować też zgłaszanie
   błędów; model chętnie cytuje złą wartość, żeby ją pokazać.
3. Rubryka dla sędziego nazywa wprost, co nie jest błędem (identyfikatory
   rejestru, daty pomocnicze bez dnia tygodnia), i nie może zależeć od dnia
   uruchomienia.
4. Haiku jako sędzia daje fałszywe negatywy na długich odpowiedziach po
   polsku; testy zachowania uruchamiać z `--judge-model sonnet`.
5. Na Windows `python3` bywa atrapą ze Sklepu; skrypty pomocnicze i skille
   muszą to rozpoznawać.

**Pakiet PL** zweryfikowany 13.11.2026 w tekstach jednolitych z serwisu ELI
Sejmu (lista źródeł w `core/locale/PL.md`): 29 twierdzeń potwierdzonych, 7
poprawionych, 2 nierozstrzygnięte.

- Poprawione: zarzuty od nakazu zapłaty w postępowaniu nakazowym to miesiąc
  (KPC art. 480² § 2 pkt 3), nie 14 dni; e-Doręczenia: doręczenie w dniu
  następnym po upływie 14 dni (art. 42 ust. 2); list sądowy: dwa okresy po 7
  dni (KPC art. 139 § 1) i wyjątki z art. 139¹ i 505³⁴; odstąpienie od umowy
  po nieumówionej wizycie: 30 dni (art. 27 ust. 2); badanie techniczne:
  art. 81 ust. 6, auto na gaz co roku; abonament RTV do 25. dnia każdego
  miesiąca; ostrzeżenie o fałszywych e-mailach w brzmieniu z podatki.gov.pl.
- Potwierdzone wbrew moim wątpliwościom: wypowiedzenie OC najpóźniej dzień
  przed końcem okresu (art. 28 ust. 1); paszport na 5 lat do 12. roku życia.
  Mój błąd w danych testowych i w przykładzie `file-document` (OC do
  ostatniego dnia okresu) poprawiony.
- Nierozstrzygnięte: dzień doręczenia nieodebranego listu sądowego (wynika z
  orzecznictwa SN, niedostępnego automatycznie); ważność pierwszego prawa
  jazdy kategorii B wydanego od września 2026 (okres próbny). Pakiet każe w
  obu przypadkach sprawdzić datę w dokumencie lub w sądzie.

---

## 9. Luki wykryte przy weryfikacji planu

| Luka | Gdzie pokryta | Stan |
|---|---|---|
| Daty liczone wyłącznie przez model | D4, `dates.py` | zamknięta |
| Brak danych krajowych czytelnych dla skryptu | D7, `PL.json` | zamknięta |
| Odwołania do `shared/` niedostępne w czacie | D5, `sync.py`, walidator | zamknięta |
| Nazwa z samych słów ogólnych | D1 | decyzja podjęta, ryzyko ręcznej oceny |
| Pakiet PL niezweryfikowany w źródłach | Etap 1 E, Etap 1.1 | zamknięta; oba punkty otwarte w Etapie 1 rozstrzygnięte w Etapie 1.1 |
| Brak testów zachowania i danych testowych | D12, 24 przypadki, generator | zamknięta dla rdzenia |
| Brak wersji schematu rejestrów | D3, `migrate` | zamknięta |
| Rosnący rejestr czytany w całości | `record.py due/find`, `archive` | zamknięta |
| Konflikty synchronizacji we wspólnym folderze | `conflicts`, `merge`, blokada zapisu | zamknięta |
| Brak reguły „brak danych to nie zero” | `absent-is-not-zero.md` | zamknięta |
| Brak sprawdzenia, czyja jest skrzynka i dysk | `storage-scope.md` | zamknięta |
| Odczyt niezaufanych dokumentów przez agenta z prawem zapisu | `document-reader` bez zapisu | zamknięta |
| Zakres ograniczony do dokumentów i terminów | rozdział 4, Etapy 2 i 3 | w planie |
| Brak `customize`, `find-document`, `doctor` | Etap 1 F | zamknięta |
| Pola retencji bez skilla, który ich używa | `annual-review`, `record.py retention` | zamknięta (Etap 3) |
| Brak wymogów katalogu w walidatorze | `validate.py`, `--profile directory` | zamknięta |
| Brak README i licencji w folderze wtyczki | Etap 1 A | zamknięta |
| Brak SECURITY, CHANGELOG, NOTICE, QUICKSTART | Etap 1 A | zamknięta |
| Brak wariantu bezobsługowego | D11, `managed-agent-cookbooks/deadline-watcher` | zamknięta (Etap 4) |
| Brak analizy wzorca jako rezultatu badawczego | `docs/architecture.md` | zamknięta (Etap 4) |
| Brak wymaganej wersji Claude Code do testów | zaktualizowano do 2.1.323 | zamknięta |
| Identyfikator skopiowany do rejestru | `record.py validate`, `validate.py` | zamknięta (nowa) |
| Atrapa `python3` na Windows | wykrywanie interpretera w skillach i `seed.sh` | zamknięta (nowa) |
| Narzędzie tylko w jednym języku | D14, Etap 1.1 | zamknięta (nowa) |
| Płatność cykliczna traci dzień zapasu w następnym wystąpieniu | `transit_buffer_days` | zamknięta (nowa) |
| Podejrzana prośba o zmianę konta zapisywana jako notatka z numerem | reguła treści niezaufanej, `household-customize` | zamknięta (nowa) |
| Skrypt uruchomiony w folderze skilla nie widzi rekordu | `record.py locate` ze wskazówką, krok 0 każdego skilla, test jednostkowy | zamknięta (Etap 2) |
| Termin po stronie firmy liczony z regułą dla oświadczeń domownika | `met_by` i `silence` przy oknie w pakiecie | zamknięta (Etap 2) |
| Formy rodzajowe w polskich odpowiedziach zgadywane | reguła językowa: formy bezosobowe, dopóki domownik nie pokaże swoich | zamknięta (Etap 2) |
| Limit 512 plików przy pełnym zakresie | testy zachowania poza paczką, `scripts/eval.py` | zamknięta (Etap 2.1) |
| Następny przegląd liczony od starego terminu, nie od dnia wykonania | `record.py complete --from-done` | zamknięta (Etap 3) |
| Brak listy dokumentów danego typu bez słów kluczowych | `record.py find --type/--category` | zamknięta (Etap 3) |
| Tekst z dokumentu w wierszu poleceń (`$(...)` w nadawcy, nazwie załącznika, płatniku) | reguła treści niezaufanej (punkt 7), `--query-file -`, `--file -`, pole `original` | zamknięta (Etap 4) |
| Zapis przez dowiązanie lub junction poza folder gospodarstwa | `ensure_inside`, `copy_new`, unikalne pliki tymczasowe | zamknięta (Etap 4) |
| Obserwator terminów z powłoką w przebiegu bez nadzoru | `deadline-watcher` tylko z Read, Glob, Grep; walidator | zamknięta (Etap 4) |
| Scalanie kopii zatwierdzane bez pokazania zmian | `merge`: tylko kopie z listy, wszystkie zmienione pola, kontrola wpisów | zamknięta (Etap 4) |
| Identyfikatory spoza Polski (IBAN, NI, sort code) | `identifier_findings`, zapis odrzucany | zamknięta (Etap 4) |
| Pakiet tylko dla jednego kraju, bez zasięgu | pakiet GB, zasięg w pakiecie, pakiety własne w `packs/` | zamknięta (Etap 4) |
| Pasmo „po terminie” wyznaczane z daty planu, a nie z ostatniego dnia | `record.py due`, pięć skilli wypisujących pasma | zamknięta (Etap 5 A) |
| Etykiety pochodzenia i notatki skryptów po angielsku w polskiej odpowiedzi | `tags` w i18n, `provenance_local`, polskie podstawy prawne w pakiecie PL, `text_lang` | zamknięta (Etap 5 A) |
| Bramka zapisu opiera się na modelu: `--approved-by` wpisuje model, `hooks.json` jest pusty | zapis dwufazowy z żetonem, hook z oknem gospodarza | zamknięta (Etap 5 B) |
| Linię dziennika o zapisanym pliku wpisuje model | `record.py save` | zamknięta (Etap 5 B) |
| Przypomnienia wymagają konektora kalendarza albo zadania zaplanowanego | eksport `.ics` | zamknięta (Etap 5 C) |
| Ścieżka ze skryptami nie ma testów zachowania na komputerze roboczym | testy sesyjne przez `claude -p` z powłoką | program i 18 sesji gotowe; pierwszy przebieg czeka na płatną weryfikację (Etap 5 D) |
| Wiek pakietu sprawdza tylko przegląd roczny w gospodarstwie | comiesięczny przegląd pakietów w CI | zamknięta (Etap 5 E) |
| Pilotaż nie ma scenariuszy ani mierników | `docs/pilot.md` | zamknięta (Etap 5 F) |
| Warstwa dowodowa dostępna wyłącznie przez gospodarza wtyczek | lokalny serwer MCP | otwarta (Etap 6 B) |
| Obsługa Codexa sprawdzona bez uruchamiania modelu; pozostali gospodarze i modele niezmierzeni | adaptery gospodarzy, tabela zgodności | otwarta (Etap 6 C, D) |

---

## 10. Ryzyka

| Ryzyko | Ograniczenie |
|---|---|
| Zachowanie różni się między powierzchniami | D5, macierz testów w Etapie 4, pilotaż |
| Reguła prawna w pakiecie zdezaktualizuje się | akt, artykuł i źródło przy każdej regule, data przeglądu, znacznik `verify`, przegląd pakietu w `annual-review` |
| Wstrzyknięcie poleceń przez dokument lub wiadomość | reguły w każdym skillu, agent czytający bez zapisu, przypadki testowe |
| Realne dane trafią do repozytorium | dane syntetyczne, `.gitignore`, walidator odrzuca identyfikatory z poprawną sumą kontrolną |
| Koszt testów zachowania | pojedyncze przypadki w trakcie, pełny przebieg na zamknięciu etapu, limit kosztu; Etap 1: około 0,10 USD na przypadek (Sonnet, sędzia Sonnet), cały etap z sesją wieloturową około 8 USD |
| Brak Pythona u użytkownika | wariant bez skryptu z oznaczeniem `verify`, testowany przez eval na Windows |
| Limit 512 plików przy kolejnych pakietach | 382 pliki przy 34 skillach i dwóch pakietach; każdy pakiet dodaje 54 pliki; walidator ostrzega od 450; przy piątym pakiecie pakiety przechodzą do osobnej wtyczki |
| Nazwa trafi do ręcznej oceny w katalogu | opis i README jasno mówią, czym jest wtyczka; wstrzymanie nie jest odrzuceniem |
| Rozrost zakresu przy 34 skillach | akceptacja etapu oparta na ścieżkach od początku do końca; minimalna poprzeczka skilla: SKILL.md, gotchas, trzy przypadki |
| Anthropic wyda własną wtyczkę domową | projekt jest otwarty i badawczy; wartością pozostają pakiety krajowe, warstwa dowodowa i analiza wzorca |
| Wersje językowe dokumentów rozjadą się | walidator wymaga polskiego odpowiednika i wzajemnych odnośników; CLAUDE.md nakazuje zmieniać oba pliki |
| Każdy kolejny skill wymaga treści w dwóch językach | skille piszemy po angielsku (model odpowiada w języku gospodarstwa); w dwóch językach są tylko stałe teksty, szablony i dokumenty dla użytkowników |
| Słabszy albo lokalny model pomija bramkę zapisaną w instrukcjach | bramka w skryptach (Etap 5 B); gospodarz z modelem jest obsługiwany dopiero wtedy, gdy każda sesja bramki i bezpieczeństwa przechodzi dwa razy (Etap 6 D) |
| Agenci na platformie zatwierdzają sobie nawzajem zapisy | hook pyta człowieka w oknie samego gospodarza; gdy gospodarz takiego okna nie ma, README mówi, że bramka dowodzi podglądu, a nie czytelnika |
| Gospodarze różnie wczytują skille i różnie proszą o zatwierdzenie | jeden adapter i jeden wiersz tabeli zgodności na gospodarza; README nie wymienia gospodarza bez wiersza |
| Serwer MCP poszerza to, do czego sięga klient | wyłącznie lokalne stdio, jeden folder gospodarstwa ustalony przy starcie, narzędzia odczytu oznaczone jako tylko do odczytu, zapisy w dwóch fazach |
| Koszt przebiegów zgodności | limit na przebieg, sam zestaw krytyczny (około 18 sesji), model lokalny bez kosztu; około 60 USD w Etapie 6 |

---

## 11. Decyzje

Podjęte 13.11.2026:

1. Nazwa: `householdbot`.
2. Zakres: pełny, z codziennością (posiłki, zakupy, obowiązki, kalendarz rodziny) w Etapie 3.
3. Rejestry w JSON i skrypty jako warstwa dowodowa, zgodnie z wytycznymi Anthropic dla skilli.
4. Cztery etapy w czterech sesjach z pilotażem po każdym.
5. Dwujęzyczność: angielski domyślny, polski do wyboru (D14), z wersjami
   polskimi dokumentów dla użytkowników.
6. Testy zachowania poza paczką wtyczki (Etap 2.1).
7. Repozytorium nazywa się `householdbot` (także folder lokalny), a
   rozwiązanie HouseholdBot.

Podjęte w Etapie 4 (14.11.2026), na podstawie kryteriów, bez osobnego pytania:

8. Drugi pakiet krajowy: GB (Anglia i Walia). Powody: angielski jest językiem
   domyślnym narzędzia, źródła urzędowe są po angielsku i łatwe do cytowania
   (legislation.gov.uk, gov.uk), a angielski system terminów (dni zastępcze,
   „beginning with”) sprawdza ogólność silnika. Szkocja i Irlandia Północna są
   poza zakresem pakietu.
9. Wersja 1.0.0-rc.1 do czasu pilotażu i publikacji; 1.0.0 po nich.

Podjęte 14.11.2026 razem z planem Etapów 5 i 6:

10. Dwa kolejne etapy w dwóch sesjach, z pilotażem pomiędzy nimi. Wersja
    1.0.0 zamyka Etap 6, gdy pilotaż zakończył się bez błędów blokujących.
11. Projekt nie dostarcza własnego środowiska agenta ani wyboru modeli
    (LiteLLM, OpenRouter i podobne). Model wybiera gospodarz; „dowolny
    model” jest osiągany przez gospodarzy czytających Agent Skills oraz
    przez serwer MCP.
12. Serwer MCP działa wyłącznie lokalnie (stdio). Bez usługi hostowanej i
    bez zdalnego adresu: rekord pozostaje w folderze gospodarstwa.
13. Zapis egzekwują skrypty w dwóch fazach; hook dodaje potwierdzenie
    przez człowieka tam, gdzie gospodarz ma hooki.
14. Nadal poza zakresem: logowanie do banku, płacenie oraz wysyłanie pism
    i wiadomości w imieniu gospodarstwa.

Etap 2 wykonany 13.11.2026 na polecenie przejścia do niego przed pilotażem
Etapu 1; pilotaże obu etapów można przeprowadzić razem.

Otwarte, po Twojej stronie: „tak” dla każdego pushu, tagu i wydania; po
Etapie 5 pilotaż na wersji rc.4 według `docs/pilot.md` (z Cowork i
telefonem); przed Etapem 6 `codex login`, zgoda na zainstalowanie OpenCode
i OpenClaw na komputerze roboczym oraz wybór modeli dla OpenCode;
zgłoszenia do katalogów Claude i OpenAI; opcjonalnie sekret
`ANTHROPIC_API_KEY` dla testów z powłoką na Linuksie.
Jeśli „angielski domyślny” ma oznaczać angielski także wtedy, gdy
domownik bez profilu pisze po polsku, wystarczy zmiana jednej reguły (D14).
