# Google Reviews AI Responder

Automated system that generates professional, personalized responses to Google Maps reviews using Claude AI.

## What it does

- Fetches all reviews from any Google Maps business automatically
- Generates unique, personalized responses for each review using AI
- Adapts tone based on star rating (positive, negative, neutral)
- Exports a clean Excel file ready to copy-paste into Google Business
- Saves client records for monthly maintenance runs

## Scripts

| Script | Purpose |
|--------|---------|
| `1_setup_completo.py` | First-time setup — fetches ALL historical reviews and generates responses |
| `2_mantenimiento.py` | Monthly maintenance — fetches only NEW reviews since last run |
| `google_reviews_responder.py` | Basic version — manual review input |

## How it works

```
Business name → Google Maps (SerpAPI) → All reviews extracted
→ Claude AI generates personalized response per review
→ Professional Excel file delivered to client
```

## Setup

### Requirements

```bash
pip install anthropic google-search-results openpyxl
```

### API Keys needed

- **Anthropic API key** — get it at console.anthropic.com
- **SerpAPI key** — get it at serpapi.com (100 free searches/month)

### Run

```powershell
$env:ANTHROPIC_API_KEY = "your-key"
$env:SERPAPI_KEY = "your-key"
python 1_setup_completo.py
```

## Example output

The script generates an Excel file with this structure:

| # | Stars | Author | Date | Customer Review | ✅ Response (copy-paste to Google) |
|---|-------|--------|------|-----------------|-----------------------------------|
| 1 | ⭐⭐⭐⭐⭐ | John D. | 2 days ago | Amazing food! | Thank you John!... |
| 2 | ⭐ | Maria S. | 1 week ago | Bad service... | We sincerely apologize... |

## Service model

This tool powers a **Reputation Management Service** for local businesses:

- **Setup** — process all historical unanswered reviews — one-time fee
- **Maintenance** — respond to new reviews every month — monthly retainer

Target clients: restaurants, hotels, retail stores, clinics — any business with a Google Maps presence.

## Tech stack

- Python 3.13
- [Anthropic Claude API](https://anthropic.com) — AI response generation
- [SerpAPI](https://serpapi.com) — Google Maps review extraction
- openpyxl — Excel export
- Google Business Profile API — automated publishing (coming soon)
