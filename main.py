from auto_config_loader import load_config_auto
from core.bot_runner import BinanceFuturesProBot
from dotenv import load_dotenv
import os
from binance.client import Client

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Real-time price fetch ===
def fetch_recent_prices(symbol: str, interval: str, limit: int = 60):
    """Fetch recent closing prices from Binance Futures public endpoint.

    Args:
        symbol (str): Trading pair symbol, e.g. "BTCUSDT".
        interval (str): Kline interval, e.g. "5m".
        limit (int): Number of klines to retrieve.

    Returns:
        list[float]: List of closing prices.
    """
    try:
        # Deteksi testnet atau real dari environment
        api_key = os.getenv("API_KEY", os.getenv("BINANCE_API_KEY", ""))
        is_testnet = "testnet" in api_key.lower() or len(api_key) < 50 if api_key else True
        
        client = Client(testnet=is_testnet)  # public endpoints do not require API keys
        klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
        return [float(kline[4]) for kline in klines]
    except Exception as e:
        print(f"[WARN] Failed to fetch prices from Binance Futures: {e}. Falling back to empty list.")
        return []

if __name__ == "__main__":
    # VPS Optimization - Set environment variables
    import os
    os.environ['PYTHONOPTIMIZE'] = '1'  # Enable Python optimizations
    os.environ['PYTHONUNBUFFERED'] = '1'  # Unbuffered output for better logging
    
    # Reduce logging verbosity untuk VPS
    import logging
    logging.getLogger('binance').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    
    config = load_config_auto(API_KEY, API_SECRET)

    # Handle case when config is None (no API keys)
    if config is None:
        print("[ERROR] Failed to load configuration. Please check your API keys in .env file.")
        print("[ERROR] Make sure API_KEY, API_SECRET, TELEGRAM_TOKEN, and TELEGRAM_CHAT_ID are set.")
        exit(1)

    # Inject Telegram config
    config['telegram'] = {
        'token': TELEGRAM_TOKEN,
        'chat_id': TELEGRAM_CHAT_ID
    }

    # === Enhanced Equity System Info ===
    if config.get('equity_trader'):
        equity_trader = config['equity_trader']
        print(f"[EQUITY] Enhanced system active!")
        print(f"[EQUITY] Risk Level: {equity_trader.risk_level}")
        print(f"[EQUITY] Base Risk: {equity_trader.base_risk_percent}%")
        print(f"[EQUITY] Leverage: {equity_trader.leverage}x")
        print(f"[EQUITY] Max Drawdown: {equity_trader.max_drawdown_percent}%")
    
    # === Kelly Sizing Activation ===
    if config.get("initial_balance", 0) >= 50:
        winrate = 0.75  # example fixed winrate
        tp = config.get("take_profit", {}).get("tp_percent", 1.5)
        sl = config.get("stop_loss", {}).get("sl_percent", 0.75)
        if sl > 0:
            rr = tp / sl
            # Kelly fraction calculation moved to position_sizing module
            if "position_sizing" in config:
                config["position_sizing"]["method"] = "kelly_partial"
            print(f"[DYNAMIC] Kelly sizing active for balance >= $50")

    # === Market Safety Check ===
    symbol = config.get("symbol")
    if not symbol and "symbols" in config:
        symbol = config["symbols"][0]  # Ambil symbol pertama jika hanya ada 'symbols'
    if not symbol:
        symbol = "BTCUSDT"  # Default fallback
        print(f"[WARN] No symbol specified, using default: {symbol}")
    
    print(f"[INFO] Starting bot with symbol: {symbol}")
    print(f"[INFO] Balance: ${config.get('initial_balance', 0):.2f}")
    print(f"[INFO] Max positions: {config.get('max_open_trades', 1)}")
    print(f"[INFO] Confidence threshold: {config.get('confidence_threshold', 70)}%")

    # Initialize and start the async trading bot with enhanced config
    import asyncio

    bot = BinanceFuturesProBot(config)
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        print("\nBot stopped by user")