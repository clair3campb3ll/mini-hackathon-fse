import json
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from services.api_client import CryptoCompareClient
from utils import parse_amount_frequency, compute_future_value, compute_regret_score

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///regret.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class RegretRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    raw_text = db.Column(db.String(512))
    amount = db.Column(db.Float)
    frequency = db.Column(db.String(32))
    years = db.Column(db.Float)
    crypto_symbol = db.Column(db.String(16))
    spent_total = db.Column(db.Float)
    invested_value = db.Column(db.Float)
    regret_score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

crypto_client = CryptoCompareClient()

@app.template_filter('currency')
def currency_filter(value):
    return f"R{value:,.0f}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        decision = request.form.get('decision', '').strip()
        amount_raw = request.form.get('amount', '').strip()
        frequency = request.form.get('frequency', 'one-time')
        years = float(request.form.get('years', 1))
        crypto_symbol = request.form.get('crypto_symbol', 'BTC').upper()

        amount, parsed_freq = parse_amount_frequency(amount_raw or decision, frequency)
        frequency = parsed_freq
        if amount <= 0:
            return render_template('index.html', error='Enter a valid numeric amount')

        cagr = crypto_client.fetch_annual_crypto_cagr(crypto_symbol) or 0.20
        spent_total = compute_future_value(amount, frequency, years, contributions=False)
        invested_value = compute_future_value(amount, frequency, years, rate=cagr, contributions=True)
        regret_score = compute_regret_score(spent_total, invested_value, frequency, cagr)

        record = RegretRecord(
            raw_text=decision or f'{amount} {frequency}',
            amount=amount,
            frequency=frequency,
            years=years,
            crypto_symbol=crypto_symbol,
            spent_total=spent_total,
            invested_value=invested_value,
            regret_score=regret_score,
        )
        db.session.add(record)
        db.session.commit()
        return redirect(url_for('result', record_id=record.id))

    return render_template('index.html')

@app.route('/result')
def result():
    record_id = request.args.get('record_id', type=int)
    record = RegretRecord.query.get(record_id)
    if not record:
        return redirect(url_for('index'))

    totals = db.session.query(
        db.func.sum(RegretRecord.spent_total),
        db.func.sum(RegretRecord.invested_value)
    ).first()
    total_spent = totals[0] or 0
    total_invested = totals[1] or 0
    total_opportunity_cost = total_invested - total_spent

    if record.regret_score <= 20:
        category = 'Probably fine'
    elif record.regret_score <= 50:
        category = 'Mild regret'
    elif record.regret_score <= 80:
        category = 'Risky decision'
    else:
        category = 'High regret'

    # Build year-by-year chart data
    cagr_val = round(crypto_client.fetch_annual_crypto_cagr(record.crypto_symbol) or 0.20, 4)
    n_years = max(1, int(record.years))
    chart_years = list(range(0, n_years + 1))
    chart_spent_data = [0.0]
    chart_invested_data = [0.0]
    for y in range(1, n_years + 1):
        s = compute_future_value(record.amount, record.frequency, y, contributions=False)
        iv = compute_future_value(record.amount, record.frequency, y, rate=cagr_val, contributions=True)
        chart_spent_data.append(round(s, 2))
        chart_invested_data.append(round(iv, 2))

    chart_data = json.dumps({
        'years': chart_years,
        'spent': chart_spent_data,
        'invested': chart_invested_data,
        'regret_score': record.regret_score,
        'spent_total': round(record.spent_total, 2),
        'invested_value': round(record.invested_value, 2),
        'opportunity_cost': round(max(0, record.invested_value - record.spent_total), 2),
    })

    return render_template('result.html', record=record, total_spent=total_spent,
                           total_invested=total_invested,
                           total_opportunity_cost=total_opportunity_cost,
                           category=category,
                           cagr=cagr_val,
                           chart_data=chart_data)

if __name__ == '__main__':
    app.run(debug=True)
