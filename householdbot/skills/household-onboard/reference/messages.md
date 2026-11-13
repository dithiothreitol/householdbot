# Setup messages in English and Polish

Fixed texts for `household-onboard`, so both languages read the same way every
time. Use them as written, then continue in the chosen language. English is
the default.

## Language line (first line of the first reply)

Shown in both languages whatever the reply's language, so a member can switch
before anything else:

- When continuing in English:
  > Language: English. *Wolisz po polsku? Napisz „po polsku”.*
- When continuing in Polish:
  > Język: polski. *Prefer English? Say "in English".*

## Introduction

**English**

> **HouseholdBot keeps your household's papers in order:** it files letters,
> bills, contracts and policies, tracks deadlines and cancel-by dates, and
> briefs you on the week ahead. Nothing is written, sent or paid without your
> yes.
>
> **2 minutes** gets a working setup with sensible defaults. **15 minutes**
> adds your homes, vehicles, providers, decision rules and the reminders that
> fit your country.
>
> Quick or full? (You can upgrade later with `/householdbot:household-onboard --full`.)

**Polski**

> **HouseholdBot porządkuje papiery domowe:** archiwizuje listy, rachunki,
> umowy i polisy, pilnuje terminów płatności i wypowiedzeń oraz przygotowuje
> przegląd nadchodzącego tygodnia. Niczego nie zapisuje, nie wysyła i nie
> płaci bez Twojej zgody.
>
> **2 minuty** dają działającą konfigurację z ustawieniami domyślnymi.
> **15 minut** obejmuje też domy, pojazdy, dostawców, zasady decyzji i
> przypomnienia właściwe dla Twojego kraju.
>
> Szybka czy pełna? (Pełną można uruchomić później poleceniem `/householdbot:household-onboard --full`.)

## Folder question

**English**

> Where should the household folder live? A folder in a synced drive (Google
> Drive, OneDrive, Dropbox, iCloud) lets both adults see the same record; a
> local folder stays on this computer. Nothing is created until you approve
> the profile.

**Polski**

> Gdzie ma być folder gospodarstwa? Folder na dysku synchronizowanym (Google
> Drive, OneDrive, Dropbox, iCloud) pozwala obojgu dorosłym widzieć ten sam
> rekord, a folder lokalny zostaje na tym komputerze. Nic nie powstaje, dopóki
> nie zatwierdzisz profilu.

## Approval question for the profile

**English**

> This is the profile I will write, together with the empty registers. Write
> it? (yes / change / no) And whose name should I record as approving?

**Polski**

> Taki profil zapiszę razem z pustymi rejestrami. Zapisać? (tak / zmień / nie)
> Czyje imię mam zapisać jako zatwierdzającego?

## Closing

**English**

> Your household record is ready in `<folder>`. Next: send the next paper
> ("file this"), or ask "what's due".

**Polski**

> Rekord gospodarstwa jest gotowy w `<folder>`. Dalej: wyślij kolejny dokument
> („zapisz to”) albo zapytaj „co mamy do zrobienia”.
