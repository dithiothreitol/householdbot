# Protokół pilotażu

[English](pilot.md) · **Polski**

Pilotaż to ostatni warunek wersji 1.0 (definicja ukończenia w
`development-plan.pl.md`, warunki 1 i 6): prawdziwe gospodarstwo przechodzi
pełną ścieżkę bez pomocy autora i nie zostaje żaden otwarty błąd blokujący.
Pilotaż odbywa się na wersji 1.0.0-rc.4, między Etapami 5 i 6.

## Przed pierwszą sesją

- **Prywatny folder poza tym repozytorium**, na przykład
  `Dokumenty/Gospodarstwo`. Prawdziwe dokumenty nigdy nie trafiają do
  repozytorium; `.gitignore` wyłapuje tylko część nazw folderów.
- **HouseholdBot 1.0.0-rc.4** zainstalowany z marketplace
  (`/plugin marketplace update householdbot`, potem `/plugin install
  householdbot@householdbot`). Wersję pokazuje `/plugin`.
- **Python 3.8 lub nowszy** w ścieżce PATH. Na Windows `python3` bywa
  atrapą ze Sklepu Microsoft, która niczego nie uruchamia; polecenie
  `python --version` musi odpowiedzieć.
- **Kopia folderu** (archiwum zip) przed każdą sesją, dzięki czemu każdą
  sesję da się cofnąć.
- **Ten plik i plik notatek** obok siebie. Notatki nie zawierają prawdziwych
  danych (zob. szablon niżej).

## Dwanaście scenariuszy

| # | Scenariusz | O co poprosić | Co sprawdzić |
|---|---|---|---|
| 1 | Konfiguracja | „skonfiguruj HouseholdBota”, szybka konfiguracja | rekord powstaje jednym commitem po jednym „tak”; okno gospodarza pokazuje zmianę |
| 2 | Trzy zapisane dokumenty | rachunek, polisa, pismo urzędowe | każdy pokazany w podglądzie i zapisany po „tak”; zobowiązania z datami; oryginały w `documents/<rok>/` |
| 3 | Lista terminów | „co nas czeka?” | pasma, data planu i ostatni dzień, etykiety po polsku |
| 4 | Pismo urzędowe z terminem | pismo i „do kiedy?” | ostatni dzień z artykułem i data planu, każda sprawdzona przez `dates.py window` albo w ustawie |
| 5 | Wyciąg bankowy | plik CSV z Twojego banku | numery kont zamaskowane; sumy zgodne z wyciągiem |
| 6 | Szkic wypowiedzenia | „wypowiedz umowę na internet” | tylko szkic; nic nie zostaje wysłane |
| 7 | Przegląd tygodnia | „przegląd tygodnia” | dwie kolumny dat; zapis przez `record.py save` dopiero po „tak” |
| 8 | Pulpit | „strona na lodówkę” | nic, czego nie powiesisz na widoku; HTML drukuje się na A4 |
| 9 | Przypomnienia w telefonie | „zrób plik do kalendarza” | plik `.ics` się importuje; po zmianie i nowym eksporcie wydarzenia się aktualizują, a nie dublują |
| 10 | Zdarzenie życiowe | przeprowadzka, samochód, narodziny, nowa praca, jeśli coś takiego nastąpiło | kroki z datami i przepisami; nic nie zostaje zapisane bez „tak”; gdy nic nie pasuje, pominięcie z notatką |
| 11 | Cowork z zaplanowanym przeglądem | cotygodniowe zadanie zaplanowane | przebieg czyta i raportuje; rekord pozostaje bez zmian |
| 12 | Telefon przez Remote Control | „co dziś do zrobienia” z telefonu | odpowiedź pochodzi z rekordu na komputerze |

## Mierniki

| Miernik | Cel | Jak mierzyć |
|---|---|---|
| Zapisy bez zgody | 0 | każda linia w `log/decisions.md` odpowiada Twojemu „tak”; w `registers/.history/` nie ma niczego nieoczekiwanego |
| Błędne daty | 0 | każda wyliczona data sprawdzona przez `dates.py` albo w źródłowej ustawie |
| Minuty do pierwszego przeglądu tygodnia | zapisane | od instalacji do pierwszego przeglądu |
| Poprawki na scenariusz | zapisane | ile razy poprawiasz odpowiedź |
| Okna gospodarza pokazujące właściwą zmianę | wszystkie | okno przed każdym commitem zgadza się z tym, co zatwierdzasz |

## Błędy

**Blokujące:** zapis bez zgody, błędny ostatni dzień, zapisany
identyfikator, utracony albo nadpisany dokument, awaria, która przerywa
scenariusz. Każdy zostaje odtworzony na danych syntetycznych i poprawiony
przed wersją 1.0 (Etap 6, część A).

**Nieblokujące:** sformułowania, zbędne pytanie, wolne działanie,
formatowanie. Każdy zostaje zapisany i poprawiony, gdy poprawka jest tania.

## Szablon notatek

Notatki opisują przebieg własnymi słowami. Nigdy nie zawierają imienia,
adresu, numeru, kwoty ani sygnatury z prawdziwego dokumentu, a zrzut ekranu
pokazuje wyłącznie dane syntetyczne.

```
Scenariusz: 4 · pismo urzędowe z terminem
Data: <dzień> · Gospodarz: Claude Code <wersja> · Model: <model>
O co poprosiłem (własnymi słowami, bez prawdziwych danych):
Co się stało:
Czego oczekiwałem:
Blokujący: tak / nie
Moje poprawki:
```

## Koniec pilotażu

Wszystkie dwanaście scenariuszy zostało przeprowadzonych (scenariusz, który
nie pasuje, zostaje pominięty z notatką), nie ma otwartego błędu
blokującego, a mierniki są zapisane. Notatki trafiają do autora w postaci z
szablonu, jako wiadomość prywatna albo zgłoszenie; rozpoczynają Etap 6.
