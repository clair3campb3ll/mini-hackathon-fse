# Financial Regret Simulator

Run the app:

```bash
cd "mini-hackathon-fse"
python -m pip install -r requirements.txt
flask --app app run --debug --port 5000
```

Open `http://127.0.0.1:5000/`.

Enter purchase amount and frequency; the app uses CryptoCompare historical data for crypto CAGR and computes cumulative spent vs invested value.

## Deploy on Render
1. Push this repository to GitHub.
2. Go to Render and create a new Web Service.
3. Connect your GitHub repo and select the branch.
4. Set the environment to Python and use the default build command.
5. Add `render.yaml` to the repo (already included).
6. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`.

Render will build and deploy automatically.
