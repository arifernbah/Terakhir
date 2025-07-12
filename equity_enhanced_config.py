#!/usr/bin/env python3
"""
Enhanced Equity-Based Trading yang terintegrasi dengan config_hybrid_all.json
"""

import json
import os
from typing import Dict, Any, Tuple
from equity_trading_implementation import EquityBasedTrading

class EnhancedEquityTrading(EquityBasedTrading):
    """
    Enhanced equity trading yang menggunakan config_hybrid_all.json
    """
    
    def __init__(self, initial_balance: float):
        # Load config dari file hybrid
        self.hybrid_config = self.load_hybrid_config()
        
        # Tentukan config berdasarkan balance
        self.selected_config = self.select_config_by_balance(initial_balance)
        
        # Convert ke equity config format
        equity_config = self.convert_to_equity_config(self.selected_config)
        
        # Initialize parent class
        super().__init__(initial_balance, equity_config)
        
        # Additional parameters dari hybrid config
        self.leverage = self.selected_config.get('leverage', 10)
        self.risk_level = self.selected_config.get('risk_level', 'balanced')
        self.portfolio_heat_limit = self.selected_config.get('portfolio_heat_limit', 10)
        self.confidence_threshold = self.selected_config.get('confidence_threshold', 70)
        self.high_confidence_threshold = self.selected_config.get('high_confidence_threshold', 80)
        self.max_open_trades = self.selected_config.get('max_open_trades', 3)
        
        print(f"🎯 Config loaded: Balance ${initial_balance}")
        print(f"📊 Risk Level: {self.risk_level}")
        print(f"⚡ Leverage: {self.leverage}x")
        print(f"🎲 Confidence Threshold: {self.confidence_threshold}%")
        print(f"🚀 Max Open Trades: {self.max_open_trades}")
    
    def load_hybrid_config(self) -> Dict[str, Any]:
        """Load config dari file hybrid"""
        try:
            with open('config_hybrid_all.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ config_hybrid_all.json not found!")
            return {}
    
    def select_config_by_balance(self, balance: float) -> Dict[str, Any]:
        """
        Pilih config berdasarkan balance
        """
        # Urutkan config berdasarkan balance
        balance_configs = []
        for key, config in self.hybrid_config.items():
            if key.startswith('$'):
                config_balance = float(key[1:])  # Remove $ sign
                balance_configs.append((config_balance, config))
        
        # Sort by balance
        balance_configs.sort(key=lambda x: x[0])
        
        # Pilih config yang sesuai
        selected_config = None
        for config_balance, config in balance_configs:
            if balance <= config_balance:
                selected_config = config
                break
        
        # Jika balance lebih besar dari config tertinggi, gunakan config tertinggi
        if selected_config is None:
            selected_config = balance_configs[-1][1]
        
        # Ensure multi-pair support: if only single 'symbol' provided, supply
        # default top-cap list so the bot can scan multiple pairs automatically.
        if 'symbols' not in selected_config:
            default_pairs = [
                "DOGEUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT",
                "SOLUSDT", "MATICUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT"
            ]
            # Preserve the original primary symbol at index 0 for backward compatibility.
            primary = selected_config.get('symbol', 'BTCUSDT')
            if primary in default_pairs:
                default_pairs.remove(primary)
            selected_config['symbols'] = [primary] + default_pairs

        return selected_config
    
    def convert_to_equity_config(self, hybrid_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert hybrid config ke format equity config
        """
        risk_level = hybrid_config.get('risk_level', 'balanced')
        
        # Mapping risk level ke equity parameters
        risk_mapping = {
            'ultra_conservative': {
                'base_risk_percent': 0.8,
                'max_risk_percent': 2.0,
                'max_drawdown_percent': 12.0,
                'daily_loss_limit': 2.5,
                'daily_profit_target': 6.0
            },
            'very_conservative': {
                'base_risk_percent': 1.2,
                'max_risk_percent': 2.5,
                'max_drawdown_percent': 15.0,
                'daily_loss_limit': 3.0,
                'daily_profit_target': 8.0
            },
            'moderate': {
                'base_risk_percent': 1.5,
                'max_risk_percent': 3.5,
                'max_drawdown_percent': 18.0,
                'daily_loss_limit': 4.0,
                'daily_profit_target': 10.0
            },
            'balanced': {
                'base_risk_percent': 2.0,
                'max_risk_percent': 4.0,
                'max_drawdown_percent': 20.0,
                'daily_loss_limit': 5.0,
                'daily_profit_target': 12.0
            },
            'balanced_plus': {
                'base_risk_percent': 2.5,
                'max_risk_percent': 5.0,
                'max_drawdown_percent': 22.0,
                'daily_loss_limit': 6.0,
                'daily_profit_target': 15.0
            },
            'professional': {
                'base_risk_percent': 1.8,
                'max_risk_percent': 3.0,
                'max_drawdown_percent': 15.0,
                'daily_loss_limit': 4.0,
                'daily_profit_target': 8.0
            },
            'full_aggressive': {
                'base_risk_percent': 1.8,
                'max_risk_percent': 3.0,
                'max_drawdown_percent': 15.0,
                'daily_loss_limit': 4.0,
                'daily_profit_target': 8.0
            }
        }
        
        return risk_mapping.get(risk_level, risk_mapping['balanced'])
    
    def calculate_position_size_with_leverage(self, entry_price: float, stop_loss_price: float, 
                                           symbol: str = "BTCUSDT", confidence: float = 0.7) -> Tuple[float, float]:
        """
        Hitung position size dengan mempertimbangkan leverage dan confidence
        """
        # Base position size calculation
        base_position_size, risk_percent = self.calculate_position_size(entry_price, stop_loss_price, symbol)
        
        # Adjust berdasarkan confidence level
        if confidence >= self.high_confidence_threshold / 100:
            # High confidence - increase position size
            confidence_multiplier = 1.2
            print(f"🚀 High confidence trade: {confidence:.1%}")
        elif confidence >= self.confidence_threshold / 100:
            # Normal confidence
            confidence_multiplier = 1.0
            print(f"✅ Normal confidence trade: {confidence:.1%}")
        else:
            # Low confidence - decrease position size
            confidence_multiplier = 0.7
            print(f"⚠️ Low confidence trade: {confidence:.1%}")
        
        # Apply confidence multiplier
        adjusted_position_size = base_position_size * confidence_multiplier
        
        # Apply leverage adjustment (dengan leverage, position size bisa lebih besar)
        # Tapi risk tetap sama karena margin requirement lebih kecil
        leveraged_position_size = adjusted_position_size * self.leverage
        
        # Tapi batasi sesuai portfolio heat limit
        max_position_value = self.current_equity * (self.portfolio_heat_limit / 100)
        max_position_size = max_position_value / entry_price
        
        final_position_size = min(leveraged_position_size, max_position_size)
        
        print(f"📊 Position Sizing with Leverage for {symbol}:")
        print(f"   💰 Current Equity: ${self.current_equity:.2f}")
        print(f"   🎯 Base Risk %: {risk_percent:.2f}%")
        print(f"   📈 Entry Price: ${entry_price:.2f}")
        print(f"   🛑 Stop Loss: ${stop_loss_price:.2f}")
        print(f"   🎲 Confidence: {confidence:.1%}")
        print(f"   ⚡ Leverage: {self.leverage}x")
        print(f"   🏦 Portfolio Heat Limit: {self.portfolio_heat_limit}%")
        print(f"   📊 Final Position Size: {final_position_size:.6f} {symbol.replace('USDT', '')}")
        
        return final_position_size, risk_percent
    
    def get_trading_parameters(self) -> Dict[str, Any]:
        """
        Dapatkan parameter trading dari config
        """
        return {
            'symbols': self.selected_config.get('symbols', [self.selected_config.get('symbol', 'BTCUSDT')]),
            'timeframe': self.selected_config.get('timeframe', '5m'),
            'leverage': self.leverage,
            'max_open_trades': self.max_open_trades,
            'confidence_threshold': self.confidence_threshold,
            'high_confidence_threshold': self.high_confidence_threshold,
            'take_profit': self.selected_config.get('take_profit', {}),
            'stop_loss': self.selected_config.get('stop_loss', {}),
            'trailing': self.selected_config.get('trailing', {}),
            'session': self.selected_config.get('session', {}),
            'portfolio_heat_limit': self.portfolio_heat_limit,
            'risk_level': self.risk_level
        }
    
    def should_enter_trade(self, symbol: str, confidence: float) -> Tuple[bool, str]:
        """
        Cek apakah boleh masuk trade berdasarkan config
        """
        # Cek basic equity conditions
        should_stop, reason = self.should_stop_trading()
        if should_stop:
            return False, reason
        
        # Cek confidence threshold
        if confidence < self.confidence_threshold / 100:
            return False, f"Confidence {confidence:.1%} below threshold {self.confidence_threshold}%"
        
        # Cek portfolio heat limit
        # Simulasi: anggap ada posisi terbuka senilai X% dari equity
        current_heat = 0  # Harus dihitung dari posisi aktif
        if current_heat >= self.portfolio_heat_limit:
            return False, f"Portfolio heat limit reached: {current_heat}%"
        
        # Cek session hours
        session_config = self.selected_config.get('session', {})
        if session_config.get('active_hours_only', False):
            # Implementasi cek jam trading
            pass
        
        return True, "OK to enter trade"
    
    def print_enhanced_status(self):
        """
        Print status dengan informasi dari hybrid config
        """
        # Print basic equity status
        super().print_status()
        
        # Print additional hybrid config info
        print("\n" + "="*50)
        print("🎯 HYBRID CONFIG STATUS")
        print("="*50)
        print(f"⚡ Leverage: {self.leverage}x")
        print(f"📊 Risk Level: {self.risk_level}")
        print(f"🎲 Confidence Threshold: {self.confidence_threshold}%")
        print(f"🚀 High Confidence Threshold: {self.high_confidence_threshold}%")
        print(f"🏦 Portfolio Heat Limit: {self.portfolio_heat_limit}%")
        print(f"📈 Max Open Trades: {self.max_open_trades}")
        
        # Trading parameters
        params = self.get_trading_parameters()
        print(f"📊 Symbols: {params['symbols']}")
        print(f"⏰ Timeframe: {params['timeframe']}")
        print(f"🎯 Take Profit: {params['take_profit'].get('tp_percent', 0):.2f}%")
        print(f"🛑 Stop Loss: {params['stop_loss'].get('sl_percent', 0):.2f}%")
        print("="*50)

def example_usage_with_config():
    """
    Contoh penggunaan dengan config hybrid
    """
    # Test dengan berbagai balance
    balances = [5, 20, 50, 100, 150]
    
    for balance in balances:
        print(f"\n{'='*60}")
        print(f"🧪 Testing with Balance: ${balance}")
        print(f"{'='*60}")
        
        # Initialize enhanced equity trader
        trader = EnhancedEquityTrading(balance)
        
        # Simulasi trade dengan confidence berbeda
        confidences = [0.6, 0.7, 0.85]  # Low, normal, high confidence
        
        for confidence in confidences:
            print(f"\n📊 Testing with confidence: {confidence:.1%}")
            
            # Cek apakah boleh trade
            can_trade, reason = trader.should_enter_trade("BTCUSDT", confidence)
            if can_trade:
                # Calculate position size
                entry_price = 50000
                stop_loss_price = 49500
                position_size, risk_percent = trader.calculate_position_size_with_leverage(
                    entry_price, stop_loss_price, "BTCUSDT", confidence
                )
                print(f"✅ Trade approved: {reason}")
            else:
                print(f"❌ Trade rejected: {reason}")
        
        # Print comprehensive status
        trader.print_enhanced_status()

if __name__ == "__main__":
    example_usage_with_config()