@app.route('/')
def home():
    opportunities = get_arbitrage_opportunities()
    return f'''
        <h1>Arbitrage Opportunities</h1>
        <table>
            <tr>
                <th>Exchange</th>
                <th>Coin Pair</th>
                <th>Bid Price</th>
                <th>Ask Price</th>
                <th>Spread</th>
                <th>Volume</th>
            </tr>
            {''.join([
                f'<tr><td>{opportunity["exchange"]}</td><td>{opportunity["coin_pair"]}</td><td>{







