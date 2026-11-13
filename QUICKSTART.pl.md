# Szybki start

[English](QUICKSTART.md) · **Polski**

Od instalacji do pierwszego zarchiwizowanego dokumentu mija około dziesięciu
minut.

## 1. Instalacja

**Claude Code**

```
/plugin marketplace add <ścieżka lub repozytorium GitHub z HouseholdBotem>
/plugin install householdbot@householdbot
```

**Cowork (aplikacja Claude na komputer)**: w ustawieniach wtyczek dodaj
marketplace, zainstaluj HouseholdBota i udostępnij sesji folder, w którym mają
leżeć domowe dokumenty.

**claude.ai i aplikacje mobilne**: skille działają w czacie, gdy wtyczka jest
zainstalowana na koncie, a wykonywanie kodu jest włączone. Czat nie otwiera
folderów na komputerze, dlatego folder gospodarstwa najlepiej trzymać na
podłączonym Dysku Google; drugą możliwością jest samodzielne zapisywanie
plików, które przygotowuje HouseholdBot.

## 2. Konfiguracja

```
/householdbot:household-onboard
```

Pierwsza linia pyta o język: domyślny jest angielski, a polecenie „po polsku”
przełącza rozmowę na polski. Potem wybierasz szybką konfigurację (około dwóch
minut): kraj, domowników i to, co zabiera najwięcej czasu. Następnie wskazujesz
miejsce na folder gospodarstwa; folder na dysku synchronizowanym pozwala
korzystać z niego dwojgu dorosłym. HouseholdBot pokazuje profil i tworzy folder
dopiero po Twojej zgodzie.

## 3. Pierwszy dokument

Wyślij zdjęcie lub PDF rachunku, polisy albo pisma, możesz też wkleić treść
maila. W odpowiedzi dostajesz opis dokumentu, najważniejsze fakty, termin, do
którego coś trzeba zrobić, i propozycję archiwizacji. Po Twojej zgodzie
dokument trafia do archiwum razem z terminem. Pismo w innym języku zostaje
objaśnione w Twoim języku, z cytatem oryginału.

## 4. Codzienne użycie

| Napisz | Co się dzieje |
|---|---|
| „co mamy do zapłacenia” | terminy według pilności, zaległe na początku |
| „zapłaciłam” | zamyka pozycję i przygotowuje następny miesiąc |
| „gdzie jest polisa na samochód” | dokument, fakt i strona |
| „dostałem to we wtorek, ile mam czasu?” | termin z uwzględnieniem świąt |
| „przegląd tygodnia” | jedna strona o nadchodzącym tygodniu |
| „sprzedaliśmy samochód” | zmiana w profilu i przypomnienia, które się zamykają |
| „sprawdź rekord” | kontrola stanu folderu |
| „od teraz po angielsku” | zmiana języka gospodarstwa |

## Python

Dwa dołączone skrypty liczą daty i sprawdzają rejestry. Claude Code i Cowork
uruchamiają je za pomocą Pythona 3, jeśli jest zainstalowany; claude.ai robi
to w swojej piaskownicy. Bez Pythona HouseholdBot stosuje te same zasady
samodzielnie i oznacza wyliczone daty słowem „verify” (do sprawdzenia).
