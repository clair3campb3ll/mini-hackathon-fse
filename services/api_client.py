import requests

class CryptoCompareClient:
    BASE_URL = 'https://min-api.cryptocompare.com'

    def fetch_current_price(self, symbol: str, currency: str = 'USD'):
        url = f'{self.BASE_URL}/data/price'
        params = {'fsym': symbol.upper(), 'tsyms': currency.upper()}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json().get(currency.upper())
        except Exception:
            return None

    def fetch_annual_crypto_cagr(self, symbol: str = 'BTC', base='USD', days=365):
        url = f'{self.BASE_URL}/data/v2/histoday'
        params = {'fsym': symbol.upper(), 'tsym': base.upper(), 'limit': days, 'aggregate': 1}
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json().get('Data', {}).get('Data', [])
            if len(data) < 2:
                return None
            start = data[0].get('close')
            end = data[-1].get('close')
            if not start or not end or start <= 0:
                return None
            years = days / 365
            return (end / start) ** (1 / years) - 1
        except Exception:
            return None
