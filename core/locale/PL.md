# Country pack — Poland (PL)

**Reviewed:** 2026-11-13. **Language:** pl. **Currency:** PLN. **Time zone:** Europe/Warsaw.

Each line below is a reminder of a rule as understood at the review date.
Dates, amounts and procedures change. The letter in hand, its instruction
section (*pouczenie*), and the official source control. Everything taken from
this file reaches the household tagged `country pack rule — verify`.

---

## Public holidays

Fixed: 1 Jan, 6 Jan, 1 May, 3 May, 15 Aug, 1 Nov, 11 Nov, 24 Dec (from 2025),
25 Dec, 26 Dec.

Movable: Easter Sunday, Easter Monday, Pentecost Sunday (49 days after Easter),
Corpus Christi (the Thursday 60 days after Easter).

Every Sunday is also a day free from work.

Law: ustawa z 18.01.1951 o dniach wolnych od pracy, art. 1. The act of
6.12.2024 (Dz.U. 2024 poz. 1965) added 24 Dec from 1 Feb 2025. Saturday is not
a public holiday, but deadline rules treat it like one (below), and most
offices are closed.

## How deadlines are counted

| Area | Rule | Law |
|---|---|---|
| Administrative proceedings | The day of the event is not counted. A deadline ending on a public holiday, a Sunday or a Saturday ends on the next day that is none of these. | KPA art. 57 § 1 and § 4 |
| Tax proceedings | Same rule, unless a tax act says otherwise. | Ordynacja podatkowa art. 12 § 1 and § 5 |
| Civil law, contracts and civil court cases | A deadline in days ends with the last day; the starting day is not counted. A deadline in weeks, months or years ends on the day matching the starting day, or on the last day of the month when that month has no such day. If the end falls on a public holiday or a Saturday, it ends on the next day that is neither. Court deadlines are counted the same way. | Kodeks cywilny art. 111, 112, 115; KPC art. 165 § 1 |

These rules move a deadline forward. The plugin still plans to the rolled-back
`do_by` date (the dates rule).

## Deemed delivery

- **Registered letter from an office or a tax office, not collected.** The post
  office holds it for 14 days and leaves two notices. It counts as delivered on
  the last day of those 14 days, and the response window runs from then. Law:
  KPA art. 44; Ordynacja podatkowa art. 150.
- **Registered letter from a court, not collected.** Each of the two notices
  gives 7 days to collect it, counted from the day after the notice. The letter
  counts as delivered on the last day of the second period, usually 15 days
  after the first notice, and the response window runs from then. Law: KPC
  art. 139 § 1; court delivery regulation (Dz.U. 2024 poz. 19) § 6 to § 8;
  Supreme Court IV CKN 1026/00. When it is the first letter in a case against a
  private person, the court may ask the claimant to have it served through a
  bailiff (KPC art. 139¹ § 1). If the claimant shows in writing that the person
  lives at that address, the letter counts as delivered on the original date,
  and a later bailiff delivery does not restart the deadline (KPC art. 139¹
  § 3). An electronic payment order counts as delivered when the notices were
  left at the address in the PESEL register (KPC art. 505³⁴).
- **e-Doręczenia.** A message from a public body counts as delivered when it
  is opened. If it is not opened, it counts as delivered on the day after the
  14 days that start when it reaches the delivery box. Law: ustawa o
  doręczeniach elektronicznych art. 41 ust. 1 pkt 3 and art. 42. Offices send
  to the e-delivery address first when the person has one (KPA art. 39 § 1;
  Ordynacja podatkowa art. 144 § 1a).

A household that has not checked its post or its delivery box may already be
inside a response window. Ask when the letter actually arrived.

## Common response windows

The window printed on the document controls. These are the usual ones.

| Document | Window | Law |
|---|---|---|
| Appeal against an administrative decision | 14 days from delivery | KPA art. 129 § 2 |
| Appeal against a tax decision | 14 days from delivery | Ordynacja podatkowa art. 223 § 2 pkt 1 |
| Objection (*sprzeciw*) to a court payment order (*nakaz zapłaty*) from the ordinary or the electronic (e-sąd) payment-order procedure | 2 weeks from delivery in Poland | KPC art. 480² § 2 pkt 1, art. 505 § 1, art. 505²⁸ § 1 |
| Pleas (*zarzuty*) against a court payment order issued on documents such as a bill of exchange, an official document or a signed acknowledgement of the debt (*postępowanie nakazowe*) | 1 month from delivery in Poland or elsewhere in the EU | KPC art. 480² § 2 pkt 3, art. 493 § 1 |
| Paying a fine issued on a ticket (*mandat kredytowany*) | 7 days from accepting it | Kodeks postępowania w sprawach o wykroczenia art. 98 § 3 |
| Withdrawing from a distance or off-premises purchase | 14 days; 30 days for a contract made during an unarranged visit by the trader to the home or during an organised trip. For goods the days run from receiving them, otherwise from signing. Sending the notice in time is enough. | ustawa o prawach konsumenta art. 27, 28, 30 ust. 2 |
| Trader's reply to a consumer complaint | 14 days from receipt, otherwise treated as accepted, unless another law sets a different time | ustawa o prawach konsumenta art. 7a ust. 1 and 2 |

Court papers, enforcement notices and tax assessments get the one-line pointer
to a professional (the not-advice rule).

## Annual tax return (PIT)

### Information forms from payers

| Form | Who sends it | By when | Law |
|---|---|---|---|
| PIT-11 | An employer, or a payer of a contract of mandate (*umowa zlecenia*) or similar income | To the taxpayer by the end of February, to the tax office by the end of January, for the previous year | ustawa o PIT art. 39 ust. 1, art. 42 ust. 2 pkt 1, art. 42g ust. 1 |
| PIT-40A | A pension authority (*organ rentowy*), such as ZUS or KRUS, with the annual tax calculation for a pension | Same dates | art. 34 ust. 7, art. 42g ust. 1 |
| PIT-11A | A pension authority that does not make the annual calculation | Same dates | art. 34 ust. 8, art. 42g ust. 1 |
| PIT-8C | A broker or other payer of income taxed without withholding, such as capital gains | Same dates | art. 39 ust. 3, art. 42a ust. 1, art. 42g ust. 1 |

A deadline ending on a Saturday or a public holiday moves to the next working day (Ordynacja podatkowa art. 12 § 5).

Some pensioners need no return. This applies when the only income is on the PIT-40A, no reliefs are claimed and the person does not file jointly; the PIT-40A then settles the year (ustawa o PIT art. 34 ust. 9).

### Twój e-PIT

| Rule | Law |
|---|---|
| From 15 February the tax office prepares the return in e-Urząd Skarbowy from the payers' forms and the advances paid. podatki.gov.pl lists PIT-37, PIT-38, PIT-36, PIT-36L, PIT-28, the PIT-OP statement and the PIT-DZ information. | ustawa o PIT art. 45cd ust. 1 |
| Accepting it before the deadline, with or without changes, files it on the day of acceptance. | art. 45cd ust. 2 |
| If the taxpayer does nothing, the return counts as filed on 30 April. This applies only when all the taxpayer's income appears on the payers' forms. There is no automatic filing when a pension PIT-40A settles the year or when the taxpayer filed a return of their own. For PIT-28 (lump-sum tax), check podatki.gov.pl before relying on it. | art. 45cd ust. 4 and 5 |

### Filing together

| Who | Rule | Law |
|---|---|---|
| Spouses (*wspólne rozliczenie małżonków*) | Joint filing needs marriage for the whole year (or from the wedding to the year's end) and joint property. One spouse may make the request in the return for both. It also works when one spouse had no income. It is not available when either spouse uses the 19% business tax (art. 30c), the lump-sum tax (*ryczałt*) or tonnage tax. The lump-sum tax paid only on private rental (*najem prywatny*, ustawa o zryczałtowanym podatku dochodowym art. 6 ust. 1a) is the exception: it does not stand in the way of joint filing. | ustawa o PIT art. 6 ust. 2, 2a, 3 and 8 |
| Single parent (*osoba samotnie wychowująca dzieci*) | Open to an unmarried, widowed, divorced or separated parent, or one whose spouse lost parental rights or is in prison. The parent must raise alone a minor child, an adult child receiving care allowance or social pension, or a student under 25. The tax is twice the tax on half the income. It is not available when the parent raises a child together with the other parent, including alternating care with 800+ split between them. The same exclusions as for spouses apply to the parent and the child (the 19% business tax, the lump-sum tax other than on private rental, tonnage tax). | art. 6 ust. 4c, 4d, 4e, 4f and 8 |

### Common reliefs and exemptions, and the proof to keep

| Relief | Rule | Proof to keep | Law |
|---|---|---|---|
| Child relief (*ulga na dzieci*) | For each month of care, PLN 92.67 for each of the first two children, PLN 166.67 for the third and PLN 225 for the fourth and each next. With one child, the relief needs income up to PLN 112,000 (a married couple or a single parent) or PLN 56,000 (others). The part the tax cannot absorb is paid out, up to the social and health contributions. | Birth certificate, guardianship or foster-care ruling, school certificate for an adult child, shown on request | ustawa o PIT art. 27f ust. 1, 2, 5, 8 and 9 |
| Thermo-modernisation (*ulga termomodernizacyjna*) | For the owner of a single-family house, covering the listed materials, devices and services. The cap is PLN 53,000 per taxpayer in total. The project must end within 3 years from the end of the year of the first expense. Grant-funded parts are excluded, and an unused amount carries forward for up to 6 years. | VAT invoices from a seller registered for VAT and not exempt | art. 26h ust. 1 to 7 |
| Rehabilitation (*ulga rehabilitacyjna*) | Disability expenses listed in the act, such as home adaptation, equipment, rehabilitation stays and medicines above PLN 100 a month. Fixed amounts of up to PLN 2,280 a year each cover use of one's own car, a guide and an assistance dog. Only the part not reimbursed counts. | A disability certificate or pension decision, plus documents showing buyer, seller, item and amount; no receipts for the fixed amounts | art. 26 ust. 1 pkt 6, ust. 7 pkt 4, ust. 7a to 7d |
| Internet | Up to PLN 760 a year, in two consecutive years only, if never used before | An invoice or other document in the taxpayer's name | art. 26 ust. 1 pkt 6a, ust. 6h, ust. 7 pkt 4 |
| Donations (*darowizny*) | Public-benefit, religious and other listed purposes, together with blood donation up to 6% of income. Gifts to private persons do not count. The return shows the recipient's details. | A bank transfer confirmation for money; for goods, a document plus the recipient's acceptance | art. 26 ust. 1 pkt 9, ust. 5, ust. 6b, ust. 7 pkt 1 and 2 |
| Blood donation (*honorowe krwiodawstwo*) | Litres given free, times the compensation rate set by regulation, within the 6% limit | A certificate from the blood-collection centre | art. 26 ust. 1 pkt 9 lit. c, ust. 7 pkt 3 |
| IKZE pension account | Payments made in the year, up to the yearly limit under the IKE and IKZE act, deducted in the return | Payment confirmations | art. 26 ust. 1 pkt 2b, ust. 6g |
| Zero PIT for the young (*ulga dla młodych*) | Wages, contracts of mandate, graduate internships, student apprenticeships and maternity benefit received before turning 26 | The payer's PIT-11, which shows the exempt amount | art. 21 ust. 1 pkt 148; art. 39 ust. 1 |
| Zero PIT for returners (*ulga na powrót*) | The same kinds of income, plus business income, for 4 consecutive years after moving residence to Poland. The conditions are in ust. 43, among them no Polish residence in the 3 calendar years before the move. | Documents showing the conditions are met | art. 21 ust. 1 pkt 152, ust. 43 |
| Zero PIT for families with four or more children | The same kinds of income, for a parent raising at least four children | Birth certificates and similar, shown on request | art. 21 ust. 1 pkt 153, ust. 47 |
| Zero PIT for working seniors | Income from work, contracts of mandate, business or maternity benefit. It applies to a woman aged 60 or more or a man aged 65 or more who is entitled to a pension but does not draw it, and only when that income is subject to social insurance. | The payer's PIT-11 | art. 21 ust. 1 pkt 154 |
| Shared cap | The four zero-PIT exemptions together cover at most PLN 85,528 a year | | art. 21 ust. 44 |

### 1.5% for a public-benefit organisation (*1,5% podatku dla OPP*)

| Rule | Law |
|---|---|
| Name one organisation by its KRS number, in a return filed on time or in a correction filed within one month after the deadline. Up to 1.5% of the tax due is then sent to it between May and July. | ustawa o PIT art. 45c ust. 1, 3 and 4 |
| The tax must be paid in full within two months after the filing deadline. | art. 45c ust. 2 |
| A pensioner whose PIT-40A settles the year names the organisation in a statement by 30 April. Without a new statement, last year's choice is used again. | art. 45c ust. 3a and 3c |

### Correcting a return, refunds and keeping papers

| Topic | Rule | Law |
|---|---|---|
| Correcting a return (*korekta zeznania*) | File a corrected return. A written explanation is optional. From 1 Oct 2026 it is required when the correction shows an overpayment above PLN 10,000. No correction can be filed during a tax audit or tax proceedings, for the matters they cover. | Ordynacja podatkowa art. 81 § 1, 2, 2a and 2b; art. 81b § 1 pkt 1 |
| Time limit (*przedawnienie*) | The tax becomes time-barred 5 years after the end of the year in which it was due. For a return due on 30 April 2026, that is the end of 2031. | art. 70 § 1 |
| Refund of an overpayment (*nadpłata*) from a return | 45 days from filing an electronic PIT return, 3 months from filing a paper one | art. 77 § 1 pkt 5 and 5a |
| Refund after a correction filed by the 30 April deadline | 45 days from an electronic correction, 3 months from a paper one | art. 77 § 2 pkt 1 and 3 |
| Refund after a correction filed later, from 1 Oct 2026 | The correction itself opens the overpayment case. The refund comes within 2 months of filing it, but not earlier than 45 days or 3 months from the original return. Corrections filed before 1 Oct 2026 follow the earlier rules. | art. 77 § 1 pkt 6 lit. a, art. 165 § 8a; Dz.U. 2026 poz. 846 art. 22 |
| Keeping papers | Keep returns, the payers' forms and the proof for each relief until the tax is time-barred. The statutory duty to keep records for that time binds those who keep tax books, but the tax office can ask anyone for proof of a relief until then. | Ordynacja podatkowa art. 70 § 1, art. 86 § 1; ustawa o PIT art. 26 ust. 7, art. 27f ust. 5 |

## Consumer complaints, returns and claims

| Topic | Rule | Law |
|---|---|---|
| Goods not in line with the contract (*brak zgodności towaru z umową*) | The trader is liable for a lack of conformity that existed at delivery and shows up within 2 years, or longer if the stated shelf life is longer. A lack of conformity that shows up within those 2 years is presumed to have existed at delivery. | ustawa o prawach konsumenta art. 43c ust. 1 |
| Order of remedies | First repair or replacement, at the trader's cost and within a reasonable time; the trader collects the goods. A price reduction or withdrawal is possible when the trader refuses or fails, the problem persists, it is serious enough, or the trader clearly will not fix it. There is no withdrawal for an insignificant lack of conformity, and any lack of conformity is presumed significant. | art. 43d ust. 1 to 5, art. 43e ust. 1 and 4 |
| Money back | A price reduction is refunded within 14 days of the statement. After withdrawal, the price is refunded within 14 days of getting the goods back or proof of sending. The consumer may hold back payment until the trader acts. | art. 43e ust. 3 and 6, art. 43f |
| Digital content and services | Content supplied once carries 2 years' liability, with the presumption running for 1 year. Content supplied continuously carries liability for the whole supply period. The first remedy is bringing it into conformity. | art. 43l ust. 1 and 3, art. 43m |
| Trader's reply to a complaint (*reklamacja*) | 14 days from receipt, otherwise the complaint is accepted, unless another law says otherwise | art. 7a ust. 1 and 2 |
| Voluntary guarantee (*gwarancja*) | Comes on top of the statutory rights and does not limit them. It lasts 2 years from handing over the item unless the guarantee states another period. | Kodeks cywilny art. 577 § 4, art. 577¹ § 2 pkt 1 |
| After withdrawing from a distance or off-premises purchase | The trader refunds all payments, including standard delivery, within 14 days of receiving the statement, but may wait for the goods or proof of sending. The consumer returns the goods within 14 days of withdrawing (sending in time is enough) and pays only the direct return cost. | ustawa o prawach konsumenta art. 32 ust. 1 and 3, art. 34 ust. 1 and 2 |
| Insurance claim (*roszczenie z umowy ubezpieczenia*) | The insurer pays within 30 days of the notice of the event. If the facts cannot be established in time, it pays within 14 days of when they could be, and the undisputed part within the 30 days. Within 7 days of the notice it starts handling the claim and says which documents it needs. Any refusal or lower payment comes in writing, with reasons and the legal basis. | Kodeks cywilny art. 817 § 1 and 2; ustawa o działalności ubezpieczeniowej i reasekuracyjnej art. 29 ust. 1, 4 and 5 |
| Complaint to a bank, insurer or other financial firm | The firm replies on paper or electronically (art. 5 ust. 1) within 30 days of receipt, and sending in time is enough (art. 6). In particularly complex cases it may take up to 60 days if it explains why (art. 7). No reply in time means the complaint is accepted (art. 8). A reply accepting a claim names a payment date at most 30 days after the reply (art. 9 pkt 4). Disputes can go to the Financial Ombudsman (*Rzecznik Finansowy*, rf.gov.pl; art. 35). | ustawa o rozpatrywaniu reklamacji przez podmioty rynku finansowego art. 5 ust. 1, art. 6, 7, 8, 9 pkt 4, art. 35 |
| Complaint about a payment service (transfer, card, payment account) | Reply within 15 working days, or up to 35 in particularly complex cases with an explanation; sending in time is enough. The act says nothing about a missing reply; do not treat silence as acceptance. | ustawa o usługach płatniczych art. 15a ust. 2 to 4 |
| Telecom complaint (phone, internet, TV) | File within 12 months of the billing period with the outage, the faulty service or the wrong invoice. It can be in writing, oral, by phone or by email. No decision within 30 days means the complaint is accepted. After the complaint, the next step is court or out-of-court resolution by the President of UKE. | Prawo komunikacji elektronicznej art. 378 ust. 2, 3 and 5, art. 379 ust. 1, art. 383 |
| Energy or gas complaint | Billing complaints are answered within 14 days. A complaint about a disconnection notice, filed within 14 days of the notice, stops the disconnection until it is decided, and such a complaint not decided within 14 days counts as accepted. Disputes can go to the Coordinator for negotiations (*Koordynator do spraw negocjacji*) at the President of URE. | electricity system regulation (t.j. Dz.U. 2025 poz. 919) § 49 pkt 8; gas system regulation (t.j. Dz.U. 2025 poz. 1382) § 41 pkt 2; Prawo energetyczne art. 6c ust. 1 and 2, art. 31a |

## Giving notice: form and delivery

| Topic | Rule | Law |
|---|---|---|
| When a notice takes effect | When it reaches the other party so that they could read it. An electronic one takes effect when it enters their means of electronic communication that way. Allow time for delivery. | Kodeks cywilny art. 61 § 1 and 2 |
| Written form (*forma pisemna*) | A handwritten signature on the document; a qualified electronic signature counts the same | art. 78 § 1, art. 78¹ § 1 and 2 |
| Documentary form (*forma dokumentowa*) | Any document, such as an email or a scan, that shows who made the statement | art. 77² and 77³ |
| Ending a contract made in written, documentary or electronic form | Termination, withdrawal or ending by agreement needs documentary form only, unless a statute or the contract requires another form | art. 77 § 2 |
| OC: two policies at once | When an automatically renewed OC policy overlaps another OC policy, the renewed one can be ended by written notice. The insurer may charge only for the time it carried the risk. | ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 28a ust. 1 and 2 |
| OC: buying a used car | The seller's OC passes to the buyer and ends with its term without renewing. The buyer may end it earlier by written notice, from the date named (not before the notice) or else from the notice date. | art. 31 ust. 1 |
| Energy and gas | An open-ended contract can be ended at no cost. A fixed-term one can be ended too, but the contract may set costs or compensation. For a household these cannot exceed the seller's direct economic losses, and the contract must state how they are calculated. The contract ends on the last day of the month after the month the notice reached the company, or on a later date the household names. | Prawo energetyczne art. 4j ust. 3, 3a, 3b, 3c and 4 |
| Telecom | If the provider lets customers sign or change a contract in documentary form, it must also let them end it that way, for example by email. It confirms receipt within 1 working day. A consumer's fixed term is at most 24 months, and the provider must also offer a term of up to 12 months. The provider warns at least 30 days before an automatic renewal. A renewed contract can be ended at any time with one month's notice. Ending a fixed-term contract early costs at most the remaining subscription fees for the service and the remaining instalments for a subsidised device. | Prawo komunikacji elektronicznej art. 295 ust. 1 and 2, art. 301 ust. 1 and 2, art. 302 ust. 1 and 2, art. 304 ust. 1 and 3 |
| Renting a home (*najem lokalu*) | An open-ended lease with monthly rent can be ended with 3 months' notice to the end of a calendar month; also read the notice terms in the contract. A fixed-term lease can be ended early only in the cases the contract lists. A landlord may give a tenant notice only for the reasons in the tenant protection act, in writing and stating the reason. | Kodeks cywilny art. 673 § 1 and 3, art. 688; ustawa o ochronie praw lokatorów art. 11 ust. 1 |
| Closing a payment account | The holder may end the agreement at any time, with immediate effect unless the contract sets a notice period, which cannot exceed 1 month. There is no fee, except within 6 months of opening if the contract provides for one, capped at the bank's costs. | ustawa o usługach płatniczych art. 35 ust. 1, 3 and 4 |

## Paying

| Topic | Rule | Law |
|---|---|---|
| When a bank transfer counts as paid | A civil debt is paid when the creditor's account is credited, not when the household's account is debited, so send transfers early. Money is owed at the creditor's place. | Supreme Court I CSK 1094/14 (14.01.2016), following resolution III CZP 164/94 (4.01.1995); Kodeks cywilny art. 454 § 1 |
| Tax paid by bank transfer | Counts on the day the payer's account is debited | Ordynacja podatkowa art. 60 § 1 pkt 2 |
| Statutory late-payment interest (*odsetki ustawowe za opóźnienie*) | Due for any delay in paying money, even without loss. The rate is the NBP reference rate plus 5.5 percentage points unless another rate was agreed, and agreed late interest cannot exceed twice the statutory rate. The Minister of Justice publishes the rate in Monitor Polski. The latest notice on 2026-11-13 (M.P. 2026 poz. 367) gives 9.25% a year from 5 Mar 2026; check for a newer notice before using the rate. | Kodeks cywilny art. 481 § 1, 2, 2¹ and 2⁴ |

## Life events

Each table lists the statutory steps of one event. A step with a deadline
becomes an obligation with a `do_by` date (the dates rule); a step without one
becomes a task. The `life_events` list in PL.json carries the same steps.

### Buying a used car

| Step | Rule | Law |
|---|---|---|
| Documents at the sale | The seller hands over the registration certificate (*dowód rejestracyjny*) and, when it shows no current test date, the roadworthiness test certificate. The sale agreement or invoice is the proof of ownership for registration. | Prawo o ruchu drogowym art. 72 ust. 1 pkt 1, art. 78 ust. 1 |
| Compulsory insurance (OC) | The seller's OC passes to the buyer (see *Giving notice: form and delivery*). A buyer who ends it must have a new OC from the day the ended one stops. If the seller had no OC, the buyer takes out OC on the day of purchase, and before driving at the latest. | ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 31 ust. 1, 3 and 6 |
| Telling the insurer | A buyer who keeps the seller's OC owes the premium from the purchase date. The insurer may recalculate it from that date with the buyer's own discounts and surcharges, and must do so at the buyer's request. The buyer gives the insurer the facts it needs; no deadline is set. | art. 31 ust. 2, art. 32 ust. 4 |
| Registration (*rejestracja pojazdu*) | Apply to the starosta (vehicle registration office) for the buyer's place of residence within 30 days of buying, from a private person or from a dealer. A late application costs a fixed penalty of PLN 500, or PLN 1,000 when no application is made within 180 days. There is no duty when the buyer sells the car on within the 30 days. | Prawo o ruchu drogowym art. 73 ust. 1, art. 73aa ust. 1 pkt 1 and ust. 7, art. 140mb ust. 1 and 5 |
| Tax on civil-law transactions (*podatek od czynności cywilnoprawnych*, PCC), private seller | The buyer pays 2% of the car's market value: the average price of cars of the same kind, condition and wear on the day of purchase. The buyer files the PCC-3 declaration and pays within 14 days of the contract, at the tax office for the buyer's place of residence. The tax office can challenge a value below market. | ustawa o podatku od czynności cywilnoprawnych art. 1 ust. 1 pkt 1 lit. a, art. 3 ust. 1 pkt 1, art. 4 pkt 1, art. 6 ust. 1 pkt 1, ust. 2 and 3, art. 7 ust. 1 pkt 1 lit. a, art. 10 ust. 1, art. 12 ust. 1 pkt 2 |
| Low-value exemption | No PCC when the market value is PLN 3,000 or less, for contracts made from 3 Nov 2026. For earlier contracts the limit is PLN 1,000. | art. 9 pkt 6; Dz.U. 2026 poz. 1354 art. 3, 10 and 11 |
| Purchase from a business | No PCC when the seller sells as a VAT taxpayer, whether the sale is taxed with VAT or exempt from it. The tax follows the contract: a contract with a private seller is taxed even when a dealer arranged it. | art. 2 pkt 4 lit. a and b |

### Selling a car

| Step | Rule | Law |
|---|---|---|
| Hand-over | The seller gives the buyer the registration certificate, the test certificate when the registration certificate shows no current test date, and the OC confirmation. | Prawo o ruchu drogowym art. 78 ust. 1; ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 32 ust. 1 |
| Notice to the starosta (*zawiadomienie o zbyciu pojazdu*) | Within 30 days of the sale, to the starosta for the seller's place of residence, with a copy of the sale agreement or invoice. One co-owner's notice is enough. Late notice costs a fixed penalty of PLN 250. | Prawo o ruchu drogowym art. 78 ust. 2 pkt 1, ust. 2a and 2b, art. 140mb ust. 6; vehicle registration regulation (Dz.U. 2024 poz. 1709) § 15 ust. 1 |
| Notice to the OC insurer | In writing, within 14 days of the sale, with the buyer's name, address and PESEL. Until the insurer is told, the seller is jointly liable with the buyer for the premium from the sale date. Damage caused after the sale does not burden the seller. | ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 32 ust. 1 to 4 |
| Voluntary cover, such as AC | The rights pass to the buyer only with the insurer's consent, unless the policy terms say otherwise. Without that, the cover ends at the sale. | Kodeks cywilny art. 823 § 1 and 3 |
| Keeping the sale agreement | A copy goes with the notice to the starosta, and its date fixes when liability and the premium passed to the buyer. | vehicle registration regulation § 15 ust. 1; ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 32 ust. 3 and 4 |
| Income tax | A sale outside a business before 6 months have passed, counted from the end of the month in which the car was bought, is a source of taxable income for the annual return. | ustawa o PIT art. 10 ust. 1 pkt 8 lit. d |

### Moving house

| Step | Rule | Law |
|---|---|---|
| Registration of residence (*zameldowanie*) | Still a duty for Polish citizens. Register at the new address by the 30th day counted from arriving, at the municipal office or online. Registering at the new address can also deregister the old one (*wymeldowanie*). Registration only records where a person lives. The act's only penalty clause covers foreigners from outside the EU, the EEA and Switzerland. | ustawa o ewidencji ludności art. 24 ust. 1 and 2, art. 27 ust. 1, art. 28 ust. 1, 2e and 4, art. 33 ust. 1 and 3, art. 59 ust. 1 |
| Vehicle registration certificate | A new address is a change of the data in the registration certificate: tell the starosta within 30 days. When the registration office stays the same, it issues a new certificate; when the move changes the office, the new office registers the vehicle again. | Prawo o ruchu drogowym art. 78 ust. 2 pkt 2; vehicle registration regulation (Dz.U. 2024 poz. 1709) § 16 ust. 1 pkt 1 and 2 |
| Identity card | Cards issued under the act in force show no address, so a move needs no new card. A new card is needed when data shown on the card change. | ustawa o dowodach osobistych art. 12 ust. 1, art. 12a ust. 1, art. 46 ust. 1 pkt 2 |
| Driving licence | The licence pattern in force shows no address. Holders tell the starosta within 30 days of a change to data shown on the licence. | ustawa o kierujących pojazdami art. 18 ust. 1; driving licence pattern regulation (Dz.U. 2025 poz. 1072) annex 1 pt 2.1.4 |
| Tax office | A person whose tax identifier is the PESEL number (no business, or not registered for VAT) updates the address by giving it in the next tax return or other tax document, or on form ZAP-3. No deadline applies. From 1 Jan 2027 only a tax return or ZAP-3 counts. | ustawa o zasadach ewidencji i identyfikacji podatników i płatników art. 3 ust. 1 pkt 1, art. 9 ust. 1d; Dz.U. 2026 poz. 1270 art. 2 pkt 1 |
| 800+ | A person receiving 800+ tells ZUS on their PUE/eZUS profile within 7 days of a change to data given in the application; the application includes the address. | ustawa o pomocy państwa w wychowywaniu dzieci art. 13 ust. 3 pkt 1 lit. a, art. 20 ust. 1 |
| Property tax | A person who buys or sells a home or land files the property information (*informacja o nieruchomościach i obiektach budowlanych*) with the municipality within 14 days. | ustawa o podatkach i opłatach lokalnych art. 6 ust. 6 |
| Waste collection fee | The owner files the first fee declaration with the municipality within 14 days of the first resident moving in. When data behind the fee change, such as the number of residents, a new declaration is due by the 10th day of the following month. In a block of separately owned flats, the housing community or cooperative carries these duties. | ustawa o utrzymaniu czystości i porządku w gminach art. 2 ust. 3, art. 6m ust. 1, 1¹ and 2 |
| Insurers | When a policy requires reporting changes to facts the insurer asked about, such as the address, report them promptly. This does not apply to life insurance. | Kodeks cywilny art. 815 § 2 |

### Birth of a child

| Step | Rule | Law |
|---|---|---|
| Birth registration (*zgłoszenie urodzenia*) | Within 21 days of the birth card (*karta urodzenia*) being drawn up; 3 days for a stillbirth. The mother or father registers the birth at the civil registry office (*urząd stanu cywilnego*) for the place of birth, or online through gov.pl; a proxy may act at the office. If no one registers in time, the registrar draws up the birth certificate ex officio and chooses the name. | Prawo o aktach stanu cywilnego art. 14, art. 55 ust. 1 and 2, art. 56 ust. 2, art. 57 ust. 1 and 2, art. 58a ust. 1 |
| PESEL and registered residence | The registrar requests the PESEL number ex officio, and the child is registered at the parents' address on the day the birth certificate is drawn up. | ustawa o ewidencji ludności art. 16 ust. 1, art. 17 ust. 1 pkt 1, art. 29 |
| Health insurance | A parent registered for health insurance by someone else, such as an employer, tells that body about the child within 7 days so the child is registered as a family member. A child under 18 with Polish citizenship is entitled to publicly funded care in any case. | ustawa o świadczeniach opieki zdrowotnej finansowanych ze środków publicznych art. 2 ust. 1 pkt 3 lit. a, art. 67 ust. 3 |
| 800+ | Apply online (ZUS PUE/eZUS, online banking or the family ministry's service) within 3 months of the birth to receive it from the month of birth. A later application counts from its own month. | ustawa o pomocy państwa w wychowywaniu dzieci art. 13 ust. 5, art. 18 ust. 2 and 2a |
| *Becikowe* (*jednorazowa zapomoga z tytułu urodzenia się dziecka*) | PLN 1,000 per live-born child when family income is at most PLN 1,922 a person. The mother must have been under medical care from the 10th week of pregnancy at the latest until birth, shown by a doctor's or midwife's certificate. Apply to the municipality within 12 months of the birth; a later application is left unexamined. | ustawa o świadczeniach rodzinnych art. 3 pkt 11, art. 15b ust. 1, 2, 3, 5 and 6 |
| *Kosiniakowe* (*świadczenie rodzicielskie*) | PLN 1,000 a month for 52 weeks for one child (65 to 71 weeks for multiple births), when no parent receives maternity benefit. Apply to the municipality within 3 months of the birth to receive it from the month of birth. | art. 17c ust. 1, 3, 5 and 9 pkt 1, art. 24 ust. 9 |
| Maternity leave (*urlop macierzyński*) | 20 weeks for one child, 31 to 37 weeks for multiple births. Up to 6 weeks may be taken before the expected birth. | Kodeks pracy art. 180 § 1 and 2 |
| Supplementary maternity leave (*uzupełniający urlop macierzyński*) | For a premature or hospitalised baby, right after maternity leave: one week for each week the baby spends in hospital up to the 8th or the 15th week after birth, depending on the case. Request it at least 21 days before maternity leave ends. In force since 19 Mar 2025. | art. 180² § 1 and 4; Dz.U. 2024 poz. 1871 |
| Paternity leave (*urlop ojcowski*) | Up to 2 weeks, in one part or two parts of at least a week, before the child turns 12 months. Request it at least 7 days ahead. | art. 182³ § 1, 1¹ and 2 |
| Parental leave (*urlop rodzicielski*) | Up to 41 weeks for one child (43 for multiple births) for both parents together, 9 of them reserved for each parent. In up to 5 parts, until the end of the year in which the child turns 6. Request it at least 21 days ahead. | art. 182¹a § 1, 3 and 4, art. 182¹c, art. 182¹d § 1 |
| Maternity benefit (*zasiłek macierzyński*) | 100% of the benefit base for maternity and paternity leave, 70% for parental leave. A mother who applies in writing within 21 days of the birth receives 81.5% for maternity and parental leave together; the father's 9 reserved weeks stay at 70%. | ustawa o świadczeniach pieniężnych z ubezpieczenia społecznego w razie choroby i macierzyństwa art. 30a ust. 1, art. 31 ust. 1, 2, 3 and 3f |
| Check-ups and vaccinations | The check-up schedule (*bilanse zdrowia*) is in annex 1, part III, of the Minister of Health's regulation on guaranteed primary care services. The vaccination schedule (*Program Szczepień Ochronnych*) is announced each year by the Chief Sanitary Inspector, by 31 October for the next year, in the Minister of Health's official journal. | primary care regulation (t.j. Dz.U. 2023 poz. 1427) annex 1 part III; ustawa o zapobieganiu oraz zwalczaniu zakażeń i chorób zakaźnych u ludzi art. 17 ust. 11 |

### Changing job

| Step | Rule | Law |
|---|---|---|
| Work certificate (*świadectwo pracy*) | The employer issues it on the day the employment ends, unless a new contract with the same employer follows within 7 days. When that is not possible, the employer posts or delivers it within the next 7 days. It may not depend on settling accounts. | Kodeks pracy art. 97 § 1, 1¹ and 1³ |
| Correcting it | Ask the employer within 14 days of receiving it. After a refusal, go to the labour court within 14 days of being told; without any reply, the request goes to the court. | art. 97 § 2¹ |
| Certificate not issued | The employee may sue for it at any time before the claim is time-barred. | art. 97¹ § 1 and 3 |
| Tax-reducing amount in advances (PIT-2) | The new employer reduces monthly tax advances by the tax-reducing amount only after the employee's statement, at the latest from the month after it arrives. The former employer stops applying it when the job ends. Up to three payers may apply it, at 1/12, 1/24 or 1/36 each. | ustawa o PIT art. 31a ust. 2, 5 and 7, art. 31b ust. 1 to 3 |
| Employee capital plan (PPK) | The new employer enrols an employee under 55 no earlier than after 14 days and no later than the 10th day of the month after the month in which 3 months of employment pass; work for the same employer in the previous 12 months counts. From 55 to 69 only on request; from 70 there is no enrolment. The employee may opt out in writing before enrolment or later; contributions stop from the month of the declaration. Every 4 years, from 1 April, contributions restart unless the employee opts out again. | ustawa o pracowniczych planach kapitałowych art. 15 ust. 1 and 2, art. 16 ust. 1 and 2, art. 23 ust. 2, 4 and 6 |
| Other PPK accounts | Within 7 days of the new employer's PPK contract, the employee tells that employer about PPK accounts opened by earlier employers; the employer then explains the transfer request. | art. 19 ust. 1 and 2 |
| Health insurance | Cover ends 30 days after the insurance obligation ends, or later while sickness or maternity benefit is paid. | ustawa o świadczeniach opieki zdrowotnej finansowanych ze środków publicznych art. 67 ust. 4 and 6 |
| Registering as unemployed | The labour market act of 20 Mar 2025 replaced the 2004 act from 1 Jun 2025. Registration is at the county labour office (*powiatowy urząd pracy*). The benefit runs for each day from registration when the person had at least 365 days of work or similar periods, with pay or contributions based on at least the minimum wage, in the 18 months before. There is no benefit after resigning from the last job with notice, unless the reason was a move or termination under Kodeks pracy art. 55 § 1 or 1¹, or that job is not needed to qualify. After a termination by agreement it starts 90 days after registration, unless the reason was a move, the employer's insolvency or liquidation, or job cuts. A registered unemployed person has health insurance. | ustawa o rynku pracy i służbach zatrudnienia art. 218 ust. 1, art. 219 ust. 1 pkt 1 and ust. 2, art. 220 ust. 1 pkt 5 and ust. 2 pkt 3, art. 460; ustawa o świadczeniach opieki zdrowotnej art. 66 ust. 1 pkt 24 |

### Death of a close relative

| Step | Rule | Law |
|---|---|---|
| Death registration (*zgłoszenie zgonu*) | Within 3 days of the death card (*karta zgonu*) being drawn up, or within 24 hours of a death caused by an infectious disease, at the civil registry office for the place of death. The person entitled to bury makes it: the spouse, descendants, ascendants, side-line relatives up to the 4th degree, in-laws in the direct line of the 1st degree, or someone who voluntarily takes it on. | Prawo o aktach stanu cywilnego art. 13 ust. 2, art. 93 ust. 1 and 2; ustawa o cmentarzach i chowaniu zmarłych art. 10 ust. 1 |
| Funeral allowance (*zasiłek pogrzebowy*) | PLN 7,000 for a death from 1 Jan 2026 (PLN 4,000 before). It is due after the death of an insured person, a pensioner, a person who met the pension conditions, or a family member of an insured person or pensioner. A family member who paid for the funeral receives the full amount; another person receives the documented costs up to it; an employer, care home, municipality, county or church may also claim. The right expires without an application within 12 months of the death, or 12 months of the funeral when an earlier application was impossible for reasons beyond the claimant's control. Since 1 Jan 2026 ZUS pays in most cases without a decision, within 14 days of the last fact being clarified, and a funeral home may apply and receive it with the family's authorisation. The amount rises from 1 March when yearly inflation exceeds 5%; ZUS confirmed PLN 7,000 from 1 Mar 2026. KRUS pays the same amount. | ustawa o emeryturach i rentach z FUS art. 77 ust. 1 and 2, art. 78, art. 79 ust. 1, art. 80 ust. 1, 2 and 7, art. 81 ust. 1 and 2, art. 115 ust. 3a, art. 116 ust. 3a, art. 129 ust. 2a, art. 130 ust. 2c; Dz.U. 2025 poz. 718 art. 13 and 14; M.P. 2026 poz. 150; ustawa o ubezpieczeniu społecznym rolników art. 35 ust. 3 |
| Accepting or rejecting the inheritance (*przyjęcie lub odrzucenie spadku*) | A statement before a notary or a court within 6 months of the day the heir learned of their title to inherit. Filing the request with the court within that time is enough. When the statement needs a court's permission, the time stops while that case runs. No statement means acceptance with the benefit of inventory (*przyjęcie z dobrodziejstwem inwentarza*), which limits liability for the debts. | Kodeks cywilny art. 1012, art. 1015 § 1, 1¹, 1² and 2, art. 1018 § 3 |
| Confirming the heirs | A court decision (*stwierdzenie nabycia spadku*) or a notarial certificate of succession (*akt poświadczenia dziedziczenia*). Neither can be issued within 6 months of the death unless all known heirs have made their statements. | art. 1025 § 1, art. 1026 |
| Inheritance tax: closest family | A spouse, descendants, ascendants, stepchildren, siblings, stepfather and stepmother are exempt if they file SD-Z2 with the tax office within 6 months of the court decision becoming final or of the notarial certificate being registered. An heir who learned of the inheritance later has 6 months from learning. No filing is needed when everything received from the deceased, together with what came from them in that year and the 5 years before, is within PLN 36,120. | ustawa o podatku od spadków i darowizn art. 4a ust. 1 pkt 1, ust. 1a, 2 and 4 pkt 1, art. 9 ust. 1 pkt 1 |
| Missed SD-Z2 deadline | Since 7 Jan 2026 the deadline is restored on request when the heir shows it was missed without fault; the request is filed within 7 days of the cause ending, together with SD-Z2. Without restoration, the acquisition is taxed as for tax group I, and the tax return (SD-3) is due within a month of the missed deadline. | art. 4a ust. 3, art. 4c ust. 1, art. 17a ust. 1a; Ordynacja podatkowa art. 162 § 2; Dz.U. 2025 poz. 1854 |
| Inheritance tax: other heirs | When the share exceeds the heir's tax-free amount, the tax return (SD-3) is due within a month of the tax obligation. For decisions and certificates from 7 Jan 2026 the obligation arises when the court decision becomes final or the notarial certificate is registered. | art. 6 ust. 1 pkt 1, art. 9 ust. 1, art. 17a ust. 1; Dz.U. 2025 poz. 1854 art. 2 ust. 2 |
| Bank accounts | On the bills, the bank pays the funeral costs, within customary limits, from the deceased's savings and current accounts; this money is outside the estate. Money under a disposition on death (*dyspozycja wkładem na wypadek śmierci*) goes to the named spouse, ascendants, descendants or siblings, up to 20 times the average monthly enterprise-sector wage for the month before the death, also outside the estate; the bank tells those persons. A person with a legal title to the estate can get, through a bank, a summary of the deceased's accounts in all banks and credit unions. | Prawo bankowe art. 55 ust. 1 pkt 1 and ust. 2, art. 56 ust. 1, 2 and 5, art. 56a ust. 2, art. 92ba ust. 1 and 2, art. 92bc ust. 1 |
| Tax on a disposition on death | The money is subject to inheritance and gift tax. The tax obligation arises at the death, so the closest family file SD-Z2 within 6 months of the death, unless the PLN 36,120 limit applies. | ustawa o podatku od spadków i darowizn art. 1 ust. 2, art. 4a ust. 1 pkt 1 and ust. 4 pkt 1, art. 6 ust. 1 pkt 3 |
| 800+ after a parent's death | When the parent who received 800+ dies, the other parent who applies within 3 months receives it from the day of death, for months not yet paid. | ustawa o pomocy państwa w wychowywaniu dzieci art. 18 ust. 2b |
| The deceased's car | The heirs apply for registration within 60 days of the court decision becoming final or the notarial certificate being drawn up (30 days before 24 Dec 2025). The penalties for buyers apply. The deceased's OC passes to them. | Prawo o ruchu drogowym art. 73aa ust. 2, art. 140mb ust. 1 and 5; Dz.U. 2025 poz. 1734; ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 31 ust. 1 |
| Survivor's pension (*renta rodzinna*) | ZUS pays it on application. An application in the month of the death or the next month gets it from the day of death; a later one only from its own month. A widow or widower with their own pension may, under the conditions of art. 95a, choose combined payment (*renta wdowia*). | ustawa o emeryturach i rentach z FUS art. 65 ust. 1, art. 95a ust. 1 and 2, art. 129 ust. 1 and 2 |

## Recurring household obligations

Offer these when the profile shows they apply. Each becomes an obligation only
after the household confirms it.

| Applies when | Obligation | When | Law or source |
|---|---|---|---|
| Any adult with taxable income | Annual income tax return (PIT) | 15 Feb to 30 Apr for the previous year; a return sent earlier counts as filed on 15 Feb | ustawa o PIT art. 45 ust. 1 |
| Owns a home, land or a garage | Property tax, also farm and forest tax | Instalments by 15 Mar, 15 May, 15 Sep, 15 Nov; a yearly amount up to PLN 100 is paid once, by the first instalment date | ustawa o podatkach i opłatach lokalnych art. 6 ust. 7 and 11a; ustawa o podatku rolnym art. 6a ust. 6 and 10a; ustawa o podatku leśnym art. 6 ust. 3 and 7a |
| Owns a registered vehicle | Compulsory liability insurance (OC): the 12-month contract renews by itself unless the owner gives the insurer written notice no later than one day before the term ends; it does not renew if the premium for the ending term is unpaid | Cancel-by is the day before the term ends | ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 28 ust. 1 and ust. 2 pkt 1 |
| Owns a passenger car | Periodic roadworthiness test | First within 3 years of first registration, second within 5 years of first registration and at most 2 years after the first, then every year; a car running on gas is tested every year | Prawo o ruchu drogowym art. 81 ust. 6 |
| Has a child under 18 | 800+ child benefit application for the period 1 Jun to 31 May | Online only, from 1 Feb; an application filed by 30 Apr is decided and paid by 30 Jun; entitlement runs from the month of filing, so filing by 30 Jun keeps June | ustawa o pomocy państwa w wychowywaniu dzieci art. 13 ust. 5, art. 18 ust. 1 and 2, art. 21 ust. 3 and 4 |
| Has a radio or TV set registered | Broadcast licence fee (abonament RTV) | In advance, by the 25th day of each month; a payment for several months or the whole year is made by the 25th day of the first month it covers | ustawa o opłatach abonamentowych art. 3 ust. 4 |
| Any household | Waste collection fee | Dates set by the municipality; ask, or read the municipality's notice | ustawa o utrzymaniu czystości i porządku w gminach art. 6l ust. 1; uchwała rady gminy |
| Owns a house | Chimney flues (smoke, flue gas and ventilation) and gas installation check | At least once a year, single-family houses included | Prawo budowlane art. 62 ust. 1 pkt 1 lit. c and ust. 2 |
| Owns a house | Building condition check, including electrical and lightning protection | At least every 5 years | Prawo budowlane art. 62 ust. 1 pkt 2 |
| New heat source installed | Declaration to the central register of building emissions (CEEB) | Within 14 days of first use; a new declaration within 14 days of a change | ustawa o wspieraniu termomodernizacji i remontów oraz o centralnej ewidencji emisyjności budynków art. 27g ust. 1 and 4 |

## Documents with an expiry date

Register the expiry as an obligation with `kind: expiry` and a lead time.

| Document | Validity | Suggested lead time |
|---|---|---|
| Identity card (dowód osobisty) | 10 years; 5 years when issued to a child under 12 (ustawa o dowodach osobistych art. 7 ust. 1 and 2). A card issued before 2 Aug 2021 is valid until its printed date, but not after 3 Aug 2031 (Dz.U. 2021 poz. 1000, art. 4); for holders aged 70 or more, check the exception in Regulation (EU) 2019/1157 art. 5 — verify | 60 days |
| Passport | 10 years; 5 years when issued to a child under 12 (ustawa o dokumentach paszportowych art. 17 ust. 1 and 2) | 180 days, because many countries require 6 months of validity |
| Driving licence issued from 19 Jan 2013 | The date printed in field 4b: up to 15 years for categories AM, A1, A2, A, B1, B, B+E and T, and up to 5 years for C and D categories. A first category B licence issued from 4 Sep 2026 is valid only for the probation period: 2 years, or 3 years for a licence obtained at 17 but not past the 20th birthday. When it expires, the holder applies to the starosta for a new licence, which then follows the 15-year rule (ustawa o kierujących pojazdami art. 13 ust. 1, art. 91 ust. 1; Dz.U. 2025 poz. 1676 art. 9 ust. 1; Dz.U. 2025 poz. 1073 § 14 ust. 1 pkt 13 and § 15 ust. 3 pkt 10) | 60 days |
| Driving licence issued up to 18 Jan 2013 | Valid for its own period, but no longer than its exchange date; exchanges run from 19 Jan 2028 to 18 Jan 2033 on dates set by the transport minister (ustawa o kierujących pojazdami art. 124 ust. 4 and 6) | 60 days before the date set for it |
| European Health Insurance Card (EKUZ) | The date printed on the card, while the holder keeps NFZ cover | 30 days before travel |

## Health papers

| Topic | Rule | Law |
|---|---|---|
| Paper prescription (*recepta*) | Can be filled within 30 days of its issue date, or of the date it may be filled from (*realizacja od dnia*) when the prescriber wrote one. | Prawo farmaceutyczne art. 96a ust. 1 pkt 5, ust. 7 pkt 1 |
| E-prescription (*e-recepta*) | 30 days, as on paper, unless the prescriber marks a 365-day term. After the first 30 days the pharmacy dispenses only the days of use that remain, counted from the issue date or the "from" date. One collection gives at most 120 days of use; the next part can be collected after three quarters of that period has passed. | art. 96a ust. 7 pkt 1, ust. 7a and 7aa; prescriptions regulation (t.j. Dz.U. 2025 poz. 604) § 9 ust. 3 |
| Shorter and longer terms | Antibiotics for internal use or injection: 7 days from the issue or "from" date. Medicines and special foods imported for the patient, and immunological products made for the patient: 120 days from the issue date. Narcotic and psychotropic medicines: 30 days from the issue date. | art. 96a ust. 7 pkt 2 to 4 |
| Quantity on one prescription | A doctor may prescribe up to 360 days of use at once. A paper prescription covers at most 120 days, and up to 12 paper prescriptions may cover consecutive periods of 360 days in total. | art. 96a ust. 2 pkt 1, ust. 3 |
| Referral to a specialist (*skierowanie*) | NFZ-funded outpatient specialist care needs a referral from a health-insurance doctor (*lekarz ubezpieczenia zdrowotnego*). No referral is needed for a gynaecologist, dentist, venereologist, oncologist or psychiatrist, among others listed in the act. The act sets no expiry date; pacjent.gov.pl states that a referral to a specialist clinic is valid until the reason it was issued for ends. | ustawa o świadczeniach opieki zdrowotnej finansowanych ze środków publicznych art. 57 ust. 1 and 2, art. 59aa |
| Waiting list (*lista oczekujących*) | With an e-referral, the patient gives the provider the access key, or the access code and PESEL, before being entered on the list. With a paper referral, the patient delivers the original within 14 working days of the entry, or is removed from the list; posting it in time at a Polish post office of the designated operator counts. One list per service at one provider. | art. 20 ust. 2a, 2aa and 10; KPC art. 165 § 2 |
| Appointment that cannot be kept | The patient must tell the provider without delay. A missed appointment means removal from the list, unless the patient shows force majeure as likely; a request to be restored is due within 7 days of the obstacle ending. After removal, the provider returns a paper referral or makes the e-referral usable again. | art. 20 ust. 2b, 9, 10e and 10f |
| Central e-registration (*centralna elektroniczna rejestracja*) | For services listed by the health minister there are no waiting lists. The patient registers through the Internetowe Konto Pacjenta or with a provider, using one referral per service. A missed appointment means removal, as above. In force from 1 Jan 2026. | art. 23c ust. 1 and 2, art. 23e ust. 3 and 10, art. 23g ust. 10 (added by Dz.U. 2025 poz. 1537) |
| Hospital | Planned hospital treatment needs a referral from a doctor, dentist or feldsher when outpatient care cannot achieve the aim. In an emergency, care is given immediately. The act sets no expiry date for a hospital referral. | art. 58, art. 19 ust. 1 |
| Outpatient physiotherapy | The patient registers the referral with a chosen provider within 30 days of its issue. | guaranteed rehabilitation benefits regulation (t.j. Dz.U. 2021 poz. 265), annex 1 lp. 1 lit. b |
| Spa treatment (*leczenie uzdrowiskowe*, *sanatorium*) | A health-insurance doctor issues the referral, and NFZ must confirm it. Since 1 Jul 2025 the referral is electronic and reaches the NFZ branch for the patient's home through the system. A paper referral, used only without system access or for treatment abroad, must reach the branch within 30 days of issue or it lapses. NFZ decides within 30 days of receipt, extendable by up to 14 days, and tells the patient within 30 days of a refusal or of a wait for a free place. A confirmed paper referral arrives at least 14 days before the stay; for an e-referral, NFZ reports each step through IKP, text message or email. For an adult in a spa sanatorium, the doctor takes into account that at least 12 months have passed since the last spa stay and that stays are recommended no more often than once in 18 months; this does not apply to spa hospitals or outpatient spa treatment. | art. 33 ust. 1 and 2; spa referral regulation (t.j. Dz.U. 2026 poz. 557) § 1a, § 2 ust. 1 pkt 2, ust. 2 and ust. 6, § 4 ust. 5, § 5 ust. 2, § 6 ust. 3, § 7 ust. 1, § 9b ust. 1 and 6, § 9c |
| Medical records (*dokumentacja medyczna*) | Available to the patient, the patient's statutory representative or a person the patient authorised. After death: the person authorised in life, the representative at the time of death, or a close relative, unless another close relative or the patient objected; a court settles disputes. Forms: inspection with notes or photos, an extract, copy or printout, electronic transfer, or a data carrier. The first copy in the requested scope is free for the patient or the representative. Other copies cost at most 0.002 of the previous quarter's average wage per extract page, 0.00007 per copy or printout page and 0.0004 for a data carrier. Records are provided without undue delay, and a refusal states its reason. | ustawa o prawach pacjenta i Rzeczniku Praw Pacjenta art. 26 ust. 1, 2, 2a and 2b, art. 27 ust. 1, art. 28 ust. 1, ust. 2a pkt 1 and ust. 4; medical documentation regulation (t.j. Dz.U. 2026 poz. 1391) § 70 ust. 1, § 71 |
| How long the provider keeps records | 20 years from the end of the year of the last entry. Exceptions: 22 years for records of children under 2, 30 years after a death from injury or poisoning, 10 years for X-rays kept outside the file. | art. 29 ust. 1 |
| Sick-leave certificate (e-ZLA) | The doctor issues it electronically and sends it to ZUS, which shows it to the employer on the employer's PUE profile by the next day. A printout is given when the employer has no PUE profile, or on request; the patient then hands it to the employer or to ZUS, and the act sets no number of days for this. A paper form is used only when the system cannot be used, and the doctor then sends the electronic version within 3 working days. | ustawa o świadczeniach pieniężnych z ubezpieczenia społecznego w razie choroby i macierzyństwa art. 55 ust. 1 and 2, art. 55a ust. 6, 7 and 9, art. 58 ust. 1, art. 62 ust. 1 |
| During sick leave | A change of address during the leave is reported to the employer and ZUS within 3 days. Earning work, or activity that hinders recovery, costs the benefit for the whole leave; everyday and unavoidable incidental tasks are excepted, under definitions in force from 13 Apr 2026. If the patient prevents a ZUS medical check, the certificate stops being valid from the next day. | art. 59 ust. 5e and 6, art. 17 ust. 1, 1a and 1b (Dz.U. 2026 poz. 26) |
| Claiming the benefit | A claim for sickness, maternity or care benefit expires 6 months after the last day of the period it covers, or 3 years when the error was the employer's or ZUS's. | art. 67 ust. 1 and 4 |
| Vaccination schedule | The Chief Sanitary Inspector (GIS) announces the national vaccination programme (*Program Szczepień Ochronnych*) for the next year by 31 October, in a notice in the health minister's official journal. | ustawa o zapobieganiu oraz zwalczaniu zakażeń i chorób zakaźnych u ludzi art. 17 ust. 11 |

## Children and school

| Topic | Rule | Law |
|---|---|---|
| Pre-school year (*roczne przygotowanie przedszkolne*) | Compulsory from the start of the school year in the calendar year the child turns 6, in a kindergarten, a kindergarten class at a primary school or another pre-school form. The parents register the child and ensure regular attendance. | Prawo oświatowe art. 31 ust. 4 and 5, art. 33 ust. 1 |
| School obligation (*obowiązek szkolny*) | Starts with the school year in the calendar year the child turns 7 and lasts until the end of primary school, but not beyond age 18. Education is compulsory until 18 (*obowiązek nauki*). The parents register the child and ensure regular attendance. | art. 35 ust. 1 and 2, art. 40 ust. 1 |
| Earlier or later start | At the parents' request a child may start school at 6, if the child attended pre-school the year before or has an opinion from a counselling centre (*poradnia psychologiczno-pedagogiczna*). A one-year postponement needs the parents' application with a counselling-centre opinion, filed by 31 August of the year the child turns 7. | art. 36 ust. 1, 2 and 4 to 6 |
| School abroad | When the child fulfils the pre-school year or the school obligation at a kindergarten or school abroad, or at a foreign embassy school in Poland, the parents inform the head of the primary school for the district where the child lives, by 30 September each year. | art. 33 ust. 1 pkt 3, art. 36 ust. 10, art. 40 ust. 1 pkt 4 |
| Missed schooling | Unexcused absence from at least half of the classes in a month counts as not fulfilling the obligation, which is enforced in administrative enforcement proceedings. | art. 42 ust. 1 and 2 |
| School year | Runs from 1 September to 31 August. Lessons start on the first weekday of September, or on the following Monday if 1 September is a Friday or a Saturday. They end on the first Friday after 20 June, or on the Wednesday before it when that Thursday is a public holiday. | art. 94; school year regulation (t.j. Dz.U. 2023 poz. 1211) § 2 ust. 1 |
| Breaks | Christmas: 23 to 31 December, from 22 December when it is a Monday. Spring: from the Thursday before Easter to the Tuesday after it. Winter: two weeks between mid-January and the end of February; the education minister announces the dates for each voivodeship by the end of June two years ahead. Summer: from the day after lessons end to 31 August. | regulation § 3 ust. 1 |
| Extra days off | A primary school head may set up to 8 extra days off a year, and the head of a secondary school up to 10. Parents are told by 30 September, and the school must offer supervised activities on those days. | regulation § 5 ust. 1 and 3, § 6 |
| School trips (*wycieczki*) | In public kindergartens and schools, a minor pupil joins a trip with the parents' written consent. Trips run during the school year, not in holidays or breaks. For a trip abroad the school must insure the participants against accidents (NNW) and medical costs. | trips regulation (Dz.U. 2018 poz. 1055) § 1 ust. 1, § 3, § 7 pkt 2, § 8 |
| School accident insurance (NNW) | Prawo oświatowe sets no duty for parents to buy it, and the education ministry describes it as voluntary. The exceptions fall on others: the school insures pupils on trips abroad, and the organiser insures children at camps abroad. | trips regulation § 7 pkt 2; ustawa o systemie oświaty art. 92c ust. 4 pkt 1 |
| Parents' council (*rada rodziców*) | May collect funds from voluntary contributions of parents and from other sources. | Prawo oświatowe art. 84 ust. 6 |
| Child's identity card and passport | One parent applies for a child's identity card, and the child comes along unless under 5. A child's passport needs the consent of both parents: on the application, in a signed letter certified by a passport office or a notary, or in a document with an electronic signature. When the parents disagree or one cannot be reached, a family court order replaces the consent. Validity: see Documents with an expiry date. | ustawa o dowodach osobistych art. 25 ust. 2, art. 27; ustawa o dokumentach paszportowych art. 43 ust. 1, 3 and 5 |
| Child travelling abroad | Polish law requires no written consent document for a child crossing the border. The Border Guard (*Straż Graniczna*) states this for a child travelling without parents, for example with grandparents or alone, and may check that the guardians know of and agree to the trip. Other countries may have their own rules, published by their embassies and summarised on the MSZ pages. Between parents, important matters of the child are decided jointly, and a guardianship court decides when they disagree. | Straż Graniczna guide "Dziecko w podróży" (1 Jul 2025); Kodeks rodzinny i opiekuńczy art. 97 § 2 |

## Keeping and shredding documents

The annual review proposes items past these periods; the household decides.
A period marked *suggested* has no statute of its own, and the basis column
gives the reasoning. Tax papers: see Correcting a return, refunds and keeping
papers.

| Document | Keep for | Basis |
|---|---|---|
| Tax returns, payers' forms, proof of reliefs | 5 years from the end of the year in which the tax was due: for a return due on 30 April 2026, to the end of 2031. For proof of a relief carried forward, count from the tax for the last year in which it is deducted. | Ordynacja podatkowa art. 70 § 1 |
| Energy, gas and water bills, with proof of payment | Suggested: to the end of the third year after the year the bill was due | Claims from sales by a business, which include energy and water, expire after 2 years. Claims for periodic payments expire after 3 years, ending on 31 December. After that a claim generally cannot be enforced against a consumer. Kodeks cywilny art. 554, 555, 118, 117 § 2¹ |
| Phone, internet and TV bills, with proof of payment | Suggested: as for energy bills | The Supreme Court applied the 3-year period of art. 118 to telephone charges under the earlier telecom act (III CZP 20/09). A complaint suspends the limitation until the complaint procedure ends. Kodeks cywilny art. 118; Prawo komunikacji elektronicznej art. 381 |
| Receipts and other proof of purchase of goods | 2 years from delivery, or longer if the stated shelf life is longer; for the length of a voluntary guarantee; until a complaint is settled | ustawa o prawach konsumenta art. 43c ust. 1; Kodeks cywilny art. 577 § 4 |
| Building works contract, acceptance record (*protokół odbioru*), invoices | 5 years from handover, and while a defect claim is pending | Kodeks cywilny art. 568 § 1 and 2, with art. 638 § 1 and art. 656 § 1 |
| Work certificates (*świadectwa pracy*), employers' pay certificates, employment contracts | Suggested: permanently | No period is set for the employee. ZUS accepts these documents as evidence of past work and pay, including for the initial capital (*kapitał początkowy*) for work before 1999. An employer keeps its files only 10 years after the employment ends. Pension proceedings regulation (t.j. Dz.U. 2026 poz. 1055) § 21 and 22; ustawa o emeryturach i rentach z FUS art. 173 ust. 1; Kodeks pracy art. 94 pkt 9b |
| Insurance policies and claim letters | Suggested: 3 years after the cover ends, or after the insurer's written decision on a reported claim | Claims under an insurance contract expire after 3 years. Reporting the claim or the event interrupts the period, which restarts from the insurer's written decision. Kodeks cywilny art. 819 § 1 and 4 |
| Liability (OC) policies | Suggested: 10 years after the cover ends | A claim for damage caused by a tort expires 3 years after the injured person learns of the damage and who is liable, but no later than 10 years after the event, with longer periods after a crime and for personal injury. Kodeks cywilny art. 442¹ § 1 to 4 |
| Notarial deeds and title documents for a home, with invoices for improvements | Suggested: permanently | The notary keeps the original deed and issues further extracts (*wypis*) to the parties and their successors; an extract has the force of the original. A sale within 5 years from the end of the year of purchase or construction is taxed, and only documented purchase costs and value-adding outlays count. Prawo o notariacie art. 95, 109, 110 § 1; ustawa o PIT art. 10 ust. 1 pkt 8, art. 22 ust. 6c |
| Court decisions and court settlements | Suggested: permanently | A claim confirmed by a final court ruling or a court settlement expires after 6 years, and future periodic payments under it after 3 years. Kodeks cywilny art. 125 § 1 |
| Loan agreements, repayment schedules, the lender's confirmation of full repayment | Suggested: 6 years after the end of the year of the final payment | The general limitation period is 6 years and ends on 31 December; claims connected with running a business expire after 3 years. Kodeks cywilny art. 118, art. 120 § 1 |
| Bank statements | Suggested: while a statement is proof for another item in this table | No period is set for a household. Banks keep transaction records for 5 years after the customer relationship ends. Ustawa o przeciwdziałaniu praniu pieniędzy oraz finansowaniu terroryzmu art. 49 ust. 1 |

## Insurance a household must or may have

| Topic | Rule | Law |
|---|---|---|
| Compulsory insurance named in the act | Vehicle liability (OC; see Recurring household obligations), farmers' liability (*OC rolników*) and insurance of farm buildings against fire and other natural events (*ubezpieczenie budynków rolniczych*). Other acts may add compulsory insurance. | ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 4 |
| Farmers' liability (OC rolników) | Required of a person who holds a farm: farmland over 1 ha subject to agricultural tax, or land of any size used for special agricultural production. The duty starts on the day the farm is taken over. The contract runs 12 months and renews by itself unless the farmer gives the insurer written notice no later than one day before it ends; it does not renew if the premium for the ending term is unpaid. | art. 2 ust. 1 pkt 4 and 12, art. 44, art. 45 ust. 1, art. 46 ust. 1 and 2, art. 47 ust. 1 |
| Farm buildings | A building over 20 m² held by a farmer must be insured from the day it is roofed. The same 12-month term and renewal rules apply. | art. 2 ust. 1 pkt 2, art. 59, 60, art. 61 ust. 1, art. 62 ust. 1 and 2 |
| Insurer's notice before automatic renewal | For vehicle OC, farmers' OC and farm buildings, the insurer sends information at least 14 days before the 12-month term ends: the premium for the next term, that it may still change, and how and by when the contract can be ended. It goes electronically if the policyholder agreed to that, otherwise in writing. The insurer confirms the renewed contract with a policy document within 14 days. These rules do not apply to contracts negotiated with a business. | art. 28 ust. 1a to 1d and 1f; art. 46 ust. 1a to 1d and 1f; art. 62 ust. 1a to 1d and 1f |
| Change of farm holder | The previous holder tells the insurer in writing within 14 days; after a death, the new holder does. The contracts pass to the new holder, who may end them by written notice; otherwise they end with their 12-month term. | art. 47 ust. 2, art. 48 ust. 1, art. 63 ust. 1, art. 64 ust. 1 |
| Hunters | Members of the Polish Hunting Association (*Polski Związek Łowiecki*) must be insured against accidents and for liability in hunting. | Prawo łowieckie art. 32 ust. 6 |
| Dog owners | The animal protection act requires a municipal permit to keep a dog of a breed listed as aggressive; it sets no insurance duty. | ustawa o ochronie zwierząt art. 10 ust. 1 |
| Voluntary policies | Home insurance other than for farm buildings, life, personal accident (NNW) and travel insurance are not among the compulsory insurances named in the act. A school or a camp organiser insures children on trips abroad (see Children and school). | ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK art. 4 |
| Renewal of voluntary policies | The Civil Code's insurance chapter has no rule requiring notice before renewal; renewal follows the policy terms. | Kodeks cywilny art. 805 to 834 |
| Time limit for claims | Claims under an insurance contract expire after 3 years. Reporting the claim or the event interrupts the period, and it restarts on the day the person who reported it receives the insurer's written decision. An injured person's claim against a liability insurer has the same limitation as the claim against the person liable. | Kodeks cywilny art. 819 § 1, 3 and 4 |

## Home upkeep, further rules

| Topic | Rule | Law |
|---|---|---|
| Smoke detector | Each dwelling (*lokal mieszkalny*) must have at least one autonomous smoke detector meeting the Polish Standard, unless a fire alarm system or a fixed automatic extinguishing system protects it. A dwelling already in use on 23 Dec 2024 must comply from 1 Jan 2030; others from the start of use. | fire protection regulation (t.j. Dz.U. 2023 poz. 822) § 28a ust. 1 and 2; Dz.U. 2024 poz. 1716 § 2 ust. 2 |
| Carbon monoxide detector | A room in a dwelling where solid, liquid or gas fuel is burned (in a fire zone of the ZL, people-risk, category) needs at least one autonomous CO detector meeting the Polish Standard. This does not apply when the appliance has a sealed combustion chamber or is a gas cooker. Rooms already in use on 23 Dec 2024 must comply from 1 Jan 2030. | § 28a ust. 3 and 4; Dz.U. 2024 poz. 1716 § 2 ust. 3 |
| Fitting and upkeep | Detectors are fitted, maintained and used as the manufacturer's instructions say. The owner equips the building with the required fire devices and keeps them serviced; a manager or user takes this over under a contract, and without one the person actually in control is responsible. | § 3 ust. 3a; ustawa o ochronie przeciwpożarowej art. 4 ust. 1 pkt 2 and 3, ust. 1a |
| Heating-system check (*kontrola systemu ogrzewania*) | The owner or manager has the heating system checked: boilers of 20 to 100 kW at least every 5 years, gas boilers over 100 kW every 4 years, solid or liquid fuel boilers over 100 kW every 2 years, other heat sources over 70 kW every 3 years. Air conditioning over 12 kW gets an efficiency assessment every 5 years. The check is made by a person on the list in the central register of energy performance of buildings. Residential buildings with automation that continuously monitors efficiency and controls the system are exempt. | ustawa o charakterystyce energetycznej budynków art. 23 ust. 1 and 6, art. 24 ust. 8 |
| Gas installation, flues and boiler servicing | The yearly check of gas installations and chimney flues is in Recurring household obligations. These acts set no separate yearly service of the boiler itself; a manufacturer's guarantee sets its own conditions in the guarantee statement. | Prawo budowlane art. 62 ust. 1 pkt 1 lit. c; Kodeks cywilny art. 577 § 1 |
| Local anti-smog rules (*uchwała antysmogowa*) | A voivodeship assembly may restrict or ban the use of fuel-burning installations by a resolution, which is local law. It sets the area, the installations covered, and the fuels allowed or banned or the emission standards; it may set dates and duties needed for control. CEEB: see Recurring household obligations. | Prawo ochrony środowiska art. 96 ust. 1, 6, 7 and 9 |
| Building works warranty (*rękojmia za wady*) | For construction works the contractor answers for defects under the sale warranty rules, applied through the contract-for-work rules. A defect of a building must be found within 5 years of handover. The claim to repair or replace expires 1 year after the defect is found, but for a consumer not before those 5 years end; withdrawal or a price cut follows the same periods. If the contractor fraudulently concealed the defect, the 5-year limit does not apply. | Kodeks cywilny art. 656 § 1, art. 638 § 1, art. 568 § 1 to 3 and 6 |
| Consumer rules | The conformity rules of the consumer rights act cover goods, meaning movable things, including goods made to order; they do not cover works on a building. | ustawa o prawach konsumenta art. 2 pkt 4a, art. 43a ust. 1 |
| Other claims against a contractor | Claims under a construction contract (*umowa o roboty budowlane*) follow the general limitation periods of art. 118 (Supreme Court, seven judges, III CZP 63/01). Claims under a contract for specific work (*umowa o dzieło*) expire 2 years after the work is handed over. | Kodeks cywilny art. 118, art. 646 |

## Travel documents

| Topic | Rule | Law |
|---|---|---|
| Identity card | The Polish identity card proves identity and citizenship in the EU, the EEA, Switzerland and states that accept it by their own decision, and it entitles the holder to cross their borders. | ustawa o dowodach osobistych art. 4 ust. 1 and 2 |
| Passport | The passport entitles the holder to cross borders. Each country sets its own entry rules, including how long a passport must remain valid and whether a visa is needed; MSZ advises checking its travel information (gov.pl/web/dyplomacja) or the destination's consulate. | ustawa o dokumentach paszportowych art. 3; MSZ page "Paszporty" |
| Children | Identity card, passport and consent: see Children and school. EKUZ and document validity: see Documents with an expiry date. | |

## Where things are done

Name the channel; never open a link taken from a message.

| Matter | Official channel |
|---|---|
| Taxes, the pre-filled return (Twój e-PIT) | e-Urząd Skarbowy (urzadskarbowy.gov.pl), information at podatki.gov.pl |
| Identity, vehicle and driver data, official documents | mObywatel, gov.pl |
| Social insurance, child benefit applications | PUE / eZUS and the mZUS app, zus.pl |
| Health records, prescriptions, referrals | Internetowe Konto Pacjenta, pacjent.gov.pl |
| Official electronic mail | e-Doręczenia, edoreczenia.gov.pl |
| Court payment orders issued electronically | e-sąd, e-sad.gov.pl |

Identifiers on Polish papers that are never reproduced
(the personal-data rule): PESEL, NIP, identity card and passport numbers, full
bank account numbers (NRB / IBAN).

## Writing for a household in Poland

- Letters to Polish offices, courts, banks and companies are drafted in
  Polish, in the formal register (*Szanowni Państwo*, *Pan / Pani*), whatever
  language the household uses. An English-speaking household gets an English
  translation alongside, marked as a translation and not as the text to send.
- An appeal against an administrative decision is addressed to the appeal
  body and lodged through the office that issued the decision: the addressee
  block reads *Samorządowe Kolegium Odwoławcze w [miasto] za pośrednictwem
  Wójta Gminy [nazwa]* (or the body the instruction section names), and the
  letter goes to that office (KPA art. 129 § 1). A tax decision follows the
  same pattern through the head of the tax office (Ordynacja podatkowa
  art. 223 § 1).
- A consumer's purchase from a trader is a matter of *niezgodność towaru z
  umową* under the consumer rights act (sections above); use that term in
  drafts and answers, not *rękojmia*.
- In English text, a Polish legal term keeps its Polish name in brackets the
  first time it appears: an appeal (*odwołanie*), a payment order (*nakaz
  zapłaty*), a notice slip (*awizo*).
- Dates and amounts follow the household's language: `pt. 20.11.2026` and
  `1 240,00 zł` in Polish, `Fri 20 Nov 2026` and `PLN 1,240.00` in English,
  with the ISO form in registers.

## Scam patterns

Name the pattern when a message matches one (the untrusted-content rule).

- **Parcel surcharge.** An SMS or email about a held parcel and a small fee
  payable through a link.
- **Tax refund or arrears.** A message "from the tax office" with a link to
  confirm details or pay. The Ministry of Finance and the tax administration
  do not send emails about a tax refund asking to confirm identity or bank
  details.
- **Energy or gas disconnection.** A threat of disconnection today unless a
  small arrear is paid through a link.
- **BLIK code request.** A message from a known contact's account asking for a
  payment code.
- **"Bank security department" call.** A caller asking to move money to a
  "safe account" or to install remote-access software.
- **Relative in trouble.** A call or message claiming a family member needs
  money urgently, collected by a third person.
- **Marketplace buyer.** A "buyer" sending a link to "receive payment" that
  asks for card details.

## Sources

Consolidated texts (*tekst jednolity*) and acts, read through the Sejm ELI
service on 2026-11-13:

- Ustawa o dniach wolnych od pracy, Dz.U. 2025 poz. 296: https://api.sejm.gov.pl/eli/acts/DU/2025/296/text.pdf
- Act adding 24 Dec, Dz.U. 2024 poz. 1965: https://api.sejm.gov.pl/eli/acts/DU/2024/1965/text.html
- Kodeks postępowania administracyjnego, Dz.U. 2025 poz. 1691: https://api.sejm.gov.pl/eli/acts/DU/2025/1691/text.pdf
- Ordynacja podatkowa, Dz.U. 2026 poz. 622: https://api.sejm.gov.pl/eli/acts/DU/2026/622/text.pdf
- Kodeks cywilny, Dz.U. 2026 poz. 795: https://api.sejm.gov.pl/eli/acts/DU/2026/795/text.pdf
- Kodeks postępowania cywilnego, Dz.U. 2026 poz. 468: https://api.sejm.gov.pl/eli/acts/DU/2026/468/text.pdf
- Court delivery regulation, Dz.U. 2024 poz. 19: https://api.sejm.gov.pl/eli/acts/DU/2024/19/text.html
- Ustawa o doręczeniach elektronicznych, Dz.U. 2026 poz. 3: https://api.sejm.gov.pl/eli/acts/DU/2026/3/text.pdf
- Kodeks postępowania w sprawach o wykroczenia, Dz.U. 2026 poz. 1336: https://api.sejm.gov.pl/eli/acts/DU/2026/1336/text.pdf
- Ustawa o prawach konsumenta, Dz.U. 2026 poz. 1244: https://api.sejm.gov.pl/eli/acts/DU/2026/1244/text.pdf
- Ustawa o podatku dochodowym od osób fizycznych, Dz.U. 2026 poz. 592: https://api.sejm.gov.pl/eli/acts/DU/2026/592/text.pdf
- Ustawa o zryczałtowanym podatku dochodowym od niektórych przychodów osiąganych przez osoby fizyczne, Dz.U. 2025 poz. 843: https://api.sejm.gov.pl/eli/acts/DU/2025/843/text.pdf
- Ustawa o podatkach i opłatach lokalnych, Dz.U. 2025 poz. 707: https://api.sejm.gov.pl/eli/acts/DU/2025/707/text.pdf
- Ustawa o podatku rolnym, Dz.U. 2025 poz. 1344: https://api.sejm.gov.pl/eli/acts/DU/2025/1344/text.pdf
- Ustawa o podatku leśnym, Dz.U. 2025 poz. 176: https://api.sejm.gov.pl/eli/acts/DU/2025/176/text.pdf
- Ustawa o ubezpieczeniach obowiązkowych, UFG i PBUK, Dz.U. 2026 poz. 783: https://api.sejm.gov.pl/eli/acts/DU/2026/783/text.pdf
- Ustawa o pomocy państwa w wychowywaniu dzieci, Dz.U. 2026 poz. 508: https://api.sejm.gov.pl/eli/acts/DU/2026/508/text.pdf
- Ustawa o opłatach abonamentowych, Dz.U. 2025 poz. 1585: https://api.sejm.gov.pl/eli/acts/DU/2025/1585/text.pdf
- Ustawa o utrzymaniu czystości i porządku w gminach, Dz.U. 2025 poz. 733: https://api.sejm.gov.pl/eli/acts/DU/2025/733/text.pdf
- Prawo budowlane, Dz.U. 2026 poz. 524: https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf
- Ustawa o wspieraniu termomodernizacji i remontów oraz o centralnej ewidencji emisyjności budynków, Dz.U. 2026 poz. 920: https://api.sejm.gov.pl/eli/acts/DU/2026/920/text.pdf
- Ustawa o dowodach osobistych, Dz.U. 2025 poz. 1753: https://api.sejm.gov.pl/eli/acts/DU/2025/1753/text.pdf
- Act of 14.04.2021 amending the identity card act, Dz.U. 2021 poz. 1000: https://api.sejm.gov.pl/eli/acts/DU/2021/1000/text.html
- Ustawa o dokumentach paszportowych, Dz.U. 2026 poz. 196: https://api.sejm.gov.pl/eli/acts/DU/2026/196/text.pdf
- Ustawa o kierujących pojazdami, Dz.U. 2025 poz. 1226: https://api.sejm.gov.pl/eli/acts/DU/2025/1226/text.pdf
- Act of 17.10.2025 amending road traffic and driver rules, Dz.U. 2025 poz. 1676: https://api.sejm.gov.pl/eli/acts/DU/2025/1676/text.pdf
- Regulation on driving licence documents, Dz.U. 2025 poz. 1073: https://api.sejm.gov.pl/eli/acts/DU/2025/1073/text.pdf
- Communication on probation data in the driver register, Dz.U. 2026 poz. 743: https://api.sejm.gov.pl/eli/acts/DU/2026/743/text.pdf
- KPC reform of 2023 (art. 139¹), Dz.U. 2023 poz. 614: https://api.sejm.gov.pl/eli/acts/DU/2023/614/text.html
- Ustawa o rozpatrywaniu reklamacji przez podmioty rynku finansowego, o Rzeczniku Finansowym i o Funduszu Edukacji Finansowej, Dz.U. 2026 poz. 823: https://api.sejm.gov.pl/eli/acts/DU/2026/823/text.pdf
- Ustawa o usługach płatniczych, Dz.U. 2026 poz. 623: https://api.sejm.gov.pl/eli/acts/DU/2026/623/text.pdf
- Prawo komunikacji elektronicznej, Dz.U. 2024 poz. 1221, Chancellery unified text of 16.10.2026: https://api.sejm.gov.pl/eli/acts/DU/2024/1221/text/U/D20241221Lj.pdf
- Prawo energetyczne, Dz.U. 2026 poz. 43: https://api.sejm.gov.pl/eli/acts/DU/2026/43/text.pdf
- Prawo energetyczne amendments, Dz.U. 2026 poz. 516 and 900: https://api.sejm.gov.pl/eli/acts/DU/2026/516/text.pdf and https://api.sejm.gov.pl/eli/acts/DU/2026/900/text.pdf
- Electricity system regulation, Dz.U. 2025 poz. 919: https://api.sejm.gov.pl/eli/acts/DU/2025/919/text.pdf
- Gas system regulation, Dz.U. 2025 poz. 1382: https://api.sejm.gov.pl/eli/acts/DU/2025/1382/text.pdf
- Ustawa o działalności ubezpieczeniowej i reasekuracyjnej, Dz.U. 2025 poz. 1526: https://api.sejm.gov.pl/eli/acts/DU/2025/1526/text.pdf
- Ustawa o ochronie praw lokatorów, Dz.U. 2023 poz. 725: https://api.sejm.gov.pl/eli/acts/DU/2023/725/text.pdf
- Ordynacja podatkowa amendment in force from 1.10.2026, Dz.U. 2026 poz. 846: https://api.sejm.gov.pl/eli/acts/DU/2026/846/text.pdf
- Notice on statutory late-payment interest, M.P. 2026 poz. 367: https://api.sejm.gov.pl/eli/acts/MP/2026/367/text.pdf

- Prawo farmaceutyczne, Dz.U. 2026 poz. 612: https://api.sejm.gov.pl/eli/acts/DU/2026/612/text.pdf
- Regulation on prescriptions, Dz.U. 2025 poz. 604: https://api.sejm.gov.pl/eli/acts/DU/2025/604/text.pdf
- Ustawa o świadczeniach opieki zdrowotnej finansowanych ze środków publicznych, Dz.U. 2025 poz. 1461: https://api.sejm.gov.pl/eli/acts/DU/2025/1461/text.pdf
- Amendment introducing central e-registration, in force from 1.01.2026, Dz.U. 2025 poz. 1537: https://api.sejm.gov.pl/eli/acts/DU/2025/1537/text.pdf
- Regulation on referrals for spa treatment, Dz.U. 2026 poz. 557: https://api.sejm.gov.pl/eli/acts/DU/2026/557/text.pdf
- Regulation on guaranteed rehabilitation benefits, Dz.U. 2021 poz. 265: https://api.sejm.gov.pl/eli/acts/DU/2021/265/text.pdf
- Ustawa o prawach pacjenta i Rzeczniku Praw Pacjenta, Dz.U. 2024 poz. 581: https://api.sejm.gov.pl/eli/acts/DU/2024/581/text.pdf
- Medical documentation regulation, Dz.U. 2026 poz. 1391: https://api.sejm.gov.pl/eli/acts/DU/2026/1391/text.pdf
- Ustawa o świadczeniach pieniężnych z ubezpieczenia społecznego w razie choroby i macierzyństwa, Dz.U. 2026 poz. 854: https://api.sejm.gov.pl/eli/acts/DU/2026/854/text.pdf
- Act of 18.12.2025 amending social insurance and sick-leave rules, Dz.U. 2026 poz. 26: https://api.sejm.gov.pl/eli/acts/DU/2026/26/text.pdf
- Ustawa o zapobieganiu oraz zwalczaniu zakażeń i chorób zakaźnych u ludzi, Dz.U. 2025 poz. 1675: https://api.sejm.gov.pl/eli/acts/DU/2025/1675/text.pdf
- Prawo oświatowe, Dz.U. 2026 poz. 820: https://api.sejm.gov.pl/eli/acts/DU/2026/820/text.pdf
- Regulation on the organisation of the school year, Dz.U. 2023 poz. 1211: https://api.sejm.gov.pl/eli/acts/DU/2023/1211/text.pdf
- Regulation on school trips (krajoznawstwo i turystyka), Dz.U. 2018 poz. 1055: https://api.sejm.gov.pl/eli/acts/DU/2018/1055/text.pdf
- Ustawa o systemie oświaty, Dz.U. 2025 poz. 881: https://api.sejm.gov.pl/eli/acts/DU/2025/881/text.pdf
- Kodeks rodzinny i opiekuńczy, Dz.U. 2026 poz. 236: https://api.sejm.gov.pl/eli/acts/DU/2026/236/text.pdf
- Ustawa o emeryturach i rentach z Funduszu Ubezpieczeń Społecznych, Dz.U. 2025 poz. 1749: https://api.sejm.gov.pl/eli/acts/DU/2025/1749/text.pdf
- Regulation on pension proceedings, Dz.U. 2026 poz. 1055: https://api.sejm.gov.pl/eli/acts/DU/2026/1055/text.pdf
- Kodeks pracy, Dz.U. 2026 poz. 1245: https://api.sejm.gov.pl/eli/acts/DU/2026/1245/text.pdf
- Prawo o notariacie, Dz.U. 2026 poz. 614: https://api.sejm.gov.pl/eli/acts/DU/2026/614/text.pdf
- Ustawa o przeciwdziałaniu praniu pieniędzy oraz finansowaniu terroryzmu, Dz.U. 2025 poz. 644: https://api.sejm.gov.pl/eli/acts/DU/2025/644/text.pdf
- Prawo łowieckie, Dz.U. 2025 poz. 539: https://api.sejm.gov.pl/eli/acts/DU/2025/539/text.pdf
- Ustawa o ochronie zwierząt, Dz.U. 2026 poz. 1485: https://api.sejm.gov.pl/eli/acts/DU/2026/1485/text.pdf
- Fire protection regulation for buildings, Dz.U. 2023 poz. 822: https://api.sejm.gov.pl/eli/acts/DU/2023/822/text.pdf
- Amendment adding smoke and CO detectors, Dz.U. 2024 poz. 1716: https://api.sejm.gov.pl/eli/acts/DU/2024/1716/text.pdf
- Ustawa o ochronie przeciwpożarowej, Dz.U. 2025 poz. 188: https://api.sejm.gov.pl/eli/acts/DU/2025/188/text.pdf
- Prawo ochrony środowiska, Dz.U. 2026 poz. 1453: https://api.sejm.gov.pl/eli/acts/DU/2026/1453/text.pdf
- Ustawa o charakterystyce energetycznej budynków, Dz.U. 2024 poz. 101: https://api.sejm.gov.pl/eli/acts/DU/2024/101/text.pdf
- Prawo o ruchu drogowym, Chancellery unified text of 4.11.2026 (base t.j. Dz.U. 2024 poz. 1251): https://api.sejm.gov.pl/eli/acts/DU/1997/602/text/U/D19970602Lj.pdf
- Act of 7.11.2025 amending Prawo o ruchu drogowym (inherited vehicle, 60 days), Dz.U. 2025 poz. 1734: https://api.sejm.gov.pl/eli/acts/DU/2025/1734/text.pdf
- Vehicle registration regulation, Dz.U. 2024 poz. 1709: https://api.sejm.gov.pl/eli/acts/DU/2024/1709/text.pdf
- Driving licence pattern regulation, Dz.U. 2025 poz. 1072: https://api.sejm.gov.pl/eli/acts/DU/2025/1072/text.pdf
- Ustawa o podatku od czynności cywilnoprawnych, Dz.U. 2026 poz. 191: https://api.sejm.gov.pl/eli/acts/DU/2026/191/text.pdf
- Act of 18.09.2026 raising the PCC limit for movables to PLN 3,000, Dz.U. 2026 poz. 1354: https://api.sejm.gov.pl/eli/acts/DU/2026/1354/text.pdf
- Ustawa o ewidencji ludności, Dz.U. 2026 poz. 384: https://api.sejm.gov.pl/eli/acts/DU/2026/384/text.pdf
- Ustawa o zasadach ewidencji i identyfikacji podatników i płatników, Dz.U. 2026 poz. 151: https://api.sejm.gov.pl/eli/acts/DU/2026/151/text.pdf
- Act of 4.09.2026 amending the taxpayer identification act (art. 9 ust. 1d from 1.01.2027), Dz.U. 2026 poz. 1270: https://api.sejm.gov.pl/eli/acts/DU/2026/1270/text.pdf
- Prawo o aktach stanu cywilnego, Dz.U. 2026 poz. 393: https://api.sejm.gov.pl/eli/acts/DU/2026/393/text.pdf
- Ustawa o świadczeniach rodzinnych, Dz.U. 2026 poz. 1240: https://api.sejm.gov.pl/eli/acts/DU/2026/1240/text.pdf
- Act of 6.12.2024 amending Kodeks pracy (supplementary maternity leave), Dz.U. 2024 poz. 1871: https://api.sejm.gov.pl/eli/acts/DU/2024/1871/text.pdf
- Ustawa o świadczeniach opieki zdrowotnej finansowanych ze środków publicznych, Chancellery unified text of 3.08.2026 (base t.j. Dz.U. 2025 poz. 1461): https://api.sejm.gov.pl/eli/acts/DU/2004/2135/text/U/D20042135Lj.pdf
- Regulation on guaranteed primary care services, Dz.U. 2023 poz. 1427: https://api.sejm.gov.pl/eli/acts/DU/2023/1427/text.pdf
- Ustawa o pracowniczych planach kapitałowych, Dz.U. 2026 poz. 192: https://api.sejm.gov.pl/eli/acts/DU/2026/192/text.pdf
- Ustawa o rynku pracy i służbach zatrudnienia, Dz.U. 2025 poz. 620: https://api.sejm.gov.pl/eli/acts/DU/2025/620/text.pdf
- Ustawa o cmentarzach i chowaniu zmarłych, Dz.U. 2025 poz. 1590: https://api.sejm.gov.pl/eli/acts/DU/2025/1590/text.pdf
- Ustawa o emeryturach i rentach z FUS, Dz.U. 2025 poz. 1749: https://api.sejm.gov.pl/eli/acts/DU/2025/1749/text.pdf
- Act of 9.05.2025 raising the funeral allowance to PLN 7,000, Dz.U. 2025 poz. 718: https://api.sejm.gov.pl/eli/acts/DU/2025/718/text.pdf
- Act of 5.08.2025 on funeral allowance procedure, Dz.U. 2025 poz. 1159: https://api.sejm.gov.pl/eli/acts/DU/2025/1159/text.pdf
- ZUS notice on the funeral allowance amount, M.P. 2026 poz. 150: https://api.sejm.gov.pl/eli/acts/MP/2026/150/text.pdf
- Ustawa o ubezpieczeniu społecznym rolników, Dz.U. 2025 poz. 1770: https://api.sejm.gov.pl/eli/acts/DU/2025/1770/text.pdf
- Ustawa o podatku od spadków i darowizn, Dz.U. 2026 poz. 478: https://api.sejm.gov.pl/eli/acts/DU/2026/478/text.pdf
- Act of 21.11.2025 amending the inheritance and gift tax act, Dz.U. 2025 poz. 1854: https://api.sejm.gov.pl/eli/acts/DU/2025/1854/text.pdf
- Prawo bankowe, Dz.U. 2026 poz. 38: https://api.sejm.gov.pl/eli/acts/DU/2026/38/text.pdf

Official pages:

- Twój e-PIT: https://podatki.gov.pl/twoj-e-pit
- Tax administration warning on false emails: https://www.podatki.gov.pl/aktualnosci/uwaga-na-falszywe-e-maile
- ZUS, 800+ applications for the new period: https://www.zus.pl/-/mo%C5%BCna-ju%C5%BC-sk%C5%82ada%C4%87-wnioski-o-800-na-nowy-okres-%C5%9Bwiadczeniowy
- mObywatel: https://www.gov.pl/web/mobywatel
- Internetowe Konto Pacjenta: https://pacjent.gov.pl/
- e-Doręczenia: https://www.gov.pl/web/e-doreczenia and https://edoreczenia.gov.pl/
- e-sąd (EPU): https://www.e-sad.gov.pl/
- Supreme Court, IV CKN 1026/00 of 10.08.2000, via SAOS: https://www.saos.org.pl/judgments/79878
- Supreme Court, II UZ 43/04 of 28.09.2004, via SAOS: https://www.saos.org.pl/judgments/82871
- Regional Court Gliwice, III Cz 256/26 of 10.09.2026, via SAOS: https://www.saos.org.pl/judgments/554498
- Police, new rules for novice drivers (18.09.2026): https://policja.pl/pol/aktualnosci/281897,Nowe-zasady-dla-poczatkujacych-kierowcow-wazne-wyjasnienie.html
- NFZ, EKUZ: https://www.nfz.gov.pl/dla-pacjenta/nasze-zdrowie-w-ue/leczenie-w-krajach-unii-europejskiej-i-efta/wypoczynek-w-panstwach-czlonkowskich-ueefta-ekuz/
- City of Warsaw, rules for new category B drivers from 4 Sep 2026: https://warszawa19115.pl/-/przewodnik-dla-nowych-kierowcow-ktorzy-uzyskali-po-raz-pierwszy-uprawnienia-kat.-b-poczawszy-od-4-wrzesnia-2026-r.
- podatki.gov.pl, payer deadlines for PIT-11: https://podatki.gov.pl/poradniki-i-informatory/platnik
- podatki.gov.pl, KAS reminder on PIT-11, PIT-8C and PIT-40A/11A (15.01.2026): https://podatki.gov.pl/aktualnosci/kas-przypomina-platniku-przeslij-pit-za-2025-rok-z-prawidlowymi-danymi-podatnika
- Supreme Court, I CSK 1094/14 of 14.01.2016, via SAOS: https://www.saos.org.pl/judgments/244204
- Court of Appeal Łódź, I ACa 1710/22 of 29.09.2023 (citing III CZP 164/94), via SAOS: https://www.saos.org.pl/judgments/493764
- pacjent.gov.pl, Skierowanie do specjalisty (updated 6.04.2023): https://pacjent.gov.pl/artykul/skierowanie-do-specjalisty
- Ministry of Health, Jak długo ważna jest e-recepta (21.01.2020): https://www.gov.pl/web/zdrowie/jak-dlugo-wazna-jest-e-recepta
- Ministry of Education, NNW insurance of pupils is voluntary (12.09.2019): https://www.gov.pl/web/edukacja/bezpieczny-poczatek-nowego-roku-szkolnego
- Straż Graniczna, Dziecko w podróży (1.07.2025): https://www.strazgraniczna.pl/pl/niezbednik-podroznego/dziecko-w-podrozy/1302,Dziecko-w-podrozy-poradnik.html
- MSZ, Paszporty: https://www.gov.pl/web/dyplomacja/paszporty; MSZ travel information (on 2026-11-13 the address redirected to https://odyseusz.gov.pl/): https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych
- Ministry of Development and Technology, checks of heating and air-conditioning systems (14.04.2023): https://www.gov.pl/web/rozwoj-technologia/kontrole-systemow-ogrzewania-i-klimatyzacji--nowe-przepisy-wymogi-obowiazujace-od-dawna
- State Fire Service (KP PSP Wejherowo), smoke and CO detectors (22.11.2025): https://www.gov.pl/web/kppsp-wejherowo/autonomiczne-czujki-dymu-i-autonomiczne-czujki-tlenku-wegla
- Supreme Court, III CZP 63/01 of 11.01.2002 (seven judges), via SAOS: https://www.saos.org.pl/judgments/81119
- Supreme Court, III CZP 20/09 of 7.05.2009, via SAOS: https://www.saos.org.pl/judgments/90182
- gov.pl, notifying the sale or purchase of a vehicle: https://www.gov.pl/web/gov/zglos-zbycie-lub-nabycie-pojazdu-na-przyklad-sprzedaz-kupno-darowizne
- gov.pl, replacing the vehicle registration certificate: https://www.gov.pl/web/gov/wymien-dowod-rejestracyjny-pojazdu
- gov.pl, PCC-3: https://www.gov.pl/web/gov/zaplac-podatek-od-czynnosci-cywilnoprawnych
- gov.pl, SD-Z2: https://www.gov.pl/web/gov/zglos-otrzymanie-majatku-ze-spadku-lub-darowizny-formularz-podatkowy-sd-z2
- gov.pl, SD-3: https://www.gov.pl/web/gov/zloz-zeznanie-podatkowe-o-nabyciu-rzeczy-lub-praw-majatkowych-formularz-podatkowy-sd-3
- podatki.gov.pl, registration and update forms (ZAP-3): https://podatki.gov.pl/formularze-rejestracja
