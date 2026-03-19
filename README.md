# Financial Regret Simulator

Run the app:

```bash
cd "mini-hackathon-fse"
python -m pip install -r requirements.txt
flask --app app run --debug --port 5001
```

Open `http://127.0.0.1:5001/`.

Enter purchase amount and frequency; the app uses CryptoCompare historical data for crypto CAGR and computes cumulative spent vs invested value.
