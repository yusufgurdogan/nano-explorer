from flask import Flask, render_template, request
import requests
from datetime import datetime

app = Flask(__name__)

# Public Nano Node API endpoint
NANO_NODE_API = 'https://node.somenano.com/proxy'

# Headers for the API requests
HEADERS = {
    'Content-Type': 'application/json'
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query'].strip()
        if search_query.startswith('nano_'):
            return account_info(search_query)
        elif len(search_query) == 64:
            return block_info(search_query)
        else:
            error = "Invalid Nano account or block hash."
            return render_template('index.html', error=error)
    return render_template('index.html')

def account_info(account):
    # Fetch account info
    account_payload = {
        "action": "account_info",
        "account": account,
        "representative": "true",
        "weight": "true",
        "pending": "true",
        "include_confirmed": "true",
        "receivable": "true"
    }
    account_response = requests.post(NANO_NODE_API, json=account_payload, headers=HEADERS)
    account_data = account_response.json()
    if 'error' in account_data:
        error = account_data['error']
        return render_template('account.html', error=error)
    
    # Fetch recent transactions
    history_payload = {
        "action": "account_history",
        "account": account,
        "count": "10",
        "include_only_confirmed": "true"
    }
    history_response = requests.post(NANO_NODE_API, json=history_payload, headers=HEADERS)
    history_data = history_response.json()
    if 'error' in history_data:
        history = []
    else:
        history = history_data.get('history', [])
    
    return render_template('account.html', account=account, data=account_data, history=history)

@app.route('/block/<block_hash>')
def block_info_route(block_hash):
    return block_info(block_hash)

def block_info(block_hash):
    payload = {
        "action": "block_info",
        "json_block": "true",
        "hash": block_hash
    }
    response = requests.post(NANO_NODE_API, json=payload, headers=HEADERS)
    data = response.json()
    if 'error' in data:
        error = data['error']
        return render_template('block.html', error=error)
    return render_template('block.html', block_hash=block_hash, data=data)

# Custom filter to convert RAW to NANO
@app.template_filter('humanize_nano')
def humanize_nano(raw_amount):
    try:
        return int(raw_amount) / 1e30
    except (ValueError, TypeError):
        return 0

# Custom filter to format timestamps
@app.template_filter('format_timestamp')
def format_timestamp(timestamp):
    if timestamp == '0' or timestamp is None:
        return 'N/A'
    else:
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            return 'Invalid Timestamp'

if __name__ == '__main__':
    app.run(debug=True)
