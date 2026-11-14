# Szybki start

[English](QUICKSTART.md) · **Polski**

Od instalacji do pierwszego zarchiwizowanego dokumentu mija około dziesięciu
minut.

## 1. Instalacja

**Claude Code** (terminal lub IDE)

```
/plugin marketplace add dithiothreitol/householdbot
/plugin install householdbot@householdbot
```

Działa też lokalna kopia tego repozytorium: wystarczy podać jej ścieżkę w
`/plugin marketplace add`.

**Aplikacja Claude na komputer, karta Code**: w sesji lokalnej wybierz
**+ > Add plugins** i dodaj ten sam marketplace.

**Cowork (aplikacja Claude na komputer)**: dodaj marketplace w **Customize >
Plugins** albo pobierz `householdbot.plugin` z najnowszego wydania i wybierz
**Upload plugin**. Udostępnij sesji folder, w którym mają leżeć domowe
dokumenty.

**claude.ai (przeglądarka)**: zainstaluj wtyczkę na swoim koncie albo wgraj
pojedyncze skille z wydania (`skills/<skill>.zip`) w ustawieniach skilli i
włącz wykonywanie kodu, dzięki któremu działają skrypty. Czat nie otwiera
folderów na komputerze, dlatego folder gospodarstwa najlepiej trzymać na
podłączonym Dysku Google; drugą możliwością jest samodzielne zapisywanie
plików, które przygotowuje HouseholdBot.

**Telefon**: na telefonie nie instaluje się wtyczek. Remote Control pozwala
sterować z telefonu sesją Claude Code na komputerze, w której wtyczka jest
zainstalowana.

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
| „co trzeba zapłacić” | lista płatności z sumą; płacisz sam, potem piszesz „zapłaciłem” |
| wyciąg z banku (CSV) | miesiąc na jednej stronie: wpływy, wydatki, kategorie, podwyżki |
| „odpowiedz na pismo” / „wypowiedz umowę” | szkic w języku adresata, data nadania, nic nie zostaje wysłane |
| „przegląd miesiąca” | poczta, dokumenty, rachunki, następny miesiąc i pieniądze za jednym razem |
| „kupiliśmy auto” / „przeprowadzamy się” | każdy krok ustawowy z datą, każdy z osobną zgodą |
| „jadłospis na tydzień” / „dopisz mleko” | posiłki na tydzień i jedna lista zakupów według sklepów |
| „podział obowiązków na ten tydzień” | sprawiedliwy plan według udziału i wieku; zatwierdza dorosły |
| „co nas czeka w tym tygodniu” | kalendarze rodziny obok siebie, kolizje nazwane wprost |
| „co można wyrzucić z papierów” | dokumenty po terminie przechowywania; niszczysz sam, nic nie jest usuwane za Ciebie |
| „od teraz po angielsku” | zmiana języka gospodarstwa |
| „pulpit” / „stan wszystkiego” | jedna strona o całym gospodarstwie: terminy, pieniądze, dokumenty i to, czego rekord jeszcze nie obejmuje |
| „zrób z tego skill” | własny skill dla powtarzalnej czynności, zapisany po Twojej zgodzie |
| „zbuduj pakiet krajowy dla Niemiec” | pakiet ze źródeł urzędowych, sprawdzony i zapisany w Twoim folderze |

## Przegląd tygodnia według harmonogramu

- **Cowork**: utwórz cotygodniowe zadanie zaplanowane (Scheduled na pasku
  bocznym) z poleceniem „przegląd tygodnia”. Zadania zaplanowane korzystają z
  zainstalowanych wtyczek; zadanie, które potrzebuje folderu gospodarstwa na
  komputerze, działa tylko wtedy, gdy komputer jest włączony.
- **Aplikacja Claude na komputer, karta Code**: zadanie zaplanowane w folderze
  gospodarstwa działa, gdy aplikacja jest otwarta, a komputer nie śpi.
- **Bez włączonego komputera**: cookbook agenta zarządzanego
  (`managed-agent-cookbooks/deadline-watcher`) wykonuje cotygodniowy przegląd
  terminów na platformie Anthropic na kopii rejestrów. Jego README opisuje, co
  zostaje przesłane.
- **W pozostałych miejscach** nic nie uruchamia się samo: wystarczy w
  poniedziałek powiedzieć „przegląd tygodnia” albo pozwolić HouseholdBotowi
  wpisać terminy do kalendarza.

## Python

Cztery dołączone skrypty liczą daty, sprawdzają rejestry, sumują wyciągi
bankowe co do grosza i układają plan obowiązków. Claude Code i Cowork
uruchamiają je za pomocą Pythona 3, jeśli jest zainstalowany; claude.ai robi
to w swojej piaskownicy. Bez Pythona HouseholdBot stosuje te same zasady
samodzielnie i oznacza wyliczone daty słowem „verify” (do sprawdzenia).
