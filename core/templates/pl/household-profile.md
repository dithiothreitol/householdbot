<!--
TO JEST SZABLON.

Szablon jest częścią HouseholdBota i zmienia się przy każdej aktualizacji.
Dane gospodarstwa nigdy tu nie trafiają. `household-onboard` kopiuje tę
strukturę do folderu gospodarstwa jako `household-profile.md` i wypełnia ją
w trakcie wywiadu.

Zasady dla każdego skilla i agenta:
1. Folder gospodarstwa wskazuje reguła o rekordzie domowym; profil czytaj z
   `household-profile.md` w tym folderze, a nie z tego pliku.
2. `[PLACEHOLDER]` oznacza, że gospodarstwo jeszcze nie odpowiedziało. Skill,
   który potrzebuje tej wartości, pyta o nią raz i proponuje jej zapisanie.
3. `[DEFAULT]` oznacza wartość roboczą z szybkiej konfiguracji. Skill jej
   używa i mówi o niej, gdy wpływa na odpowiedź.
4. Linia zaczynająca się od `<!-- SETUP PAUSED AT:` oznacza przerwany wywiad.
   Skill proponuje wznowienie od tej sekcji.
5. Nagłówki odpowiadają jeden do jednego szablonowi angielskiemu
   (`../en/household-profile.md`): Gospodarstwo = Household, Domownicy =
   Members, Domy = Homes, Pojazdy = Vehicles, Dostawcy = Providers, Zasady
   decyzji = Decision rules, Podłączone narzędzia = Connected tools, Rytm =
   Rhythm, Pakiet krajowy = Country pack. Znaczniki `[PLACEHOLDER]` i
   `[DEFAULT]` zostają po angielsku w obu szablonach.
-->

# Profil gospodarstwa

*Plik powstaje w trakcie wywiadu konfiguracyjnego. Można go poprawiać ręcznie
w każdej chwili: każdy skill czyta go przed rozpoczęciem pracy, więc poprawka
tutaj działa wszędzie.*

---

## Gospodarstwo

- **Nazwa:** [PLACEHOLDER — krótka nazwa gospodarstwa, np. „Kowalscy, Radzymin”]
- **Kraj:** [PLACEHOLDER — dwuliterowy kod ISO 3166]
- **Język:** pl
- **Waluta:** [PLACEHOLDER — kod ISO 4217]
- **Strefa czasowa:** [PLACEHOLDER — nazwa IANA]
- **Data konfiguracji:** [PLACEHOLDER — RRRR-MM-DD]
- **Wersja profilu:** 1

**Co zabiera najwięcej czasu lub nerwów:** [PLACEHOLDER — słowami domowników]

---

## Domownicy

Tylko to, co potrzebne: imię lub określenie, rola, a rok urodzenia wyłącznie
przy dziecku, gdy od wieku zależą przypomnienia.

| Imię | Rola | Zajmuje się | Uwagi |
|---|---|---|---|
| [PLACEHOLDER] | dorosły | [PLACEHOLDER — np. podatki, samochód, ubezpieczenia] | |
| [PLACEHOLDER] | dorosły / dziecko | | |

---

## Domy

| Nazwa | Własność czy najem | Miejscowość | Ogrzewanie | Uwagi |
|---|---|---|---|---|
| [PLACEHOLDER — np. „Mieszkanie, Radzymin”] | [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER] | |

## Pojazdy

| Pojazd | Właściciel | Koniec okresu ubezpieczenia | Termin badania technicznego |
|---|---|---|---|
| [PLACEHOLDER — albo „brak”] | | | |

---

## Dostawcy

Tylko nazwy. Numery kont i numery klienta zostają w dokumentach.

| Kategoria | Dostawca | Sposób płatności | Uwagi |
|---|---|---|---|
| Bank | [PLACEHOLDER] | | |
| Prąd | [PLACEHOLDER] | | |
| Gaz / ogrzewanie | [PLACEHOLDER] | | |
| Woda / odpady | [PLACEHOLDER] | | |
| Internet / telewizja | [PLACEHOLDER] | | |
| Telefon komórkowy | [PLACEHOLDER] | | |
| Ubezpieczenie domu | [PLACEHOLDER] | | |
| Zdrowie | [PLACEHOLDER] | | |
| Szkoła / opieka nad dziećmi | [PLACEHOLDER] | | |

---

## Zasady decyzji

- **Próg zgody dwojga dorosłych:** [DEFAULT — brak; każdą kwotę zatwierdza jedna dorosła osoba]
- **Nigdy bez pytania:** [DEFAULT — płacenie, wysyłanie, podpisywanie, wypowiadanie, składanie pism]
- **Kto widzi przegląd tygodnia:** [DEFAULT — tylko dorośli]
- **Jak długo trzymamy dokumenty:** [DEFAULT — 6 lat, chyba że rodzaj dokumentu wymaga dłużej; dokumenty tożsamości, nieruchomości, sądowe i decyzje podatkowe bezterminowo]

---

## Podłączone narzędzia

| Kategoria | Stan | Czyje konto | Bez tego |
|---|---|---|---|
| Poczta | [PLACEHOLDER ✓ / ✗ / ⚪ niesprawdzone] | | Dokumenty przychodzą jako pliki, zdjęcia lub wklejony tekst |
| Kalendarz | [PLACEHOLDER ✓ / ✗ / ⚪ niesprawdzone] | | Terminy są w przeglądzie; bez propozycji wpisów w kalendarzu |
| Magazyn dokumentów | [PLACEHOLDER ✓ / ✗ / ⚪ niesprawdzone] | | Folder gospodarstwa jest lokalny lub na dysku synchronizowanym |

*Ponowne sprawdzenie: `/householdbot:household-onboard --check-integrations`*

---

## Rytm

- **Przegląd tygodnia:** [DEFAULT — na żądanie; wystarczy napisać „przegląd tygodnia”]
- **Harmonogram:** [DEFAULT — brak; nic nie uruchamia się bez prośby domownika]
- **Forma wyników:** [DEFAULT — krótka odpowiedź w rozmowie, przegląd zapisany jako plik Markdown w briefs/]

---

## Pakiet krajowy

- **Wczytany:** [PLACEHOLDER — np. „PL, przegląd 2026-11-13” albo „brak”]
- **Przyjęte przypomnienia ustawowe:** [PLACEHOLDER — lista potwierdzonych zobowiązań cyklicznych albo „na razie brak”]
