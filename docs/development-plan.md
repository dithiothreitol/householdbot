# Plan implementacji

Stan: 2026-11-13, po Etapie 1. Dokument roboczy po polsku. Dokumentacja
publiczna repozytorium (README, CONTRIBUTING, skille) jest po angielsku. Plan
zostanie przetłumaczony przed publikacją w Etapie 4.

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

| Powierzchnia | Zakres w v1.0 | Stan po Etapie 1 |
|---|---|---|
| Claude Code | pełny | zweryfikowane: instalacja z marketplace, sesja ze skryptami na Windows |
| Cowork (desktop) | pełny: pliki, skrypty, agenci | do testu w pilotażu |
| Czat web i telefon | skille i konektory; rekord przez konektor dysku | do testu w Etapie 4 |

**D7. Lokalizacja.** Rozmowa w języku gospodarstwa, nazwy pól i statusy po
angielsku. Pakiet krajowy to `core/locale/<CC>.md` (dla modelu) i
`<CC>.json` (dla skryptów). Identyfikatory reguł liczenia są wspólne dla
krajów (`administrative`, `tax`, `civil`, `court`, `calendar`). Każda reguła
prawna podaje akt, artykuł i źródło. Drugi pakiet w Etapie 4.

**D8. Konektory.** Poczta, kalendarz, magazyn dokumentów (adresy z wtyczki
small-business). Każdy skill działa bez konektorów.

**D9. Zakres v1.0: pełny.** Decyzja z 13.11.2026. Administracja domu oraz
codzienność: kalendarz rodziny, posiłki, zakupy, podział obowiązków (Etap 3).

**D10. Licencja i atrybucja.** Apache-2.0, `NOTICE` wskazuje źródła wzorca,
README zawiera zdanie o braku powiązania z Anthropic.

**D11. Proaktywność.** Harmonogram tylko tam, gdzie środowisko daje prawdziwe
zadania zaplanowane; w pozostałych przypadkach uczciwy zamiennik (wpis w
kalendarzu). Wariant bezobsługowy: cookbook agenta zarządzanego (Etap 4).

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

### Pieniądze i korespondencja (Etap 2)

| Skill | Zadanie |
|---|---|
| `inbox-triage` | poczta podzielona na: wymaga decyzji, do archiwum, załatwione; rachunki i pisma do `file-document` |
| `bills-due` | stos rachunków, lista płatności do wykonania przez domownika; dwie osobne zgody |
| `contract-check` | umowa lub oferta przed podpisem: okres, odnowienie, zmiany ceny, kary, prawo odstąpienia |
| `subscriptions-review` | koszty cykliczne: podwyżki, nieużywane, koniec promocji, daty wypowiedzenia |
| `budget-snapshot` | wyciąg bankowy: kategorie, obciążenia stałe, porównanie miesięcy |
| `tax-season-organizer` | komplet dokumentów do rozliczenia rocznego według pakietu krajowego; bez składania |
| `reply-to-letter` | odpowiedź, wyjaśnienie lub odwołanie na pismo; termin; projekt do wysłania przez domownika |
| `complaint-and-claim` | reklamacja, zwrot, gwarancja, szkoda: projekt, lista dowodów, termin odpowiedzi |
| `cancel-or-switch` | wypowiedzenie w formie wymaganej umową, data nadania, śledzenie potwierdzenia |
| łańcuch `monthly-review` | rachunki, nowe dokumenty, następny miesiąc, obraz wydatków |

### Dom, rodzina i codzienność (Etap 3)

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

Nowe elementy rekordu w Etapie 3: `registers/chores.json` (definicje
obowiązków i rotacji), folder `lists/` (zakupy, jadłospisy), skrypt
`chores.py` (rotacja i obciążenie domowników liczone deterministycznie).

### Zasięg i rozszerzalność (Etap 4)

| Skill | Zadanie |
|---|---|
| `household-dashboard` | jednostronicowy widok całości |
| `build-skill` | powtarzalna czynność domowa zamieniona we własny skill |
| `pack-builder` | utworzenie i weryfikacja pakietu krajowego |

Do tego: cookbook `deadline-watcher`, drugi pakiet krajowy.

---

## 5. Struktura repozytorium (stan po Etapie 1)

```
.claude-plugin/marketplace.json        marketplace "householdbot"
.github/workflows/validate.yml         sync, walidator, testy, claude plugin validate
README.md QUICKSTART.md CONNECTORS.md CONTRIBUTING.md CLAUDE.md
SECURITY.md CHANGELOG.md CODE_OF_CONDUCT.md NOTICE LICENSE .gitignore
docs/development-plan.md
core/                                  źródła wszystkiego, co trafia do skilli
  rules/*.md                           11 reguł wspólnych
  locale/PL.md PL.json                 pakiet krajowy
  scripts/dates.py record.py           warstwa dowodowa
  templates/                           profil, opis rejestrów
  vendor.json                          który skill dostaje które pakiety
scripts/sync.py validate.py make_icon.py
tests/test_dates.py test_record.py     testy jednostkowe
householdbot/                          wtyczka
  .claude-plugin/plugin.json icon.png   .mcp.json   README.md   PRIVACY.md   LICENSE
  hooks/hooks.json
  agents/deadline-watcher.md document-reader.md
  skills/<skill>/SKILL.md reference/*.md
  skills/<skill>/shared/               kopie generowane (rules.md, locale/, scripts/, templates/)
  evals/<skill>/<przypadek>/case.yaml setup.sh
  evals/fixtures/make_household.py seed.sh
```

Prognoza liczby plików: 8 skilli to 113 plików wtyczki. Przy 34 skillach
około 34 × 8 plików skilli i 110 przypadków testowych daje około 450 plików,
blisko limitu 512. Przegląd w Etapie 4 (patrz ryzyka).

---

## 6. Strategia weryfikacji

| Poziom | Co sprawdza | Narzędzie | Kiedy |
|---|---|---|---|
| 1. Struktura | manifesty, frontmatter, samowystarczalność skilli, aktualność kopii, limity katalogu, uprawnienia agentów, kształt testów, pakiety krajowe, identyfikatory i sekrety w plikach | `scripts/validate.py`, `claude plugin validate --profile directory --strict` | po każdej zmianie, w CI |
| 2. Rachunek | święta, terminy, cofanie, pasma, cykliczność, rejestry, scalanie, archiwizacja | `python -m unittest` | po zmianie skryptu, w CI |
| 3. Zachowanie | wyzwalanie skilli, poprawność wyniku, zatrzymanie na bramce, odporność na wstrzyknięcie i oszustwa | `claude plugin eval` | w trakcie: pojedyncze przypadki; na zamknięciu etapu pełny przebieg |
| 4. Użycie | pełna ścieżka wieloturowa, realne dokumenty | sesja `claude -p` na danych syntetycznych, pilotaż | po każdym etapie |

Ograniczenia ustalone w Etapie 1:

- Na Windows `claude plugin eval` nie przydziela powłoki (brak piaskownicy
  systemowej), więc testy zachowania sprawdzają tu wariant bez Pythona.
  Ścieżkę ze skryptami sprawdzają testy jednostkowe i sesja wieloturowa.
  Testy z powłoką w CI na Linuksie (Etap 4).
- Przypadki z zapisem po zgodzie wymagają historii rozmowy
  (`context.history_file`). Transkrypt z sesji lokalnej zawiera ścieżki
  użytkownika, więc takie przypadki powstaną w CI na Linuksie (Etap 4). Do
  tego czasu zapis po zgodzie sprawdza sesja wieloturowa.
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

Cztery etapy, każdy jako jedna sesja. Etapy 2 i 3 są od siebie niezależne.

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

### Etap 2. Pieniądze i korespondencja (wersja 0.2)

Zakres: dziewięć skilli i łańcuch `monthly-review` z rozdziału 4.
`statement.py` (rozbiór eksportu bankowego: separator, kodowanie, formaty
polskich banków, obciążenia cykliczne, sumy co do grosza). Reguły wspólne
`money` i `voice` (ton pism urzędowych). Rozszerzenie pakietu PL: dokumenty i
ulgi do rozliczenia rocznego, prawa konsumenta, forma i doręczenie
wypowiedzeń. Makiety konektora poczty (`evals/mocks/gmail/`). Przypadki
testowe: co najmniej 30.

Kryteria akceptacji:

- ścieżka: skrzynka, rachunek, lista płatności; dwie osobne zgody potwierdzone testem
- pismo urzędowe: poprawny termin z arytmetyką, projekt odpowiedzi nie zostaje wysłany
- wyciąg: sumy zgodne co do grosza z danymi testowymi; brak danych zgłaszany jako brak, nie jako zero
- wypowiedzenie: data nadania uwzględnia formę i czas doręczenia

Twój udział: eksport z własnego banku i dwa realne pisma w pilotażu.

### Etap 3. Dom, rodzina i codzienność (wersja 0.3)

Zakres: jedenaście skilli i łańcuchy `life-event`, `annual-review`.
`chores.py` i rejestr obowiązków. Listy kontrolne zdarzeń życiowych z
nakładką krajową. Rozszerzenie pakietu PL: obowiązki po kupnie i sprzedaży
pojazdu, terminy związane z dzieckiem, ważność skierowań i recept, zmiana
adresu. Rozszerzenie wywiadu startowego o część „codzienność” (opcjonalną).
Przypadki testowe: co najmniej 39.

Kryteria akceptacji:

- każde zdarzenie życiowe tworzy zobowiązania z datami i źródłem prawnym
- dane o zdrowiu i alergiach nie pojawiają się w przeglądzie ani we wpisie kalendarza (test)
- `emergency-file` nie zawiera żadnego identyfikatora ani hasła (test)
- rotacja obowiązków jest deterministyczna i równa w obciążeniu (testy jednostkowe)
- przegląd roczny proponuje usunięcia według retencji i niczego nie usuwa sam

Twój udział: pilotaż jednego zdarzenia życiowego, jadłospisu z listą zakupów
i przeglądu polis.

### Etap 4. Zasięg, utwardzenie, publikacja (wersja 1.0)

Zakres:

- **Powierzchnie.** Test macierzy z D6. Rekord na dysku przez konektor w
  czacie i na telefonie. Zadania zaplanowane tam, gdzie istnieją.
- **Rozszerzalność.** `household-dashboard`, `build-skill`, `pack-builder`,
  drugi pakiet krajowy, `docs/country-packs.md`.
- **Wariant bezobsługowy.** Cookbook `deadline-watcher` z trzema poziomami
  uprawnień i skryptem wdrożenia.
- **Utwardzenie.** Testy zachowania w CI na Linuksie z powłoką (ścieżka ze
  skryptami) i z historią rozmowy (zapis po zgodzie). Pełny przebieg z
  porównaniem bez wtyczki. Przegląd bezpieczeństwa. Poprawki z pilotaży.
  Przegląd liczby plików względem limitu 512.
- **Dokumentacja.** `docs/architecture.md` (analiza wzorca), tłumaczenie
  planu.
- **Publikacja.** Publiczne repozytorium `householdbot` (adres już wpisany w
  `plugin.json` jako strona, repozytorium i polityka prywatności), wydanie z
  paczką budowaną w CI, zgłoszenie do katalogu wtyczek.

Kryteria akceptacji: sześć warunków z rozdziału 1.

Twój udział: test w Cowork i w aplikacji mobilnej, zgoda na publikację,
utworzenie repozytorium i zgłoszenie do katalogu z Twojego konta.

---

## 8. Stan po Etapie 1

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
| Pakiet PL niezweryfikowany w źródłach | Etap 1 E | zamknięta; 2 punkty do ręcznego sprawdzenia (rozdział 8) |
| Brak testów zachowania i danych testowych | D12, 24 przypadki, generator | zamknięta dla rdzenia |
| Brak wersji schematu rejestrów | D3, `migrate` | zamknięta |
| Rosnący rejestr czytany w całości | `record.py due/find`, `archive` | zamknięta |
| Konflikty synchronizacji we wspólnym folderze | `conflicts`, `merge`, blokada zapisu | zamknięta |
| Brak reguły „brak danych to nie zero” | `absent-is-not-zero.md` | zamknięta |
| Brak sprawdzenia, czyja jest skrzynka i dysk | `storage-scope.md` | zamknięta |
| Odczyt niezaufanych dokumentów przez agenta z prawem zapisu | `document-reader` bez zapisu | zamknięta |
| Zakres ograniczony do dokumentów i terminów | rozdział 4, Etapy 2 i 3 | w planie |
| Brak `customize`, `find-document`, `doctor` | Etap 1 F | zamknięta |
| Pola retencji bez skilla, który ich używa | `annual-review` | Etap 3 |
| Brak wymogów katalogu w walidatorze | `validate.py`, `--profile directory` | zamknięta |
| Brak README i licencji w folderze wtyczki | Etap 1 A | zamknięta |
| Brak SECURITY, CHANGELOG, NOTICE, QUICKSTART | Etap 1 A | zamknięta |
| Brak wariantu bezobsługowego | D11 | Etap 4 |
| Brak analizy wzorca jako rezultatu badawczego | `docs/architecture.md` | Etap 4 |
| Brak wymaganej wersji Claude Code do testów | zaktualizowano do 2.1.323 | zamknięta |
| Identyfikator skopiowany do rejestru | `record.py validate`, `validate.py` | zamknięta (nowa) |
| Atrapa `python3` na Windows | wykrywanie interpretera w skillach i `seed.sh` | zamknięta (nowa) |

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
| Limit 512 plików przy 34 skillach | jeden `case.yaml` na przypadek; w Etapie 4 przegląd: mniej kopii na skill albo paczka wydania bez `evals/` |
| Nazwa trafi do ręcznej oceny w katalogu | opis i README jasno mówią, czym jest wtyczka; wstrzymanie nie jest odrzuceniem |
| Rozrost zakresu przy 34 skillach | akceptacja etapu oparta na ścieżkach od początku do końca; minimalna poprzeczka skilla: SKILL.md, gotchas, trzy przypadki |
| Anthropic wyda własną wtyczkę domową | projekt jest otwarty i badawczy; wartością pozostają pakiety krajowe, warstwa dowodowa i analiza wzorca |

---

## 11. Decyzje

Podjęte 13.11.2026:

1. Nazwa: `householdbot`.
2. Zakres: pełny, z codziennością (posiłki, zakupy, obowiązki, kalendarz rodziny) w Etapie 3.
3. Rejestry w JSON i skrypty jako warstwa dowodowa, zgodnie z wytycznymi Anthropic dla skilli.
4. Cztery etapy w czterech sesjach z pilotażem po każdym.

Otwarte: brak decyzji blokujących Etap 2. Etap 2 startuje po Twoim pilotażu
Etapu 1.
