# Financial Regret Simulator - Project Plan

## 1) Project Goal
Build a Flask web app that converts a user financial decision into a clear, surprising regret insight and a regret score (0–100), using opportunity cost and behavior factors.

### Primary outcome
- User enters one or more purchases/expenses.
- App computes for each purchase:
  - cumulative amount spent over time (if recurring),
  - cumulative growth if that amount had instead been invested in crypto over the same period,
  - opportunity cost difference (spent vs invested),
  - behavioral/context metrics.
- Outputs include per-purchase growth chart or summary and aggregate cumulative regret insights.
- Show meaningful output: "What this could have become" and a regret summary with a weighted regret score.

## 2) MVP Feature Set (Due in first iteration)
1. Flask web app with at least:
   - Home route (`/`) with input form
   - Result route (`/result`) displays insights and score
2. Parser for user input to extract numeric amount, frequency, category.
3. Regret calculation formula using at least 2 factors:
   - Opportunity cost vs 8% stock return (or API inflation)
   - Recurring cost multiplier (monthly/annual frequency)
4. UI templates: `index.html`, `result.html`, base styling.
5. SQLite + SQLAlchemy model for storing history (input, score, timestamp).
6. External API integration (example: Frankfurter currency rates or CoinGecko crypto prices).
7. README updates and clear usage instructions.

## 3) Architecture and Components
- `app.py`:
  - Flask app factory (or single app), forms input handling, routes.
  - Database setup (SQLAlchemy) and persistence.
  - API client call (service wrapper). 
- `models.py`:
  - `RegretRecord` with fields: id, raw_text, amount, category, score, created_at.
- `utils.py`:
  - Helpers: parse sentences, convert frequencies, compute compound growth.
  - `compute_regret_score` formula.
- `instance/services/api_client.py`:
  - External API fetch functions (currency rate, crypto/stock price).
- `templates/`:
  - `base.html`, `index.html`, `result.html` with Jinja and summary cards.

## 4) Regret Scoring Formula (Example)
Use dynamic factors from input:
- `base_opportunity_cost = amount * ((1 + r)^n - 1)`
- `frequency_factor` for recurring costs
- `behavior_factor` (luxury weight, recurring weight, volatility risk)

Example score formula:

```
regret_raw = opportunity_cost / amount
score = min(100, round(25*behavior_weight + 50*opportunity_cost_ratio + 25*risk_multiplier))
```

This ensures 2+ factors and a normalized 0–100 output.

## 5) Implementation Plan (2-day sprint)
### Day 1: Core app + calculations
- [ ] Set up Flask app and routes
- [ ] Build input form and result page templates
- [ ] Implement parsing + simple regret formula
- [ ] Add SQLite model and store each request
- [ ] Add basic style

### Day 2: API + polish + demo
- [ ] Add external API call (Frankfurter or CoinGecko)
- [ ] Use API data in regret calculation (exchange/inflation)
- [ ] Improve scoring interpretation text and categories
- [ ] Add input history + quick reset
- [ ] Test with sample scenarios, fix bugs
- [ ] Write README + quick demo script

## 6) Acceptance Criteria
- [ ] User can submit decision and get a regret score and narrative.
- [ ] Score is computed using at least 2 distinct factors.
- [ ] At least one external API is called with real-time data.
- [ ] Data stored in SQLite and can be viewed in app (or logs).
- [ ] Demo is ready with at least three example inputs.

## 7) Risks and Mitigations
- API downtime: fallback default constants (8% return, 4% inflation).
- Parsing edge cases: add safe fallback for numeric extraction and user guidance.
- Score too extreme: clamp to 0–100 and add category labels.

## 8) Next Steps
1. Build `app.py` + templates from `regret.md` requirements.
2. Add API client and test one endpoint.
3. Run app locally and verify with sample inputs.
4. Record quick demo script in README.
