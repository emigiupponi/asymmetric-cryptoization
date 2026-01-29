# Asymmetric Cryptoization Dashboard

Interactive dashboard showing crypto-asset preferences across Advanced Economies (AEs) and Emerging Markets (EMDEs).

## Deploy to Render

1. Create a new Web Service on [Render](https://render.com)
2. Connect your GitHub repo or upload this folder
3. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server --bind 0.0.0.0:$PORT`
   - **Python Version**: 3.11

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:8050

## Data

The `data/monthly_data.csv` file contains pre-processed monthly volumes by region and crypto type.
