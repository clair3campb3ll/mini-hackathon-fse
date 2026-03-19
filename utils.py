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


def compute_future_value(amount: float, frequency: str, years: float, rate: float = 0.10, contributions: bool = True):
    if years <= 0:
        years = 1
    if frequency == 'daily':
        n = 365
    elif frequency == 'weekly':
        n = 52
    elif frequency == 'monthly':
        n = 12
    else:
        n = 1

    if contributions:
        periodic_rate = rate / n
        contributions_per_period = amount
        periods = int(n * years)
        if rate == 0:
            return contributions_per_period * periods
        value = contributions_per_period * (((1 + periodic_rate) ** periods - 1) / periodic_rate)
        return value
    else:
        if frequency in ['daily', 'weekly', 'monthly']:
            total = amount * n * years
            return total
        return amount


def compute_regret_score(spent: float, invested: float, frequency: str, growth_rate: float):
    if spent <= 0:
        return 0
    opportunity_diff = max(0, invested - spent)
    base_ratio = opportunity_diff / spent
    frequency_factor = {'daily': 1.25, 'weekly': 1.15, 'monthly': 1.1, 'one-time': 1.0}.get(frequency, 1.0)
    risk_factor = min(1.0, max(0.05, abs(growth_rate)))

    raw = 40 * base_ratio + 30 * frequency_factor + 30 * risk_factor
    score = int(min(100, max(0, raw * 10)))
    return score
