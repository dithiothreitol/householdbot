# Prywatność

[English](PRIVACY.md) · **Polski**

HouseholdBot składa się z instrukcji, dwóch lokalnych skryptów i listy
konektorów. Nie ma serwera, konta ani analityki.

## Gdzie trafiają dane gospodarstwa

- **Folder gospodarstwa.** Profil, rejestry, zarchiwizowane oryginały,
  przeglądy i dziennik zgód leżą w folderze wybranym przez gospodarstwo.
  HouseholdBot czyta i zapisuje wyłącznie tam, a poza tym jeden plik wskaźnika
  (`~/.claude/plugins/config/householdbot/location.md`) ze ścieżką do folderu.
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
kalendarza.

## Usuwanie danych

Usunięcie folderu gospodarstwa i pliku wskaźnika usuwa wszystko, co
HouseholdBot zapisał. Żadne inne miejsce nie przechowuje kopii utworzonej
przez wtyczkę.
