# Plan implementacji

Stan: 2026-11-13, po Etapie 1 i Etapie 1.1 (dwujęzyczność). Dokument roboczy
po polsku. Narzędzie i dokumentacja są dwujęzyczne: angielski domyślnie,
polski do wyboru; dokumenty dla użytkowników mają wersje `.pl.md`, a
dokumenty dla programistów (CONTRIBUTING, CLAUDE.md, skille) są po angielsku.
Plan zostanie przetłumaczony na angielski jako wersja domyślna przed
publikacją w Etapie 4.

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

### Zasięg i rozszerzalność (Etap 4)

| Skill | Zadanie |
|---|---|
| `household-dashboard` | jednostronicowy widok całości |
| `build-skill` | powtarzalna czynność domowa zamieniona we własny skill |
| `pack-builder` | utworzenie i weryfikacja pakietu krajowego |

Do tego: cookbook `deadline-watcher`, drugi pakiet krajowy.

---

## 5. Struktura repozytorium (stan po Etapie 3)

```
.claude-plugin/marketplace.json        marketplace "householdbot"
.github/workflows/validate.yml         sync, walidator, testy, claude plugin validate
README.md QUICKSTART.md (+ .pl.md) CONNECTORS.md CONTRIBUTING.md CLAUDE.md
SECURITY.md CHANGELOG.md CODE_OF_CONDUCT.md NOTICE LICENSE .gitignore
docs/development-plan.md
core/                                  źródła wszystkiego, co trafia do skilli
  rules/*.md                           14 reguł wspólnych (Etap 2: money, voice; Etap 3: everyday)
  locale/PL.md PL.json                 pakiet krajowy
  i18n/en.json pl.json                 języki: daty, kwoty, odmiana, notatki, dziennik
  scripts/dates.py record.py           warstwa dowodowa
  scripts/statement.py                 wyciągi bankowe (Etap 2)
  scripts/chores.py                    podział obowiązków (Etap 3)
  money/categories.json                kategorie wydatków w dwóch językach (Etap 2)
  templates/en/ templates/pl/          profil, opis rejestrów w każdym języku
  vendor.json                          który skill dostaje które pakiety
scripts/sync.py validate.py make_icon.py
scripts/eval.py                        testy zachowania na kopii wtyczki w build/ (Etap 2.1)
tests/test_dates.py test_record.py test_statement.py test_chores.py
evals/<skill>/<przypadek>/case.yaml setup.sh [mocks/gmail/*.md]
evals/fixtures/make_household.py make_statement.py make_everyday.py seed.sh
householdbot/                          wtyczka
  .claude-plugin/plugin.json icon.png   .mcp.json   README(.pl).md   PRIVACY(.pl).md   LICENSE
  hooks/hooks.json
  agents/deadline-watcher.md document-reader.md
  skills/<skill>/SKILL.md reference/*.md
  skills/<skill>/shared/               kopie generowane (rules.md, locale/, i18n/, scripts/, templates/)
```

Liczba plików wtyczki: 147 po Etapie 1.1, 307 po Etapie 2 (z testami
zachowania w środku), 184 po Etapie 2.1, gdy testy wyszły poza paczkę. Przy 34
skillach prognoza to około 350 plików, poniżej limitu 512.

---

## 6. Strategia weryfikacji

| Poziom | Co sprawdza | Narzędzie | Kiedy |
|---|---|---|---|
| 1. Struktura | manifesty, frontmatter, samowystarczalność skilli, aktualność kopii, limity katalogu, uprawnienia agentów, kształt testów, pakiety krajowe, identyfikatory i sekrety w plikach | `scripts/validate.py`, `claude plugin validate --profile directory --strict` | po każdej zmianie, w CI |
| 2. Rachunek | święta, terminy, cofanie, pasma, cykliczność, rejestry, scalanie, archiwizacja | `python -m unittest` | po zmianie skryptu, w CI |
| 3. Zachowanie | wyzwalanie skilli, poprawność wyniku, zatrzymanie na bramce, odporność na wstrzyknięcie i oszustwa | `claude plugin eval` przez `scripts/eval.py` | w trakcie: pojedyncze przypadki; na zamknięciu etapu pełny przebieg |
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
- **Dokumentacja.** `docs/architecture.md` (analiza wzorca), plan po
  angielsku jako wersja domyślna i jego polskie tłumaczenie, polskie wersje
  dokumentów, które powstaną w Etapach 2 i 3.
- **Publikacja.** Publiczne repozytorium `householdbot` (adres już wpisany w
  `plugin.json` jako strona, repozytorium i polityka prywatności), wydanie z
  paczką budowaną w CI, zgłoszenie do katalogu wtyczek.

Kryteria akceptacji: sześć warunków z rozdziału 1.

Twój udział: test w Cowork i w aplikacji mobilnej, zgoda na publikację,
utworzenie repozytorium i zgłoszenie do katalogu z Twojego konta.

---

## 8. Stan po Etapach 1, 1.1, 2 i 3

**Wersja 0.3.0 (Etap 3, dom, rodzina i codzienność).**

| Poziom | Wynik |
|---|---|
| 1. Struktura | `scripts/validate.py` (nowe kontrole: zdarzenia życiowe wskazują istniejące okna, okresy przechowywania mają podstawę albo oznaczenie „sugerowany”): 0 błędów, 0 ostrzeżeń; `claude plugin validate --profile directory --strict`: przechodzi dla wtyczki i marketplace; 297 plików wtyczki z 512 |
| 2. Rachunek | 107 testów jednostkowych zielonych, w tym 14 dla `chores.py` (deterministyczność, równe obciążenie według udziału, próg wieku, stała osoba, co drugi tydzień, wyrównanie z poprzednich tygodni, zamiany, bilans), zdarzenie życiowe liczone z jednej daty, dokumenty po terminie przechowywania, `complete --from-done`, lista dokumentów danego typu, imię zatwierdzającego zamiast cytatu, wpis ze standardowego wejścia w UTF-8 |
| 3. Zachowanie | 101 przypadków (Sonnet, sędzia Sonnet, bez powłoki). Przebiegi pełne: 78/101 (0,92), 78/101 (0,93), końcowy 97/101, średnio 0,99, 15,18 USD; powtórki porażek po poprawkach opisane niżej |
| 4. Użycie | sesja `claude -p` ze skryptami (Windows), 8 tur na danych syntetycznych, około 4,50 USD: kupno używanego auta od osoby prywatnej (`dates.py event`: PCC-3 do czw. 26.11.2026, rejestracja do pon. 14.12.2026 z planem na pt. 11.12.2026), dwa przypomnienia zapisane po zgodzie Piotra; plan obowiązków na tydzień 2026-W47 policzony i zapisany przez `chores.py` po zgodzie Anny; jadłospis na 7 dni w budżecie (208 zł szacunkowo z rozpisaną sumą) zapisany do `lists/meals-2026-W47.md`, lista zakupów uzupełniona po osobnej zgodzie; przegląd papierów: rachunek z 2018 r. do zniszczenia i propozycje terminów przechowywania z podstawą; rekord i rejestr obowiązków bez błędów. Ujawniła jedną usterkę: imię zatwierdzającego zapisane razem z cytatem jego wiadomości (poprawione w `record.py`, test) |

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
| 4. Użycie | sesja `claude -p` ze skryptami (Windows): lista płatności 731,60 zł z progiem dwojga dorosłych i końcówką konta, pierwsza zgoda bez zapisu, „zapłaciłam” jako próba z drugą zgodą, zapis z „zgoda: Anna” i następne wystąpienia (woda do pt. 08.01.2027, cofnięte z soboty; prąd do czw. 17.12.2026); wcześniejsza sesja: wyciąg z zakresem i sumami zgodnymi z danymi testowymi, wypowiedzenie internetu (ostatni dzień pon. 23.11.2026, nadać do śr. 18.11.2026) z trzema wpisami po zgodzie; razem około 2 USD |

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
| Brak wariantu bezobsługowego | D11 | Etap 4 |
| Brak analizy wzorca jako rezultatu badawczego | `docs/architecture.md` | Etap 4 |
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
| Limit 512 plików przy 34 skillach | testy zachowania poza paczką (Etap 2.1): 184 pliki przy 18 skillach, prognoza około 350 przy 34; walidator ostrzega od 450 |
| Nazwa trafi do ręcznej oceny w katalogu | opis i README jasno mówią, czym jest wtyczka; wstrzymanie nie jest odrzuceniem |
| Rozrost zakresu przy 34 skillach | akceptacja etapu oparta na ścieżkach od początku do końca; minimalna poprzeczka skilla: SKILL.md, gotchas, trzy przypadki |
| Anthropic wyda własną wtyczkę domową | projekt jest otwarty i badawczy; wartością pozostają pakiety krajowe, warstwa dowodowa i analiza wzorca |
| Wersje językowe dokumentów rozjadą się | walidator wymaga polskiego odpowiednika i wzajemnych odnośników; CLAUDE.md nakazuje zmieniać oba pliki |
| Każdy kolejny skill wymaga treści w dwóch językach | skille piszemy po angielsku (model odpowiada w języku gospodarstwa); w dwóch językach są tylko stałe teksty, szablony i dokumenty dla użytkowników |

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

Etap 2 wykonany 13.11.2026 na polecenie przejścia do niego przed pilotażem
Etapu 1; pilotaże obu etapów można przeprowadzić razem.

Otwarte: brak decyzji blokujących Etap 3. Jeśli „angielski domyślny” ma oznaczać angielski także
wtedy, gdy domownik bez profilu pisze po polsku, wystarczy zmiana jednej
reguły (D14).
