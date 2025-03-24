from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/predict": {
        "origins": [
            "http://localhost:3000",
            "https://846c-182-54-141-154.ngrok-free.app"
        ],
        "methods": ["POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-pro')

def get_crypto_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_historical_prices(symbol, hours=6):
    """Get historical hourly prices for the last N hours"""
    # Map untuk ID CoinGecko yang benar
    coin_id_map = {
        'bitcoin': 'bitcoin',
        'ethereum': 'ethereum',
        'dogecoin': 'dogecoin',
        # tambahkan crypto lain jika diperlukan
    }
    
    coin_id = coin_id_map.get(symbol.lower())
    if not coin_id:
        print(f"Invalid coin symbol: {symbol}")
        return []

    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': '0.25',  # 6 hours = 0.25 days
        'interval': 'hourly'
    }
    
    try:
        print(f"Fetching historical prices for {coin_id}")
        print(f"URL: {url}")
        print(f"Params: {params}")
        
        response = requests.get(url, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'prices' not in data:
                print(f"No prices in response: {data}")
                return []
                
            prices = data['prices']
            print(f"Retrieved {len(prices)} price points")
            
            # Ensure we have exactly 6 hours of data
            prices = prices[-hours:] if len(prices) >= hours else prices
            
            historical_data = []
            for timestamp, price in prices:
                dt = datetime.fromtimestamp(timestamp/1000)
                historical_data.append({
                    'timestamp': dt.strftime('%Y-%m-%dT%H:%M:%S'),
                    'price': round(price, 6)
                })
            
            print(f"Processed historical data: {historical_data}")
            return historical_data
        else:
            print(f"Error response from CoinGecko: {response.status_code}")
            print(f"Response content: {response.text}")
            
            # Attempt alternative endpoint
            return get_historical_prices_alternative(symbol, hours)
            
    except Exception as e:
        print(f"Error fetching historical prices: {str(e)}")
        return get_historical_prices_alternative(symbol, hours)
    
    return []

def get_historical_prices_alternative(symbol, hours=6):
    """Alternative method to get historical prices using different endpoint"""
    try:
        # Using simple/price endpoint with alternative method
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': symbol.lower(),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_last_updated_at': 'true'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            current_price = data[symbol.lower()]['usd']
            last_updated = data[symbol.lower()]['last_updated_at']
            
            # Generate synthetic historical data based on 24h change
            change_24h = data[symbol.lower()].get('usd_24h_change', 0)
            price_change_per_hour = change_24h / 24
            
            historical_data = []
            for i in range(hours):
                hour_timestamp = last_updated - (3600 * (hours - i))
                estimated_price = current_price * (1 - (price_change_per_hour * (hours - i) / 100))
                
                historical_data.append({
                    'timestamp': datetime.fromtimestamp(hour_timestamp).strftime('%Y-%m-%dT%H:%M:%S'),
                    'price': round(estimated_price, 6)
                })
            
            return historical_data
            
    except Exception as e:
        print(f"Error in alternative price fetch: {str(e)}")
        return []

@app.route('/predict', methods=['POST'])
def predict_crypto():
    try:
        data = request.json
        crypto_symbol = data.get('symbol', 'bitcoin')
        timeframe = data.get('timeframe', '24h')

        # Get current price with error handling
        current_price = get_crypto_price(crypto_symbol)
        if not current_price:
            return jsonify({
                'status': 'error',
                'message': 'Failed to get current price'
            }), 500
            
        current_usd = current_price[crypto_symbol]['usd']
        
        # Get historical prices with detailed logging
        print(f"\nFetching historical prices for {crypto_symbol}")
        historical_prices = get_historical_prices(crypto_symbol, 6)
        print(f"Retrieved historical prices: {historical_prices}")
        
        if not historical_prices:
            print("Warning: No historical prices found, using alternative method")
            historical_prices = get_historical_prices_alternative(crypto_symbol, 6)

        # Prepare prompt for Gemini
        prompt = f"""
        Based on the current market conditions and historical patterns:
        - Cryptocurrency: {crypto_symbol}
        - Current Price: ${current_usd}
        - Timeframe: {timeframe}
        - Last 6 hours prices: {[h['price'] for h in historical_prices]}
        
        Provide a price prediction analysis and potential price range for {crypto_symbol} in the next {timeframe}.
        Format the response as JSON with fields: 
        - predicted_range_low (number)
        - predicted_range_high (number)
        - confidence_level (string)
        - market_sentiment (string: "BULLISH", "BEARISH", or "NEUTRAL")
        - sentiment_strength (number: 1-10, where 1 is weakest and 10 is strongest)
        - key_indicators (array of strings with technical indicators supporting the sentiment)
        - hourly_predictions (array of 24 price predictions)
        - analysis (string)
        - support_levels (array of numbers)
        - resistance_levels (array of numbers)
        """

        # Generate prediction using Gemini
        response = model.generate_content(prompt)
        
        # Parse the response text to extract JSON
        import re
        import json
        
        # Extract JSON string from the response
        json_match = re.search(r'```json\n(.*?)\n```', response.text, re.DOTALL)
        prediction_data = json.loads(json_match.group(1)) if json_match else {}
        
        # Calculate trend strength and direction
        def calculate_trend_metrics(hourly_predictions, current_price):
            if not hourly_predictions:
                return None
            
            price_changes = [
                ((next_price - current_price) / current_price) * 100 
                for next_price in hourly_predictions
            ]
            avg_change = sum(price_changes) / len(price_changes)
            
            return {
                'average_change_percentage': round(avg_change, 2),
                'trend_direction': 'BULLISH' if avg_change > 0 else 'BEARISH' if avg_change < 0 else 'NEUTRAL',
                'trend_strength': abs(round(avg_change, 2))  # Absolute value of average change
            }

        trend_metrics = calculate_trend_metrics(
            prediction_data.get('hourly_predictions', []), 
            current_usd
        )
        
        # Struktur data untuk chart dan analisis
        chart_data = {
            'current_price': current_usd,
            'historical_prices': historical_prices,
            'predicted_range': {
                'low': prediction_data.get('predicted_range_low'),
                'high': prediction_data.get('predicted_range_high')
            },
            'market_analysis': {
                'sentiment': prediction_data.get('market_sentiment', 'NEUTRAL'),
                'sentiment_strength': prediction_data.get('sentiment_strength', 5),
                'key_indicators': prediction_data.get('key_indicators', []),
                'support_levels': prediction_data.get('support_levels', []),
                'resistance_levels': prediction_data.get('resistance_levels', [])
            },
            'trend_analysis': trend_metrics,
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