# Customer Feedback & Support Ticket Analyzer

## How it works

This Python proof of concept reads tickets from a local CSV and filters greetings and promotional messages. For valid messages, it uses Gemini to assign a category, priority, sentiment, product or feature, and short suggested reply when `GEMINI_API_KEY` is configured. If the key is missing or a Gemini request fails, local text rules and reply templates provide the fallback. The output records whether each result came from Gemini, local rules, or the filter.

## Run

Requires Python 3. Run locally without Gemini:

```bash
python analyzer.py --local-only
```

This reads `sample_tickets.csv` and creates `analysis_results.csv`. To enable Gemini, create an API key in [Google AI Studio](https://aistudio.google.com/apikey), then set it in PowerShell and run the analyzer:

```bash
$env:GEMINI_API_KEY = "your-api-key"
python analyzer.py
```

Gemini uses the `gemini-flash-latest` model alias by default. Google may change which model that alias points to; available models and free-tier quotas depend on the Google AI Studio project. Set `GEMINI_MODEL` to select another available model. Temporary API errors are retried twice; persistent errors are shown in the console and local rules are used for that ticket. To analyze another CSV, pass its path and the desired output path:

```bash
python analyzer.py input.csv output.csv
```

The input CSV must have `ticket_id` and `message` columns. Gemini requests use Python's standard library, so no additional package is required. Keep the API key in the environment variable; never put it in the source code, CSV, or a shared message. If a key is exposed, revoke it and create a replacement. When Gemini is enabled, qualifying ticket text is sent to Google's Gemini API; do not submit private customer data unless you are allowed to share it. See Google's [model list](https://ai.google.dev/gemini-api/docs/models) and [billing and free-tier details](https://ai.google.dev/gemini-api/docs/billing).
