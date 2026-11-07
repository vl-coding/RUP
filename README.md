# RUP — Desk & Exam Copy Automation

A set of Python scripts I wrote during my internship at **Rutgers University Press (RUP)**
to semi-automate the fulfillment of professor **desk-copy** and **exam-copy** requests — a
process that was previously done entirely by hand across several disconnected web systems.

> **Why this repo exists:** it's a portfolio piece meant to show my *reasoning and logic* for
> building practical automation around real-world, messy, multi-system workflows. It is one of
> my **earliest automation attempts**, so it's deliberately preserved as-is (rough edges and all)
> rather than polished after the fact.
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

This repo automates most of that chain, leaving a human in the loop for review — hence
*semi*-automation.

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
        │                      AIAdressFinder.py
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
| `AIAdressFinder.py` | Classifies a shipping address as Domestic / Canadian / Foreign using an LLM (OpenAI, with a DeepSeek alternative), so `desks.py` fills the right order fields. |
| `RUP.py` | A **Streamlit** intake form — an alternative front-end for capturing requests into a CSV. |
| `gmail.py` / `outlook.py` | SMTP senders for the generated customer emails. |
| `clocking.py` | A separate utility: scheduled auto clock-in/out on **Rutgers HRMS** (Selenium), with an email confirmation. Waits for a manual 2FA "trust browser" step. |
| `launch_notes.py` | Parses internal book "launch notes" and updates the **Firebrand** title-management system via Selenium. |
| `AIAgentFlowchart.drawio` | Flowchart of the decision/agent logic. |

## Notes on the code

- **Selenium-heavy.** Most integrations are browser automations because the underlying systems
  have no APIs — so the scripts drive real login pages and forms. The deliberate `time.sleep()`
  calls and long waits are where a human reviews or completes a step.
- **LLM for a fuzzy sub-problem.** Address classification doesn't reduce cleanly to rules
  (foreign vs. Canadian vs. odd domestic formats), so it's delegated to a model.
- **Spreadsheet as the source of truth / state machine.** Completion is tracked via cell
  highlighting (done) vs. borders (partial), which `helpers.py` reads back on the next run.

## Security

Originally this code hard-coded live credentials and real recipient data inline. For this
public, showcase version:

- All API keys and logins are read from environment variables (`os.getenv(...)`); none are stored
  in the repo. See `.env.example` for the expected variable names.
- Real customer PII and internal/unpublished book data in examples and sample files were replaced
  with fictional placeholders.
