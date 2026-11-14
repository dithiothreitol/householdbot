# HouseholdBot

[English](README.md) · **Polski**

HouseholdBot to wtyczka do Claude, która prowadzi domowe sprawy papierowe w
zwykłej rozmowie. Czyta listy, rachunki, umowy i polisy, archiwizuje je w
folderze należącym do gospodarstwa, pilnuje każdego terminu, odnowienia i
daty wypowiedzenia z uwzględnieniem świąt w danym kraju, a na początek
tygodnia przygotowuje krótki przegląd. Niczego nie zapisuje, nie wysyła i nie
płaci bez zgody domownika.

## Skille

| Skill | Przykładowe polecenie |
|---|---|
| `household-onboard` | „skonfiguruj nas”, „zacznijmy” |
| `household-router` | „pomóż mi ogarnąć papiery”, „co potrafisz” |
| `file-document` | „przyszło pismo”, „zapisz to”, „czy ta wiadomość jest prawdziwa?” |
| `find-document` | „gdzie jest polisa na samochód?”, „co umowa mówi o wypowiedzeniu?” |
| `deadline-tracker` | „co mamy do zapłacenia”, „zapłaciłam”, „dostałem to we wtorek, ile mam czasu?” |
| `weekly-brief` | „przegląd tygodnia”, „co nas czeka w tym tygodniu” |
| `household-customize` | „sprzedaliśmy samochód”, „dodaj domownika”, „przejdź na polski” |
| `household-doctor` | „sprawdź rekord”, „dysk zrobił drugą kopię pliku” |
| `inbox-triage` | „przejrzyj pocztę”, „co przyszło mailem” |
| `bills-due` | „co trzeba zapłacić”, „zapłaciłem te rachunki” |
| `contract-check` | „sprawdź umowę przed podpisaniem” |
| `subscriptions-review` | „jakie mamy abonamenty”, „Netflix podrożał” |
| `budget-snapshot` | wyciąg z banku, „na co idą pieniądze” |
| `tax-season-organizer` | „pomóż z rozliczeniem PIT” |
| `reply-to-letter` | „odpowiedz na pismo”, „napisz odwołanie” |
| `complaint-and-claim` | „reklamacja”, „chcę zwrócić towar”, „odszkodowanie” |
| `cancel-or-switch` | „wypowiedz umowę”, „zmiana operatora” |
| `monthly-review` | „przegląd miesiąca” |
| `home-upkeep` | „przegląd kominiarski”, „czy pralka ma jeszcze gwarancję”, „porównaj oferty” |
| `vehicle-file` | „kiedy badanie techniczne”, „dostałem mandat” |
| `insurance-overview` | „jakie mamy ubezpieczenia”, „czy nie płacimy podwójnie” |
| `identity-and-travel` | „czy dowód jest jeszcze ważny”, „czy jesteśmy gotowi do wyjazdu” |
| `school-desk` | „czego chce szkoła”, wklejona wiadomość z dziennika |
| `health-file` | „do kiedy ważne skierowanie”, „recepta ważna do” |
| `emergency-file` | „gdyby coś mi się stało” |
| `family-calendar` | „co nas czeka w tym tygodniu”, „kto odbiera Zosię” |
| `meal-planner` | „jadłospis na tydzień”, „co ugotować” |
| `shopping-list` | „dopisz mleko”, „co kupić w Lidlu” |
| `chore-rotation` | „podział obowiązków”, „kto dziś zmywa” |
| `life-event` | „przeprowadzka”, „urodziło się dziecko”, „kupiłem auto”, „zmarł tata” |
| `annual-review` | „przegląd roczny”, „co można wyrzucić” |
| `household-dashboard` | „pulpit”, „stan wszystkiego” |
| `build-skill` | „zrób z tego skill”, „chcę to robić jednym poleceniem” |
| `pack-builder` | „nie ma pakietu dla naszego kraju”, „sprawdź pakiet” |

Agenci (Claude Code i Cowork): `deadline-watcher` według harmonogramu czyta
rejestr i przygotowuje raport, mając wyłącznie narzędzia do odczytu;
`document-reader` czyta stos dokumentów bez narzędzi zapisu i zwraca
uporządkowany wyciąg.

## Start

1. Instalacja: w Claude Code `/plugin marketplace add dithiothreitol/householdbot`
   (albo ścieżka lokalnej kopii), a następnie
   `/plugin install householdbot@householdbot`. W Cowork dodajesz marketplace
   w Customize > Plugins albo wgrywasz `householdbot.plugin` z wydania. W
   OpenAI Codex: `codex plugin marketplace add dithiothreitol/householdbot`, a
   następnie `codex plugin add householdbot@householdbot`.
2. Uruchom `/householdbot:household-onboard`. Szybka konfiguracja trwa około
   dwóch minut i kończy się zarchiwizowaniem pierwszego prawdziwego dokumentu.
3. Od tej chwili wystarczy wysłać zdjęcie lub PDF dowolnego pisma albo zapytać
   „co mamy do zapłacenia”.

## Rekord gospodarstwa

Folder zwykłych plików w miejscu wybranym przez gospodarstwo, najlepiej na
dysku synchronizowanym, dzięki czemu dwoje dorosłych korzysta z niego bez
żadnego serwera:

```
household-profile.md       kto tu mieszka, co posiada i jak podejmuje decyzje
registers/documents.json   spis zarchiwizowanych dokumentów, każdy fakt ze stroną i cytatem
registers/obligations.json każdy termin, odnowienie i płatność wraz ze źródłem
registers/chores.json      obowiązki domowe, udziały i zapisane plany (gdy gospodarstwo z nich korzysta)
lists/                     lista zakupów, stałe produkty i jadłospis tygodnia
documents/<rok>/           zarchiwizowane oryginały
briefs/, reviews/          zapisane przeglądy i strony
exports/                   plik kalendarza dla telefonu
registers/.history/        poprzednia wersja każdego zmienionego pliku
registers/.pending/        podglądy czekające na „tak” (najwyżej 30 minut)
log/decisions.md           każda zatwierdzona zmiana: kiedy, kto, co
```

## Co wtyczka uruchamia, wysyła i pobiera

- **Uruchamia** cztery skrypty w Pythonie dołączone do skilli (`dates.py`
  liczy święta, terminy i zdarzenia życiowe, `record.py` obsługuje rejestry,
  `statement.py` czyta wyciągi bankowe przekazane przez gospodarstwo,
  `chores.py` układa sprawiedliwy plan obowiązków). Korzystają wyłącznie z
  biblioteki standardowej. Czytają i zapisują pliki w folderze gospodarstwa
  oraz jeden plik wskaźnika w `~/.claude/plugins/config/householdbot/` i
  odrzucają ścieżkę, która wyprowadza poza folder gospodarstwa. Tekst z
  dokumentów trafia do nich przez standardowe wejście, nigdy przez wiersz
  poleceń. Każdy zapis jest najpierw podglądem; `commit` wykonuje dokładnie
  pokazaną zmianę z imieniem zatwierdzającego. W Claude Code i Cowork hook
  wtyczki `PreToolUse` (`hooks/gate.py`, uruchamiany przez `hooks/gate.sh`
  ze znalezionym Pythonem) kieruje każdy commit i każdy bezpośredni zapis do
  folderu gospodarstwa do okna uprawnień gospodarza. `build-skill` zapisuje folder nowego skilla w `~/.claude/skills/`,
  gdy domownik zatwierdzi to miejsce. Bez Pythona skille stosują te same
  zasady samodzielnie i oznaczają wyliczone daty do sprawdzenia.
- **Wysyła** dane wyłącznie do usług podłączonych przez gospodarstwo, bo
  HouseholdBot nie ma żadnej własnej usługi. Podłączone konta Gmail, Kalendarza
  Google lub Dysku Google (`.mcp.json`) czytają dane na prośbę domownika, a
  zapisują (szkic, wpis w kalendarzu, plik) dopiero po zgodzie, na warunkach
  dostawcy. Szkice nigdy nie są wysyłane. HouseholdBot nie loguje się do banku
  i niczego nie płaci.
- **Pobiera:** skrypty nie wykonują żadnych zapytań do internetu.
  `pack-builder` prosi Claude o przeczytanie urzędowych stron z tekstami ustaw
  i informacjami administracji jego własnymi narzędziami sieciowymi, gdy sesja
  je ma, żeby zbudować pakiet krajowy.

## Języki

Domyślnym językiem jest angielski, drugim polski. Konfiguracja zaczyna się od
wyboru języka, a później zmienia go polecenie „po polsku” albo „in English”.
Od wybranego języka zależą odpowiedzi, przeglądy, zapis dat (`pt. 20.11.2026`
albo `Fri 20 Nov 2026`) i kwot (`1 240,00 zł` albo `PLN 1,240.00`), szablon
profilu i dziennik zgód. Dokumenty zachowują swój język: polskie pismo
zostaje objaśnione po angielsku dla gospodarstwa anglojęzycznego, z cytatem
oryginału, a odpowiedź do polskiego urzędu powstaje po polsku, z tłumaczeniem
na angielski.

## Kraje

Pakiety krajowe zawierają święta, zasady liczenia terminów, typowe terminy na
odpowiedź i obowiązki cykliczne, każdy z podstawą prawną i datą przeglądu.
Dostępne pakiety: Polska (`PL`, przegląd 2026-11-13) oraz Anglia i Walia
(`GB`, przegląd 2026-11-14). Dla innego kraju lub regionu `pack-builder`
buduje własny pakiet gospodarstwa ze źródeł urzędowych i zapisuje go w
folderze gospodarstwa. Bez pakietu HouseholdBot
opiera się na tym, co podają dokumenty i domownicy.

## Prywatność

[Polityka prywatności](PRIVACY.pl.md) ([in English](PRIVACY.md)): dane
gospodarstwa zostają w jego folderze i w usługach, które samo podłączy.

## Licencja

Apache-2.0. HouseholdBot jest niezależnym projektem open source, niepowiązanym
z Anthropic i nieposiadającym jego rekomendacji.
