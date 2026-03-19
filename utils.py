import re

FREQUENCY_MAP = {
    'daily': ('daily', 365),
    'weekly': ('weekly', 52),
    'monthly': ('monthly', 12),
    'yearly': ('yearly', 1),
    'once': ('one-time', 1),
    'one-time': ('one-time', 1),
    'one time': ('one-time', 1),
    'single': ('one-time', 1),
}

PERIODS_PER_YEAR = {'daily': 365, 'weekly': 52, 'monthly': 12}


def parse_amount_frequency(amount_text: str, frequency: str = 'one-time'):
    digits = re.findall(r"[0-9]+(?:\.[0-9]+)?", amount_text.replace(',', ''))
    amount = float(digits[0]) if digits else 0.0

    frequency = frequency.lower().strip()
    for key in FREQUENCY_MAP:
        if key in frequency:
            return amount, FREQUENCY_MAP[key][0]
    for key in FREQUENCY_MAP:
        if key in amount_text.lower():
            return amount, FREQUENCY_MAP[key][0]
    return amount, 'one-time'


def compute_future_value(amount: float, frequency: str, years: float,
                         rate: float = 0.10, contributions: bool = True):
    """
    Compute future value of spending or investing.

    contributions=False  → total cash outflow (no growth, linear for recurring)
    contributions=True   → future value if invested at the given annual rate

    Formulas used:
      - One-time lump sum:  FV = PV * (1 + r)^t
      - Regular annuity:    FV = PMT * ((1 + r_p)^N - 1) / r_p
        where r_p = (1 + r_annual)^(1/n) - 1  [geometrically correct periodic rate]
    """
    if years <= 0:
        return 0.0

    is_recurring = frequency in PERIODS_PER_YEAR

    if not contributions:
        # Total cash spent — no investment growth applied
        if is_recurring:
            n = PERIODS_PER_YEAR[frequency]
            return amount * n * years          # linear accumulation
        return amount                          # one-time: spent once, fixed

    # ── Invested value ──
    if not is_recurring:
        # Lump-sum compound growth: FV = PV * (1 + r)^t
        return amount * (1 + rate) ** years

    # Regular contributions annuity
    n = PERIODS_PER_YEAR[frequency]
    # Geometrically correct periodic rate (not simple rate/n)
    periodic_rate = (1 + rate) ** (1 / n) - 1
    periods = int(n * years)
    if periods == 0:
        return 0.0
    if periodic_rate == 0:
        return amount * periods
    # Standard future-value-of-annuity formula
    return amount * (((1 + periodic_rate) ** periods - 1) / periodic_rate)


def generate_chart_data(amount: float, frequency: str, total_years: int, cagr: float):
    """
    Build time-series arrays for the growth chart with adaptive resolution:
      - ≤ 2 years  → monthly data points  (smooth curve for short horizons)
      - ≤ 10 years → quarterly data points
      - > 10 years → yearly data points
    Returns (labels, spent_series, invested_series).
    """
    n = max(1, total_years)

    if n <= 2:
        total_steps = n * 12
        steps = [round(m / 12, 6) for m in range(total_steps + 1)]
        labels = []
        for m in range(total_steps + 1):
            if m == 0:
                labels.append("Start")
            elif m % 12 == 0:
                labels.append(f"Yr {m // 12}")
            else:
                labels.append(f"{m}M")
    elif n <= 10:
        total_steps = n * 4
        steps = [round(q / 4, 6) for q in range(total_steps + 1)]
        labels = []
        for q in range(total_steps + 1):
            if q == 0:
                labels.append("Start")
            elif q % 4 == 0:
                labels.append(f"Yr {q // 4}")
            else:
                yr, qtr = divmod(q, 4)
                labels.append(f"Y{yr + 1}Q{qtr}")
    else:
        steps = list(range(n + 1))
        labels = ["Start"] + [f"Yr {y}" for y in range(1, n + 1)]

    spent_series = []
    invested_series = []
    for y in steps:
        if y == 0:
            spent_series.append(0.0)
            invested_series.append(0.0)
        else:
            spent_series.append(round(compute_future_value(amount, frequency, y, contributions=False), 2))
            invested_series.append(round(compute_future_value(amount, frequency, y, rate=cagr, contributions=True), 2))

    return labels, spent_series, invested_series


def compute_regret_score(spent: float, invested: float, frequency: str, growth_rate: float):
    """
    Score breakdown (sums to 100 max):
      - Growth gap (60 pts): how much more the invested value is vs spent
      - Habit tax  (25 pts): penalty for recurring frequency
      - Crypto heat (15 pts): how fast the chosen crypto grows
    """
    if spent <= 0:
        return 0

    # Growth gap: invested/spent multiplier, capped at 3x (=60 pts)
    multiplier = invested / spent
    opp_score = min(60, max(0, (multiplier - 1) * 30))

    # Habit tax: recurring spending compounds regret
    freq_score = {'daily': 25, 'weekly': 15, 'monthly': 10, 'one-time': 0}.get(frequency, 0)

    # Crypto heat: higher CAGR = higher regret for not investing
    risk_score = min(15, abs(growth_rate) * 50)

    return int(min(100, max(0, opp_score + freq_score + risk_score)))
