# Document types

One `type` per document. Pick the closest; use `other` with a clear title
rather than forcing a fit.

**Retention** is a default for tidiness, not a legal requirement. The
profile's *Documents kept for* rule overrides it, and a country pack may name
a statutory period. `permanent` means never proposed for disposal.

| `type` | Extract | Typical obligations | Default `keep_until` |
|---|---|---|---|
| `bill` | issuer, period covered, amount, due date, how it is paid, the payment account's last four digits only, meter readings if any, change against the previous bill | payment by due date; none if paid by direct debit (say so) | 6 years |
| `bank-statement` | bank, period, opening and closing balance | none | 6 years |
| `contract` | provider, service, start, minimum term, renewal mechanism, notice period and method, price, price-change clause | cancel-by before each renewal; end of a promotional price | end of contract + 6 years |
| `rental-agreement` | landlord or tenant, address, rent, deposit, term, notice period, who pays what | rent dates; notice date; deposit return | end of tenancy + 6 years |
| `insurance-policy` | insurer, what is covered, term, premium, payment dates, renewal mechanism, notice rule, excess | premium instalments; cancel-by or renewal with `lead_time_days` to compare offers | end of term + 6 years |
| `insurance-claim` | insurer, claim event, what is requested from the household, decision, amount | documents to supply; appeal window on a refusal | 10 years |
| `official-letter` | office, case reference by pointer, what it asks for, the instruction section on how and when to respond | response window from delivery | 6 years |
| `official-decision` | office, what was decided, effective date, appeal instruction | appeal window from delivery; any payment or action ordered | permanent |
| `tax-document` | tax year, kind (return, assessment, statement of income), amounts, payment or refund | filing date; payment dates; correction window | permanent for assessments and decisions; 6 years otherwise |
| `court-paper` | court, case reference by pointer, what it is, what is required, the instruction section | response or objection window; hearing date | permanent |
| `fine` | issuer, offence date, amount, payment window, how to contest | payment by; contest by | 6 years |
| `income-statement` | payer, period, gross, net, tax withheld | none; input for the tax return | 6 years |
| `benefit-decision` | body, benefit, amount, period, what must be reported or renewed | renewal application window; reporting duties | end of period + 6 years |
| `warranty-receipt` | seller, item, purchase date, price, warranty length and conditions | warranty end (`kind: expiry`) | warranty end + 1 year |
| `medical` | provider, date, kind (referral, result, prescription, discharge), validity of a referral or prescription | appointment; referral or prescription expiry | permanent |
| `school-notice` | school, child, what it is about, date, payment or consent required | payment by; consent by; event date | end of the school year |
| `identity-document` | kind, holder, expiry date (numbers by pointer only) | expiry with lead time from the country pack | until replaced |
| `vehicle-document` | vehicle, kind (registration, test certificate, sale contract), dates | next roadworthiness test; registration duties after a purchase or sale | while the vehicle is owned + 6 years |
| `property-document` | property, kind (deed, land register extract, mortgage, survey), parties, dates | mortgage instalments; rate-change dates | permanent |
| `suspicious-message` | the channel, the sender as shown, the ask quoted, the pattern it matches | none, ever | 1 year |
| `other` | whatever the document states | whatever it asks for | 6 years |

## Reading notes

- **A bill paid by direct debit** has no payment obligation. Record the amount
  and date as a fact, and flag a rise of more than 10% against the previous
  bill in the same series.
- **A contract's renewal clause** is often on the last page or in separate
  terms. If the terms were not supplied, say that the notice period is unknown
  rather than assuming one.
- **An instruction section** (how and when to respond, where to appeal; in
  Polish *pouczenie*) is the controlling text for the deadline. Quote it.
- **A reminder or final demand** belongs to the series of the original bill.
  Do not create a second payment obligation for the same debt.
- **A document about a child** is filed with the child in `concerns` and an
  adult as `owner` of any obligation.
- **Medical documents** are filed with a neutral title ("Clinic: referral,
  2026-11-04"); the diagnosis stays in the original.
