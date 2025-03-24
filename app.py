from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

app = Flask(__name__)

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-pro')

def get_crypto_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/predict', methods=['POST'])
def predict_crypto():
    try:
        data = request.json
        crypto_symbol = data.get('symbol', 'bitcoin')
        timeframe = data.get('timeframe', '24h')

        current_price = get_crypto_price(crypto_symbol)
        current_usd = current_price[crypto_symbol]['usd']
        
        prompt = f"""
        Based on the current market conditions and historical patterns:
        - Cryptocurrency: {crypto_symbol}
        - Current Price: ${current_usd}
        - Timeframe: {timeframe}
        
        Provide a price prediction analysis and potential price range for {crypto_symbol} in the next {timeframe}.
        Include hourly price predictions for the next 24 hours.
        Format the response as JSON with fields: 
        - predicted_range_low (number)
        - predicted_range_high (number)
        - confidence_level (string)
        - hourly_predictions (array of 24 price predictions)
        - analysis (string)
        """

        response = model.generate_content(prompt)
        
        import re
        import json
        
        json_match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
        prediction_data = json.loads(json_match.group(1)) if json_match else {}
        
        chart_data = {
            'current_price': current_usd,
            'predicted_range': {
                'low': prediction_data.get('predicted_range_low'),
                'high': prediction_data.get('predicted_range_high')
            },
            'hourly_predictions': prediction_data.get('hourly_predictions', []),
            'confidence_level': prediction_data.get('confidence_level'),
            'analysis': prediction_data.get('analysis'),
            'timestamp': datetime.now().isoformat(),
            'timeframe': timeframe,
            'symbol': crypto_symbol
        }

        return jsonify({
            'status': 'success',
            'data': chart_data
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=False)