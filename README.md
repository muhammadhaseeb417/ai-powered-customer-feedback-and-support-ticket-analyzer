# Customer Feedback & Support Ticket Analyzer

## How it works

This Python proof of concept reads tickets from a local CSV, ignores greetings and promotional messages, then assigns a category, priority, sentiment, product or feature, and suggested reply to each valid message. It writes all results, including ignored tickets, to a second CSV. The analyzer uses lightweight text rules and reply templates, so its results are deterministic and run locally.

## Run

Requires Python 3. Run from this folder:

```bash
python analyzer.py
```

This reads `sample_tickets.csv` and creates `analysis_results.csv`. To use another input and output file:

```bash
python analyzer.py input.csv output.csv
```

The input CSV must have `ticket_id` and `message` columns. No third-party packages, API key, or model download is required.

## AI model

The assignment does not require a specific LLM or model. This PoC uses local text classification rules and tailored reply templates rather than an LLM. An LLM could improve interpretation of varied wording and generate more natural replies, but it would require a model or API configuration.
