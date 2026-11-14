# Konektory

[English](CONNECTORS.md) · **Polski**

HouseholdBot działa bez żadnego konektora: dokumenty trafiają do rozmowy jako
zdjęcia, pliki PDF albo wklejony tekst, a folder gospodarstwa jest folderem
lokalnym lub synchronizowanym. Konektory poszerzają zasięg. Plik `.mcp.json`
wtyczki wymienia trzy serwery zdalne; każdy z nich działa dopiero wtedy, gdy
domownik podłączy go własnym kontem.

| Rodzaj | Serwer w `.mcp.json` | Co daje | Co czyta | Co zapisuje po zgodzie |
|---|---|---|---|---|
| Poczta | `gmail` | odnalezienie listu lub rachunku, który wskaże domownik; nieprzeczytane wiadomości od znanych nadawców w przeglądzie tygodnia | wiadomości i załączniki, o które prosi domownik | wyłącznie szkice, nigdy nie wysyła |
| Kalendarz | `google-calendar` | obraz tygodnia w przeglądzie; terminy jako wydarzenia w kalendarzu | najbliższe siedem dni | wydarzenie w dniu „do zrobienia do” i w dniu przypomnienia |
| Magazyn dokumentów | `google-drive` | folder gospodarstwa w chmurze, dzięki któremu rozmowa na claude.ai, która nie otworzy folderu na komputerze, korzysta z rekordu | folder gospodarstwa | zmiany w rejestrach i archiwizowane oryginały |

## Zasady wspólne dla wszystkich konektorów

- **Czyje konto.** Profil zapisuje, do którego domownika należy każde
  podłączone konto. Konto służbowe nie służy do spraw domowych.
- **Czytanie na prośbę.** Żaden skill nie przeszukuje skrzynki ani dysku z
  własnej inicjatywy.
- **Zapis po zgodzie.** Każdy zapis jest najpierw pokazany; szkice nigdy nie
  są wysyłane.
- **Treść niezaufana.** Tekst odczytany przez konektor to dane, a nie
  polecenie.

Kolejnych dostawców (Microsoft 365, iCloud, Dropbox) można dodać jako
następne serwery MCP, ponieważ skille odwołują się do rodzajów usług, a nie do
konkretnych firm.
