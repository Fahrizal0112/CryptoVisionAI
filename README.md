# Crypto Price Prediction API with Gemini AI 🚀

This application is a backend service that utilizes Gemini AI to predict cryptocurrency prices. The API combines real-time price data from CoinGecko with AI analysis to provide cryptocurrency price predictions across various timeframes.

## 🌟 Features

- Cryptocurrency price prediction using Gemini AI
- Real-time price data from CoinGecko API
- Hourly predictions for the next 24 hours
- Market sentiment analysis
- Data visualization using Chart.js
- REST API endpoints

## 🛠️ Technologies Used

- Python 3.8+
- Flask
- Google Generative AI (Gemini)
- CoinGecko API
- Chart.js
- Postman (for testing)

## 📋 Prerequisites

Before running the application, ensure you have:

- Python 3.8 or newer
- Gemini AI API key
- pip (Python package manager)

## ⚙️ Installation

1. Clone this repository
```bash
git clone https://github.com/username/crypto-prediction-api.git
cd crypto-prediction-api
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # For Linux/Mac
# or
venv\Scripts\activate  # For Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create `.env` file and fill in your API key
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## 🚀 How to Run

1. Activate virtual environment (if not already activated)
```bash
source venv/bin/activate  # For Linux/Mac
# or
venv\Scripts\activate  # For Windows
```

2. Run the application
```bash
python app.py
```

The server will run at `http://localhost:5000`

## 📌 API Usage

### Prediction Endpoint

**POST** `/predict`

Request body:
```json
{
    "symbol": "bitcoin",
    "timeframe": "24h"
}
```

Response:
```json
{
    "status": "success",
    "data": {
        "current_price": 86945,
        "predicted_range": {
            "low": 85500,
            "high": 88500
        },
        "hourly_predictions": [...],
        "confidence_level": "medium",
        "analysis": "...",
        "timestamp": "2024-03-14T10:30:00.000Z",
        "timeframe": "24h",
        "symbol": "bitcoin"
    }
}
```

## 📊 Data Visualization

To view data visualization:

1. Open `index.html` in your browser
2. Ensure the backend server is running
3. The chart will automatically load the latest prediction data

## 🧪 Testing

You can use the provided Postman Collection for testing:

1. Import the `crypto_prediction_postman.json` file into Postman
2. Set environment variables if needed
3. Run the test collection

## 📝 Response Format Details

The API response includes:
- Current price
- Predicted price range (high and low)
- Hourly predictions for 24 hours
- Confidence level of prediction
- Market analysis
- Timestamp and metadata

## 🔒 Security Considerations

- API key must be stored securely in `.env` file
- Implement rate limiting for production use
- Add authentication for public deployment
- Validate all input data

## 🚧 Error Handling

The API includes error handling for:
- Invalid cryptocurrency symbols
- API service disruptions
- Invalid request formats
- Server errors

## 🔄 Future Improvements

- Add support for more cryptocurrencies
- Implement historical prediction accuracy tracking
- Add more technical indicators
- Create WebSocket support for real-time updates
- Implement caching for API responses

## 📜 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## ⚠️ Disclaimer

This application is for educational purposes only. Cryptocurrency predictions are inherently uncertain and should not be used as the sole basis for investment decisions. Always conduct thorough research and consult with financial advisors before making any investment decisions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 Contact

Your Name - [@your_twitter](https://twitter.com/your_twitter) - email@example.com

Project Link: [https://github.com/username/crypto-prediction-api](https://github.com/username/crypto-prediction-api)

## 🙏 Acknowledgments

- [Gemini AI](https://deepmind.google/technologies/gemini/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Chart.js](https://www.chartjs.org/)
- [Flask](https://flask.palletsprojects.com/)
