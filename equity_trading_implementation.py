#!/usr/bin/env python3
"""
Implementasi Praktis Equity-Based Trading
Contoh kode yang bisa diintegrasikan ke dalam bot trading
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class EquityBasedTrading:
    """
    Kelas untuk mengelola trading berdasarkan equity
    """
    
    def __init__(self, initial_equity: float, config: Dict):
        self.initial_equity = initial_equity
        self.current_equity = initial_equity
        self.peak_equity = initial_equity
        self.config = config
        
        # Trading parameters
        self.base_risk_percent = config.get('base_risk_percent', 2.0)
        self.max_risk_percent = config.get('max_risk_percent', 5.0)
        self.max_drawdown_percent = config.get('max_drawdown_percent', 20.0)
        self.daily_loss_limit = config.get('daily_loss_limit', 5.0)
        self.daily_profit_target = config.get('daily_profit_target', 10.0)
        
        # History tracking
        self.equity_history = [initial_equity]
        self.trade_history = []
        self.daily_starting_equity = initial_equity
        
        # Performance metrics
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.total_trades = 0
        self.winning_trades = 0
        
        print(f"🚀 Equity-Based Trading System initialized")
        print(f"💰 Initial Equity: ${initial_equity:.2f}")
        print(f"🎯 Base Risk: {self.base_risk_percent}%")
        print(f"⚠️  Max Drawdown: {self.max_drawdown_percent}%")
    
    def update_equity(self, new_equity: float) -> None:
        """
        Update equity dan hitung statistik
        """
        self.current_equity = new_equity
        self.equity_history.append(new_equity)
        
        # Update peak equity
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity
            print(f"🎉 New Peak Equity: ${self.peak_equity:.2f}")
    
    def get_current_drawdown(self) -> float:
        """
        Hitung drawdown saat ini
        """
        return (self.peak_equity - self.current_equity) / self.peak_equity * 100
    
    def calculate_position_size(self, stop_loss_distance: float, symbol: str = "BTCUSDT") -> Tuple[float, float]:
        """
        Hitung ukuran posisi berdasarkan equity dan kondisi terkini
        
        Returns:
            Tuple[position_size, risk_percent]
        """
        # 1. Cek batas drawdown
        current_drawdown = self.get_current_drawdown()
        if current_drawdown >= self.max_drawdown_percent:
            print(f"🚨 Drawdown limit reached: {current_drawdown:.2f}%")
            return 0, 0
        
        # 2. Cek batas kerugian harian
        daily_pnl = self.get_daily_pnl()
        if daily_pnl <= -self.daily_loss_limit:
            print(f"🚨 Daily loss limit reached: {daily_pnl:.2f}%")
            return 0, 0
        
        # 3. Adjust risk berdasarkan performa recent
        risk_percent = self.calculate_adaptive_risk()
        
        # 4. Hitung position size
        risk_amount = self.current_equity * (risk_percent / 100)
        position_size = risk_amount / stop_loss_distance
        
        print(f"📊 Position Sizing:")
        print(f"   💰 Current Equity: ${self.current_equity:.2f}")
        print(f"   🎯 Risk %: {risk_percent:.2f}%")
        print(f"   💵 Risk Amount: ${risk_amount:.2f}")
        print(f"   📈 Position Size: {position_size:.6f}")
        
        return position_size, risk_percent
    
    def calculate_adaptive_risk(self) -> float:
        """
        Hitung risk percentage yang adaptif berdasarkan performa
        """
        base_risk = self.base_risk_percent
        
        # Adjust berdasarkan consecutive wins/losses
        if self.consecutive_wins >= 3:
            # Setelah 3 kemenangan berturut-turut, tingkatkan risk sedikit
            multiplier = 1 + (self.consecutive_wins * 0.1)
            adjusted_risk = base_risk * min(multiplier, 1.5)  # Maksimal 1.5x
        elif self.consecutive_losses >= 2:
            # Setelah 2 kekalahan berturut-turut, kurangi risk
            multiplier = 1 - (self.consecutive_losses * 0.15)
            adjusted_risk = base_risk * max(multiplier, 0.5)  # Minimal 0.5x
        else:
            adjusted_risk = base_risk
        
        # Adjust berdasarkan drawdown
        current_drawdown = self.get_current_drawdown()
        if current_drawdown > 10:
            # Jika drawdown > 10%, kurangi risk
            drawdown_multiplier = 1 - (current_drawdown / 100)
            adjusted_risk *= drawdown_multiplier
        
        # Pastikan tidak melebihi batas maksimal
        final_risk = min(adjusted_risk, self.max_risk_percent)
        
        return final_risk
    
    def get_daily_pnl(self) -> float:
        """
        Hitung P&L harian dalam persentase
        """
        return (self.current_equity - self.daily_starting_equity) / self.daily_starting_equity * 100
    
    def kelly_criterion_position_size(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Hitung position size menggunakan Kelly Criterion
        """
        if avg_loss == 0 or win_rate <= 0:
            return 0
        
        win_loss_ratio = avg_win / avg_loss
        kelly_fraction = win_rate - ((1 - win_rate) / win_loss_ratio)
        
        # Gunakan fraksi Kelly yang konservatif (25%)
        conservative_kelly = kelly_fraction * 0.25
        
        # Batasi maksimal 5% dari equity
        return max(0, min(conservative_kelly, 0.05)) * 100
    
    def record_trade(self, trade_type: str, entry_price: float, exit_price: float, 
                    position_size: float, pnl: float) -> None:
        """
        Catat hasil trade dan update statistik
        """
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'type': trade_type,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'position_size': position_size,
            'pnl': pnl,
            'equity_before': self.current_equity - pnl,
            'equity_after': self.current_equity
        }
        
        self.trade_history.append(trade_record)
        self.total_trades += 1
        
        # Update consecutive wins/losses
        if pnl > 0:
            self.winning_trades += 1
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            print(f"✅ Winning Trade #{self.consecutive_wins}")
        else:
            self.consecutive_wins = 0
            self.consecutive_losses += 1
            print(f"❌ Losing Trade #{self.consecutive_losses}")
        
        # Update equity
        new_equity = self.current_equity + pnl
        self.update_equity(new_equity)
        
        # Print trade summary
        print(f"📝 Trade Summary:")
        print(f"   📊 {trade_type} | Size: {position_size:.6f}")
        print(f"   💰 P&L: ${pnl:.2f}")
        print(f"   💵 New Equity: ${self.current_equity:.2f}")
    
    def get_performance_stats(self) -> Dict:
        """
        Dapatkan statistik performa trading
        """
        if self.total_trades == 0:
            return {}
        
        win_rate = self.winning_trades / self.total_trades
        total_return = (self.current_equity / self.initial_equity - 1) * 100
        max_drawdown = self.get_max_drawdown()
        
        # Hitung average win/loss
        winning_trades = [t for t in self.trade_history if t['pnl'] > 0]
        losing_trades = [t for t in self.trade_history if t['pnl'] < 0]
        
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = abs(sum(t['pnl'] for t in losing_trades) / len(losing_trades)) if losing_trades else 0
        
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'win_rate': win_rate,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'current_drawdown': self.get_current_drawdown(),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': avg_win / avg_loss if avg_loss > 0 else 0,
            'kelly_suggested_risk': self.kelly_criterion_position_size(win_rate, avg_win, avg_loss)
        }
    
    def get_max_drawdown(self) -> float:
        """
        Hitung maximum drawdown sepanjang waktu
        """
        if len(self.equity_history) < 2:
            return 0
        
        peak = self.equity_history[0]
        max_dd = 0
        
        for equity in self.equity_history[1:]:
            if equity > peak:
                peak = equity
            else:
                drawdown = (peak - equity) / peak * 100
                max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def should_stop_trading(self) -> Tuple[bool, str]:
        """
        Cek apakah trading harus dihentikan
        """
        # Cek drawdown limit
        current_drawdown = self.get_current_drawdown()
        if current_drawdown >= self.max_drawdown_percent:
            return True, f"Maximum drawdown reached: {current_drawdown:.2f}%"
        
        # Cek daily loss limit
        daily_pnl = self.get_daily_pnl()
        if daily_pnl <= -self.daily_loss_limit:
            return True, f"Daily loss limit reached: {daily_pnl:.2f}%"
        
        # Cek consecutive losses
        if self.consecutive_losses >= 5:
            return True, f"Too many consecutive losses: {self.consecutive_losses}"
        
        return False, "Trading can continue"
    
    def reset_daily_stats(self) -> None:
        """
        Reset statistik harian (panggil setiap hari)
        """
        self.daily_starting_equity = self.current_equity
        print(f"🌅 Daily stats reset. Starting equity: ${self.current_equity:.2f}")
    
    def print_status(self) -> None:
        """
        Print status equity dan performa
        """
        stats = self.get_performance_stats()
        
        print("\n" + "="*50)
        print("📊 EQUITY TRADING STATUS")
        print("="*50)
        print(f"💰 Current Equity: ${self.current_equity:.2f}")
        print(f"🎯 Peak Equity: ${self.peak_equity:.2f}")
        print(f"📈 Total Return: {stats.get('total_return', 0):.2f}%")
        print(f"📉 Current Drawdown: {self.get_current_drawdown():.2f}%")
        print(f"📊 Daily P&L: {self.get_daily_pnl():.2f}%")
        print(f"🎲 Win Rate: {stats.get('win_rate', 0):.1%}")
        print(f"🔥 Consecutive Wins: {self.consecutive_wins}")
        print(f"❄️  Consecutive Losses: {self.consecutive_losses}")
        print(f"💡 Kelly Suggested Risk: {stats.get('kelly_suggested_risk', 0):.2f}%")
        print("="*50)

def example_usage():
    """
    Contoh penggunaan Equity-Based Trading
    """
    # Konfigurasi
    config = {
        'base_risk_percent': 2.0,
        'max_risk_percent': 5.0,
        'max_drawdown_percent': 20.0,
        'daily_loss_limit': 5.0,
        'daily_profit_target': 10.0
    }
    
    # Initialize equity trading system
    equity_trader = EquityBasedTrading(initial_equity=1000.0, config=config)
    
    # Simulasi beberapa trades
    print("\n🎮 Simulasi Trading:")
    
    # Trade 1: Winning trade
    position_size, risk_percent = equity_trader.calculate_position_size(stop_loss_distance=50)
    if position_size > 0:
        equity_trader.record_trade("LONG", 50000, 50100, position_size, 20)
    
    # Trade 2: Losing trade
    position_size, risk_percent = equity_trader.calculate_position_size(stop_loss_distance=60)
    if position_size > 0:
        equity_trader.record_trade("SHORT", 50100, 50150, position_size, -15)
    
    # Trade 3: Winning trade
    position_size, risk_percent = equity_trader.calculate_position_size(stop_loss_distance=45)
    if position_size > 0:
        equity_trader.record_trade("LONG", 50150, 50200, position_size, 25)
    
    # Print final status
    equity_trader.print_status()
    
    # Cek apakah trading harus dihentikan
    should_stop, reason = equity_trader.should_stop_trading()
    if should_stop:
        print(f"🚨 Trading stopped: {reason}")
    else:
        print("✅ Trading can continue")

if __name__ == "__main__":
    example_usage()