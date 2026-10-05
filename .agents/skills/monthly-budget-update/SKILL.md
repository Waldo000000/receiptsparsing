---
name: monthly-budget-update
description: Process bank CSV exports in receiptsparsing, resolve monthly budget categories and Amazon purchases, and copy the target month's rows to the clipboard for pasting into the master spreadsheet.
---

# Monthly budget update

The inputs are bank CSV exports and, when supplied, credit-card statements or activity exports; the deliverable is new rows for one calendar month on the user's clipboard, ready to paste into the master spreadsheet. Keep the master spreadsheet unchanged. Infer the requested year/month from the conversation; ask if missing. Never substitute the current month automatically.

## Repository and processing

Use the receiptsparsing repository containing this skill (`.agents/skills/monthly-budget-update/SKILL.md`). Read the current parser and `purposes_config.py`; that private, gitignored config is authoritative. Inputs are in `in/`, outputs in `out/`, and backups in `bkp/`. Before processing, check that the bank exports cover the entire requested month; if an export was created before month-end, request a refreshed export before treating the result as complete.

Run `./parse_csv.all.sh` to back up and regenerate output; inspect failures and parsing errors before export. It processes all dates. Scope review and final clipboard rows to the requested month. Use Python's CSV reader, never split CSV on commas. UBank activity exports can have 10 columns or 11 including Tags; skip their header. Preserve actual implementation signs: expenses are positive and refunds/income negative.

## Categorisation

Apply reasonable guesses using existing mappings and merchant/product evidence. Do not ask the user to classify obvious restaurants, bakeries, pharmacies, or game purchases one by one. Briefly disclose inferred decisions. Ask about genuinely ambiguous purchases, gifts, transfers, or insufficient evidence; offer all remaining monthly TODOs together when requested. Retain a TODO the user wants to leave unresolved.

Use the user's private `purposes_config.py` for merchant mappings and personal conventions. If it is missing, use `purposes_config.example.py` as a starting template and ask for the user's categorisation preferences. Keep personal names, payee rules, purchase history, transaction IDs and recipient details in gitignored local files rather than this public skill. Preserve the exact three category levels the user requests, including blank middle levels; do not invent a different hierarchy for a named trip or subscription.

When the user clarifies an uncertain line item, prepend a concise factual version of that clarification to the description: `Clarification; original description`. Preserve the original description verbatim after the semicolon. Save the enrichment in gitignored local data keyed by the transaction ID or stable import reference, so it survives regeneration; do not put personal clarifications in this public skill. Apply description enrichment after category matching so merchant rules anchored at the start still work. Avoid adding the same prefix again on reruns.

Merchant-wide rules suit stable recurring categories. Purchases and personal transfers whose purpose varies need transaction-specific rules. Prefer bank Transaction ID regexes in the appropriate private config leaf, with comments recording the relevant purpose. Confirm ambiguous credit-card repayments rather than assuming they are transfers. Re-run and check for overlapping category matches after changes.

## Credit-card transactions

Include individual card purchases, fees and refunds. Record bank-side repayments and matching card-side credits as `Revenue / Transfer` so repayments do not count as spending again. Keep refunds in the original spending category with a negative amount. If an earlier month used a repayment as a proxy for spending, confirm any retrospective replacement before changing an already-pasted month.

Keep raw statements, extracted details and activity exports under gitignored `in/`. Reconcile statement withdrawals, credits and running/closing balances. When a statement and activity export overlap, import each transaction once while preserving genuine repeated purchases; compare occurrence counts rather than deduplicating by date and amount alone. Check posting-date coverage through month-end. Purchases that post in the following month belong in that next monthly export; retain their input rows and private category rules for the next run.

The current parser accepts three-column Bendigo CSVs but not seven-column extended exports directly. Extended exports contain account, posted date, transaction code, signed AUD amount, type, merchant and details. A leading `DDMM` followed by a currency code in the details records the purchase/refund date; infer the year from the posting date, including December/January rollover. Payment reference numbers are not purchase dates. Preserve the AUD amount rather than substituting the foreign-currency amount.

Normalise PDF or extended-export rows into `in/in.bendigo.csv` using the existing six-column parser format when both dates are available: posted date, effective date, description, negative debit amount or blank, positive credit amount or blank, balance or blank. Dates use `DD/MM/YYYY`; this parser flips input signs into positive expenses and negative credits. Keep source references in descriptions for private transaction-specific rules. Preserve both dates in output and select the month by posting date. For extended exports, keep stable import references: `BENDIGO-` plus the first 16 hex characters of SHA-256 over the original columns 1–6 joined by ASCII unit separator (`\x1f`), excluding the account column. Identical rows may share a reference; preserve their occurrence count. This keeps existing private categorisation rules valid on the next export.

## Amazon matching and browser choice

First check saved order details in `in/amazon/`; reuse evidence that matches the transaction. Retrieve only orders still needed for unresolved transactions in the target month, allowing nearby order dates to reconcile later shipment charges. Match amount, items, order date, shipment/payment details and refunds; do not force ambiguous equal-amount matches. Preserve useful order details in gitignored `in/amazon/`. Ask about purchase purpose where it changes category: a lamp may be a gift rather than an asset.

Prefer an available, user-authorized browser connection that reuses their signed-in session. Inspect the actual tools exposed to this session before promising Chrome access. Installing the ChatGPT extension or typing `@chrome` as plain text does not establish tool access. If no Chrome tool is available, state that limitation once and offer pasted order details or a separate browser login; do not repeatedly ask the user to install or mention an unavailable integration. Official setup guide: https://learn.chatgpt.com/docs/chrome-extension .

Fallback: agent-browser with a dedicated persistent profile outside the repository, e.g. `agent-browser --session receipts-amazon --headed --profile ~/.agent-browser/receipts-amazon-profile open https://www.amazon.com.au/your-orders/orders`. Let the user enter login/MFA directly. A persistent profile can reduce repeated logins, but Amazon may require reauthentication. See https://agent-browser.dev/sessions . Check that the browser tool is installed and the session is available. Do not save credentials or cookies in skill files or the repository.

For agent-browser, inspect the live page first. Possible Amazon UI selectors are: `.order-card` contains order text and `a[href*=order-details]` links; `.a-pagination a` supplies subsequent pages and `#time-filter` controls the period. Treat these selectors as fallible. Read order history/details only; do not purchase, cancel, return or change account settings. Stop after needed matches are collected and close a browser this workflow owns when finished. An Amazon data export or pasted order details is an alternative when browser access is unavailable.

## Monthly clipboard output

Filter on **posting date (column 1)** using `month_start <= posted_date < next_month_start`, including the entire last day. Keep the purchase/effective date unchanged in column 0. A purchase made in one month and posted in the next appears only in the posting month's export. This is the established workflow; do not ask the user to choose again unless they request a change.

Run the bundled helper from the repository root: `python .agents/skills/monthly-budget-update/scripts/export_month.py --year YYYY --month M`. It reads `out/out.csv`, filters by posting date, preserves duplicate rows and all nine columns, sorts by posting then effective date, and writes CSV, TSV and UTF-16LE clipboard files under `out/`. It validates round-tripping but does not write the system clipboard. Inspect TODOs and category overlaps before copying.

Preserve all nine output columns and original amounts: effective date, posted date, amount, three category levels, description, blank notes, source. Keep duplicate-looking transactions unless confirmed duplicates. Sort by posting date, then effective date. Include unresolved TODOs. Write a month-specific CSV and a tab-delimited clipboard file under `out/`, with no header. Quote fields correctly using `csv.writer`; validate round-tripping, row count, column count and monthly boundaries. Do not claim rows are absent from the master spreadsheet unless that was actually checked; if rerunning an already-pasted month, clarify append versus replacement rather than duplicate the month. When the user explicitly requests a corrected export, prepare the replacement and tell them to replace the previous pasted rows rather than append it.

In WSL, prepare a UTF-16LE text file for Windows clipboard access. Use `wslpath -w` to obtain its Windows path. PowerShell can read it with `[IO.File]::ReadAllText(path, [Text.Encoding]::Unicode)` and write it using `Set-Clipboard -Value`. Immediately compare `Get-Clipboard -Raw` with the exact prepared text in the same command. Do not merely assume a successful `clip.exe` call proves the clipboard still contains the export. Honor tool permission requirements; no additional conversational approval is needed when the user has requested the clipboard export.

Report copied row count, target month, and remaining TODOs. Provide the month-specific export link as a fallback. Never include other months or a header in the clipboard.

## Public repository changes

When asked to commit or push, inspect the complete staged diff and tracked file list. Keep raw financial inputs, generated exports, private categorisation config, browser profiles, credentials and copied statement text out of Git. Use synthetic data in tests and generic workflow examples in this skill; personal rules stay in the ignored config. Stage explicit public paths and verify ignored files have not already been tracked.
