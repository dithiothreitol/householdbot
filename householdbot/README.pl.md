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

Agenci (Claude Code i Cowork): `deadline-watcher` według harmonogramu czyta
rejestr i przygotowuje raport, niczego nie zmieniając; `document-reader` czyta
stos dokumentów bez narzędzi zapisu i zwraca uporządkowany wyciąg.

## Start

1. Instalacja: w Claude Code `/plugin marketplace add <ścieżka lub repozytorium>`,
   a następnie `/plugin install householdbot@householdbot`. W Cowork dodajesz
   marketplace i instalujesz wtyczkę.
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
documents/<rok>/           zarchiwizowane oryginały
log/decisions.md           każda zatwierdzona zmiana: kiedy, kto, co
```

## Co wtyczka uruchamia, wysyła i pobiera

- **Uruchamia** dwa skrypty w Pythonie dołączone do skilli (`dates.py` liczy
  święta i terminy, `record.py` obsługuje rejestry). Korzystają wyłącznie z
  biblioteki standardowej. Czytają i zapisują pliki w folderze gospodarstwa
  oraz jeden plik wskaźnika w `~/.claude/plugins/config/householdbot/`. Bez
  Pythona skille stosują te same zasady samodzielnie i oznaczają wyliczone
  daty do sprawdzenia.
- **Wysyła** dane wyłącznie do usług podłączonych przez gospodarstwo, bo
  HouseholdBot nie ma żadnej własnej usługi. Podłączone konta Gmail, Kalendarza
  Google lub Dysku Google (`.mcp.json`) czytają dane na prośbę domownika, a
  zapisują (szkic, wpis w kalendarzu, plik) dopiero po zgodzie, na warunkach
  dostawcy.
- **Niczego nie pobiera** z internetu.

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
Dostępny pakiet: Polska (`PL`, przegląd 2026-11-13). Bez pakietu HouseholdBot
opiera się na tym, co podają dokumenty i domownicy.

## Prywatność

[Polityka prywatności](PRIVACY.pl.md) ([in English](PRIVACY.md)): dane
gospodarstwa zostają w jego folderze i w usługach, które samo podłączy.

## Licencja

Apache-2.0. HouseholdBot jest niezależnym projektem open source, niepowiązanym
z Anthropic i nieposiadającym jego rekomendacji.
