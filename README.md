# RUP — Desk & Exam Copy Automation

A **self-initiated passion project** I built while working at **Rutgers University Press (RUP)**.
Part of my job was fulfilling professor **desk-copy** and **exam-copy** requests and pushing the
resulting customer orders through several disconnected web systems, all by hand. Nobody asked
me to automate it. I saw how repetitive and error-prone the process was and taught myself enough
Selenium, spreadsheet automation and LLM APIs to **semi-automate my own workflow**, so I could
spend less time keying in orders and more time on work that needed judgment.

## Impact

| Version | What it automated | Manual processing time |
|---------|-------------------|------------------------|
| v1: Selenium automation | Request classification, e-copy links, print order entry, emails, status tracking | **−50%** |
| v2: + ChatGPT API for international orders | Classifying foreign and Canadian shipping addresses (previously a slow manual step) | **−80%** overall |

International orders were the slowest to process by hand, because their address formats don't fit
simple rules. Sending that one fuzzy step to an LLM (`AIAddressFinder.py`) is what took the time
savings from half to four-fifths.

> **Why this repo exists:** it's a portfolio piece meant to show my *initiative* and my *reasoning*
> for building practical automation around a real-world, messy, multi-system workflow. It is one
> of my **earliest automation attempts**, so it's deliberately preserved as-is (rough edges and
> all) rather than polished after the fact.
>
> It is **not** meant to be run by others. All credentials, personal emails, customer PII, and
> internal/unpublished data have been removed or replaced with placeholders — secrets are read
> from environment variables (see `.env.example`). The sample data files contain only headers and
> dummy rows.

## The problem

A professor requests a desk or exam copy of a book. Fulfilling one request manually meant:

1. Reading the request and classifying it: **desk vs. exam**, and **print / electronic / both**.
2. Looking up the book's publisher.
3. For **electronic** copies — logging into BiblioVault and generating a time-limited
   download link with the right permissions.
4. For **print desk** copies — logging into the Chicago Distribution Center, classifying the
   shipping address (domestic / Canadian / foreign), and keying in a full order.
5. For **exam** copies — generating the correct quarterly discount code.
6. Drafting and sending the right email to the professor.
7. Marking the request as done in the tracking spreadsheet.

Doing this by hand meant logging into each system, copying the same customer details between
them, and choosing the right email template, for every single request. This repo automates most
of that chain and leaves a human in the loop to review each step (hence *semi*-automation), so
the repetitive data entry is handled by code and I only check and confirm.

## How it fits together

```
request (Excel / CSV / Streamlit form)
        │
        ▼
  RUPAgent.py ──► gather_info() ──► decide_format()  (desk/exam × print/elec/both)
        │                               │
        │            ┌──────────────────┼───────────────────┐
        │            ▼                  ▼                   ▼
        │        links.py          desks.py            helpers.py
        │   (BiblioVault e-link) (CDC print order)  (publisher lookup,
        │                             │              discount codes,
        │                             ▼              xlsx status flags)
        │                      AIAddressFinder.py
        │                   (LLM address classification)
        ▼
  make_email_content() ──► gmail.py / outlook.py (SMTP send)
        │
        ▼
  write_excel()  (mark request complete / partial)
```

## Modules

| File | Role |
|------|------|
| `RUPAgent.py` | Main engine: reads requests from `Requests.xlsx`, decides the request type, orchestrates link/order/email steps, and writes status back to the sheet. |
| `helpers.py` | Shared helpers: publisher lookup (scrapes the RUP catalog), quarterly discount-code generation, and Excel highlight/border detection used to track completion state. |
| `links.py` | Selenium flow that logs into **BiblioVault** and generates a time-limited electronic comp-copy link with custom print/copy permissions. |
| `desks.py` | Selenium flow that logs into the **Chicago Distribution Center** and places a print desk-copy order, including address-type handling. |
| `AIAddressFinder.py` | Classifies a shipping address as Domestic / Canadian / Foreign using an LLM (OpenAI, with a DeepSeek alternative), so `desks.py` fills the right order fields. |
| `RUP.py` | A **Streamlit** intake form — an alternative front-end for capturing requests into a CSV. |
| `gmail.py` / `outlook.py` | SMTP senders for the generated customer emails. |
| `launch_notes.py` | Parses internal book "launch notes" and updates the **Firebrand** title-management system via Selenium. |
| `AIAgentFlowchart.drawio` | Flowchart of the decision/agent logic (open in [diagrams.net](https://app.diagrams.net/)). |
| `requirements.txt` | Third-party packages used across the scripts. |

## Notes on the code

- **Selenium-heavy.** Most integrations are browser automations because the underlying systems
  have no APIs — so the scripts drive real login pages and forms. The deliberate `time.sleep()`
  calls and long waits are where a human reviews or completes a step.
- **LLM for a fuzzy sub-problem.** Address classification doesn't reduce cleanly to rules
  (foreign vs. Canadian vs. odd domestic formats), so it's delegated to a model.
- **Spreadsheet as the source of truth / state machine.** Completion is tracked via cell
  highlighting (done) vs. borders (partial), which `helpers.py` reads back on the next run.

## Known limitations

Preserved as an early attempt, so some rough edges remain by design:

- Scripts expect a local Chrome/ChromeDriver and live vendor accounts; hostnames are replaced
  with `example.com` placeholders, so nothing here runs end-to-end as published.
- Publisher detection in `helpers.py` scrapes a fixed-width slice of the catalog page HTML,
  which is brittle against site changes; a real version would parse the page or use an API.
- Spreadsheet column positions are hard-coded in `RUPAgent.py` and assume the intake form's
  exact export layout.
- No automated tests — each flow was validated by hand with a human reviewing every step.

## Security

Originally this code hard-coded live credentials and real recipient data inline. For this
public, showcase version:

- All API keys and logins are read from environment variables (`os.getenv(...)`); none are stored
  in the repo. See `.env.example` for the expected variable names.
- Internal system hostnames and the real discount-code scheme were replaced with generic
  placeholders (the generation logic is preserved).
- Real customer PII and internal/unpublished book data in examples and sample files were replaced
  with fictional placeholders.
