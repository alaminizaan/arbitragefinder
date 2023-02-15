import ccxt
import os
from flask import Flask, jsonify

# Add your Binance API key and secret here
binance_api_key = 'vpKO1DecEFexXzX5gsfG8WEmHuH5DPeV4lYqFKBJGwmjeVoWwXMZjU4UFcqQFaba'
binance_secret = 'mnpTkA1KNYiDBpoUsiUjQGY3KUtPOxJHcad0aFVbvSF8h5imxhAaAcriP99oiMIi'

exchanges = [{'name': 'binance', 'api_key': binance_api_key, 'secret': binance_secret}, 
             {'name': 'bitstamp'}]
coins = ['BTC/USDT', 'ETH/USDT']

app = Flask(__name__)
def calculate_arbitrage_opportunity(exchange, coin_pair, fees):
    try:
        ticker = exchange.fetch_ticker(coin_pair)
    except Exception as e:
        return {'error': f'Failed to fetch ticker for {coin_pair} on {exchange.name}: {str(e)}'}
        
    quote_currency = exchange.markets[coin_pair]['quote']
    transaction_fee = fees['funding'].get('withdraw', {}).get(quote_currency, 0)
    trading_fee = (fees['trading']['maker'] + fees['trading']['taker']) / 2
    print("Bid price: ", ticker['bid'])
    bid_price_with_fees = ticker['bid'] * (1 + trading_fee) + transaction_fee
    print("Ask price: ", ticker['ask'])
    ask_price_with_fees = ticker['ask'] * (1 - trading_fee) - transaction_fee
    spread = ask_price_with_fees - bid_price_with_fees
    spread_percentage = (spread / bid_price_with_fees) * 100
    opportunity = {
        'exchange': exchange.name,
        'coin_pair': coin_pair,
        'bid_price': bid_price_with_fees,
        'ask_price': ask_price_with_fees,
        'spread': spread,
        'spread_percentage': spread_percentage,
        'volume': ticker['quoteVolume'],
    }
    return opportunity if spread > 0 else None

def get_arbitrage_opportunities():
    opportunities = []
    for exchange_data in exchanges:
        exchange_name = exchange_data['name']
        exchange = getattr(ccxt, exchange_name)({
            'apiKey': exchange_data.get('api_key', None),
            'secret': exchange_data.get('secret', None)
        })

        # Get fees for the exchange
        try:
            fees = exchange.fetch_fees()
        except Exception as e:
            opportunities.append({'error': f'Failed to fetch fees on {exchange.name}: {str(e)}'})
            continue

        for coin_pair in coins:
            opportunity = calculate_arbitrage_opportunity(exchange, coin_pair, fees)
            if 'error' in opportunity:
                opportunities.append(opportunity)
            elif opportunity:
                opportunities.append(opportunity)

    return opportunities
@app.route('/')
def home():
    try:
        opportunities = get_arbitrage_opportunities()
        if len(opportunities) == 0:
            return '<p>No arbitrage opportunities found</p>'
        table = '<table><tr><th>Exchange</th><th>Coin Pair</th><th>Bid Price</th><th>Ask Price</th><th>Spread</th><th>Spread Percentage</th><th>Volume</th><th>Error</th></tr>'
        for opportunity in opportunities:
            if 'error' in opportunity:
                table += f'<tr><td>{opportunity["exchange"]}</td><td>{opportunity["coin_pair"]}</td><td colspan="6"></td><td>{opportunity["error"]}</td></tr>'
            else:
                table += f'<tr><td>{opportunity["exchange"]}</td><td>{opportunity["coin_pair"]}</td><td>{opportunity["bid_price"]:.8f}</td><td>{opportunity["ask_price"]:.8f}</td><td>{opportunity["spread"]:.8f}</td><td>{opportunity["spread_percentage"]:.2f}%</td><td>{opportunity["volume"]:.8f}</td><td></td></tr>'
        table += '</table>'
        return table
    except Exception as e:
        return f'<p>An error occurred: {str(e)}</p>'
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

