import ccxt
import os
from flask import Flask, jsonify

exchanges = ['binance', 'bitfinex', 'bitstamp', 'huobipro', 'okex', 'bitmex', 'bittrex', 'poloniex', 'kucoin', 'gateio', 'ftx', 'deribit', 'bybit', 'phemex', 'mxc', 'hitbtc', 'bibox', 'bitmax']
coins = ['BTC/USDT', 'ETH/USDT', 'ADA/USDT', 'SOL/USDT', 'DOT/USDT', 'DOGE/USDT', 'XRP/USDT', 'LUNA/USDT', 'AVAX/USDT', 'MATIC/USDT', 'SUSHI/USDT', 'LINK/USDT', 'CRV/USDT', 'AAVE/USDT', 'CAKE/USDT', 'GRT/USDT', 'ALGO/USDT', 'SNX/USDT', 'XTZ/USDT', 'REN/USDT', 'ATOM/USDT', 'RUNE/USDT', 'KSM/USDT', 'FIL/USDT', 'ANKR/USDT', 'KAVA/USDT', 'CHZ/USDT', 'OMG/USDT', 'BTT/USDT', 'IOST/USDT', 'ZIL/USDT']

app = Flask(__name__)

@app.route('/')
def home():
    try:
        opportunities = get_arbitrage_opportunities()
        table = '<table><tr><th>Exchange</th><th>Coin Pair</th><th>Bid Price</th><th>Ask Price</th><th>Spread</th><th>Volume</th></tr>'
        for opportunity in opportunities:
            table += f'<tr><td>{opportunity["exchange"]}</td><td>{opportunity["coin_pair"]}</td><td>{opportunity["bid_price"]}</td><td>{opportunity["ask_price"]}</td><td>{opportunity["spread"]}</td><td>{opportunity["volume"]}</td></tr>'
        table += '</table>'
        return f'<h1>Arbitrage Opportunities</h1>{table}'
    except Exception as e:
        return jsonify({'error': str(e)})

def get_arbitrage_opportunities():
    opportunities = []
    for exchange_name in exchanges:
        exchange = getattr(ccxt, exchange_name)()
        for coin_pair in coins:
            try:
                ticker = exchange.fetch_ticker(coin_pair)
                bid_price = ticker['bid']
                ask_price = ticker['ask']
                spread = ask_price - bid_price
                if spread > 0:
                    opportunity = {
                        'exchange': exchange_name,
                        'coin_pair': coin_pair,
                        'bid_price': bid_price,
                        'ask_price': ask_price,
                        'spread': spread,
                        'volume': ticker['quoteVolume'],
                    }
                    opportunities.append(opportunity)
            except Exception as e:
                print(f'Error fetching {coin_pair} on {exchange_name}: {str(e)}')
    return opportunities

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
