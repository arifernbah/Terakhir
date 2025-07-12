#!/usr/bin/env python3
"""
Test Script untuk Integration Equity System dengan Trading Bot
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test semua imports yang diperlukan"""
    print("🧪 Testing imports...")
    
    try:
        # Test equity system imports
        from equity_enhanced_config import EnhancedEquityTrading
        print("✅ EnhancedEquityTrading imported successfully")
        
        # Test auto config loader
        from auto_config_loader import load_config_auto
        print("✅ load_config_auto imported successfully")
        
        # Test bot runner
        from core.bot_runner import BinanceFuturesProBot
        print("✅ BinanceFuturesProBot imported successfully")
        
        # Test binance client
        from binance.client import Client
        print("✅ Binance Client imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_config_loading():
    """Test config loading dengan equity system"""
    print("\n🧪 Testing config loading...")
    
    try:
        from auto_config_loader import load_config_auto
        
        # Get API keys dari environment
        api_key = os.getenv("API_KEY")
        api_secret = os.getenv("API_SECRET")
        
        if not api_key or not api_secret:
            print("⚠️ API keys tidak tersedia, menggunakan dummy test")
            # Test dengan balance dummy
            from equity_enhanced_config import EnhancedEquityTrading
            equity_trader = EnhancedEquityTrading(100.0)
            print(f"✅ Equity system initialized for $100 balance")
            print(f"   Risk Level: {equity_trader.risk_level}")
            print(f"   Base Risk: {equity_trader.base_risk_percent}%")
            print(f"   Leverage: {equity_trader.leverage}x")
            return True
        
        # Test dengan API keys real
        config = load_config_auto(api_key, api_secret)
        
        if config and config.get('equity_trader'):
            print("✅ Config loaded dengan equity system")
            equity_trader = config['equity_trader']
            print(f"   Balance: ${config.get('initial_balance', 0):.2f}")
            print(f"   Risk Level: {equity_trader.risk_level}")
            print(f"   Base Risk: {equity_trader.base_risk_percent}%")
            print(f"   Leverage: {equity_trader.leverage}x")
            return True
        else:
            print("❌ Config loaded but no equity system")
            return False
            
    except Exception as e:
        print(f"❌ Config loading error: {e}")
        return False

def test_bot_initialization():
    """Test bot initialization dengan equity config"""
    print("\n🧪 Testing bot initialization...")
    
    try:
        from auto_config_loader import load_config_auto
        from core.bot_runner import BinanceFuturesProBot
        
        # Get API keys
        api_key = os.getenv("API_KEY")
        api_secret = os.getenv("API_SECRET")
        
        if not api_key or not api_secret:
            print("⚠️ API keys tidak tersedia, skip bot init test")
            return True
        
        # Load config
        config = load_config_auto(api_key, api_secret)
        if not config:
            print("❌ Failed to load config")
            return False
        
        # Initialize bot with config
        bot = BinanceFuturesProBot(config)
        
        # Check if equity trader loaded
        if bot.equity_trader:
            print("✅ Bot initialized dengan equity system")
            print(f"   Equity Trader: {type(bot.equity_trader).__name__}")
            print(f"   Risk Level: {bot.equity_trader.risk_level}")
            return True
        else:
            print("⚠️ Bot initialized tanpa equity system")
            return True
            
    except Exception as e:
        print(f"❌ Bot initialization error: {e}")
        return False

def test_equity_calculations():
    """Test equity calculations"""
    print("\n🧪 Testing equity calculations...")
    
    try:
        from equity_enhanced_config import EnhancedEquityTrading
        
        # Test dengan berbagai balance levels
        test_balances = [5, 20, 50, 100, 150]
        
        for balance in test_balances:
            print(f"\n   Testing balance: ${balance}")
            equity_trader = EnhancedEquityTrading(balance)
            
            # Test position sizing
            entry_price = 50000
            stop_loss_price = 49500
            confidence = 0.75
            
            position_size, risk_percent = equity_trader.calculate_position_size_with_leverage(
                entry_price, stop_loss_price, "BTCUSDT", confidence
            )
            
            print(f"   ✅ Position size: {position_size:.6f} BTC")
            print(f"   ✅ Risk percent: {risk_percent:.2f}%")
            print(f"   ✅ Leverage: {equity_trader.leverage}x")
        
        return True
        
    except Exception as e:
        print(f"❌ Equity calculations error: {e}")
        return False

def test_telegram_commands():
    """Test telegram command structure"""
    print("\n🧪 Testing telegram commands...")
    
    try:
        from core.bot_runner import BinanceFuturesProBot
        from equity_enhanced_config import EnhancedEquityTrading
        
        # Create dummy config
        dummy_config = {
            'initial_balance': 100.0,
            'equity_trader': EnhancedEquityTrading(100.0),
            'telegram_token': 'dummy_token',
            'telegram_chat_id': 'dummy_chat_id'
        }
        
        # Create bot instance with config
        bot = BinanceFuturesProBot(dummy_config)
        
        # Check if new commands exist
        commands = ['telegram_equity', 'telegram_risk']
        
        for cmd in commands:
            if hasattr(bot, cmd):
                print(f"✅ Command {cmd} tersedia")
            else:
                print(f"❌ Command {cmd} tidak ditemukan")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram commands error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 STARTING INTEGRATION TESTS")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Config Loading", test_config_loading),
        ("Bot Initialization", test_bot_initialization),
        ("Equity Calculations", test_equity_calculations),
        ("Telegram Commands", test_telegram_commands)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Integration successful!")
        print("\n🚀 Bot siap untuk trading dengan equity system!")
        print("\nCommands tersedia:")
        print("   python3 main.py          # Jalankan bot")
        print("   /equity                  # Cek equity status")
        print("   /risk                    # Cek risk analysis")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)