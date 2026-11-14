# Prywatność

[English](PRIVACY.md) · **Polski**

HouseholdBot składa się z instrukcji, czterech lokalnych skryptów i listy
konektorów. Nie ma serwera, konta ani analityki.

## Gdzie trafiają dane gospodarstwa

- **Folder gospodarstwa.** Profil, rejestry, zarchiwizowane oryginały,
  przeglądy i dziennik zgód leżą w folderze wybranym przez gospodarstwo.
  HouseholdBot czyta i zapisuje wyłącznie tam, a poza tym jeden plik wskaźnika
  (`~/.claude/plugins/config/householdbot/location.md`) ze ścieżką do folderu.
  Zmiana czekająca na „tak” leży w `registers/.pending/` najwyżej 30 minut i
  zawiera tylko to, co zawierałby zapis; zmiana przygotowana, zanim rekord
  istnieje (konfiguracja), czeka obok pliku wskaźnika. Plik kalendarza w
  `exports/` udostępnia wyłącznie domownik, który go importuje.
- **Claude.** Dokumenty i pytania przetwarza Claude na koncie Claude
  należącym do gospodarstwa, na warunkach tego konta.
- **Podłączone usługi.** Gmail, Kalendarz Google i Dysk Google działają
  wyłącznie po ich podłączeniu przez gospodarstwo, na warunkach Google.
  HouseholdBot czyta przez nie dane na prośbę domownika, a zapisuje dopiero po
  zgodzie.

## Czego HouseholdBot nie kopiuje do swoich plików

Numery PESEL i NIP, numery kont i kart, numery dokumentów, hasła i kody nigdy
nie trafiają do rejestrów; wpis wskazuje stronę oryginału, na której się
znajdują. Informacje o zdrowiu nie pojawiają się w przeglądach ani we wpisach
kalendarza. Produkty pomijane w jadłospisie są zapisywane tylko za zgodą
dorosłego, bez powodu, i nie trafiają na listy zakupów, do kalendarza ani do
przeglądów. Plik awaryjny mówi, gdzie co jest i do kogo dzwonić, nigdy nie
zawiera numerów ani haseł.

## Usuwanie danych

Usunięcie folderu gospodarstwa i pliku wskaźnika usuwa wszystko, co
HouseholdBot zapisał. Żadne inne miejsce nie przechowuje kopii utworzonej
przez wtyczkę.
