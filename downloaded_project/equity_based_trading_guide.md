# 📈 Panduan Trading Berdasarkan Equity

## 🎯 Apa itu Equity dalam Trading?

**Equity** adalah total nilai akun trading Anda saat ini, termasuk:
- Saldo kas (cash balance)
- Profit/Loss posisi yang sedang terbuka (floating P&L)
- Margin yang digunakan

### Formula Dasar Equity:
```
Equity = Balance + Floating P&L
```

## 📊 Jenis-Jenis Equity Trading

### 1. **Fixed Equity Trading**
Trading dengan jumlah tetap berdasarkan persentase equity

**Contoh:**
- Equity: $1,000
- Risk per trade: 2% dari equity = $20
- Jika equity naik menjadi $1,100, risk per trade = $22

### 2. **Dynamic Equity Trading**
Trading dengan penyesuaian otomatis berdasarkan perubahan equity

**Contoh:**
- Equity tinggi → posisi lebih besar
- Equity rendah → posisi lebih kecil

### 3. **Equity Curve Trading**
Trading berdasarkan performa equity curve (grafik pertumbuhan akun)

## 🔢 Cara Menghitung Position Size Berdasarkan Equity

### Formula Position Sizing:
```
Position Size = (Equity × Risk %) / Stop Loss Distance
```

### Contoh Perhitungan:
```
Equity: $1,000
Risk per trade: 2% = $20
Stop Loss Distance: $100 (contoh: dari $50,000 ke $49,900)
Position Size = $20 / $100 = 0.2 BTC

Atau dengan persentase:
Stop Loss: 0.5% dari entry price
Position Size = $20 / (Entry Price × 0.005) = Size dalam koin
```

## 📈 Strategi Trading Berdasarkan Equity

### 1. **Percentage Risk Model**
```python
# Contoh implementasi untuk Binance Futures
def calculate_position_size(equity, risk_percent, entry_price, stop_loss_price):
    risk_amount = equity * (risk_percent / 100)
    price_distance = abs(entry_price - stop_loss_price)
    position_size = risk_amount / price_distance
    return position_size

# Penggunaan untuk BTCUSDT
equity = 1000  # $1,000
risk_percent = 2  # 2%
entry_price = 50000  # $50,000
stop_loss_price = 49500  # $49,500 (1% stop loss)

position_size = calculate_position_size(equity, risk_percent, entry_price, stop_loss_price)
print(f"Position Size: {position_size:.6f} BTC")
```

### 2. **Kelly Criterion**
Formula untuk menentukan ukuran posisi optimal berdasarkan probabilitas menang

```python
def kelly_criterion(win_rate, avg_win, avg_loss):
    """
    Kelly Criterion untuk position sizing
    """
    if avg_loss == 0:
        return 0
    
    win_loss_ratio = avg_win / avg_loss
    kelly_percent = win_rate - ((1 - win_rate) / win_loss_ratio)
    
    # Gunakan fraksi Kelly untuk mengurangi risiko
    conservative_kelly = kelly_percent * 0.25  # 25% dari Kelly penuh
    
    return max(0, min(conservative_kelly, 0.05))  # Maksimal 5%

# Contoh penggunaan
win_rate = 0.60  # 60% win rate
avg_win = 150    # $150 rata-rata profit
avg_loss = 100   # $100 rata-rata loss

kelly_percent = kelly_criterion(win_rate, avg_win, avg_loss)
print(f"Kelly Percentage: {kelly_percent:.2%}")
```

### 3. **Martingale vs Anti-Martingale**

**Martingale (Tidak Disarankan):**
- Gandakan posisi setelah loss
- Sangat berisiko tinggi

**Anti-Martingale (Disarankan):**
- Perbesar posisi setelah win
- Kecilkan posisi setelah loss

```python
def anti_martingale_position_size(base_position, consecutive_wins, consecutive_losses):
    """
    Anti-Martingale position sizing
    """
    if consecutive_wins > 0:
        # Tingkatkan posisi setelah menang berturut-turut
        multiplier = 1 + (consecutive_wins * 0.1)  # 10% per kemenangan
        return base_position * min(multiplier, 2.0)  # Maksimal 2x
    elif consecutive_losses > 0:
        # Kurangi posisi setelah kalah berturut-turut
        multiplier = 1 - (consecutive_losses * 0.1)  # 10% per kekalahan
        return base_position * max(multiplier, 0.5)  # Minimal 0.5x
    else:
        return base_position
```

## 🎯 Equity-Based Risk Management

### 1. **Drawdown Limits**
```python
def check_drawdown_limit(current_equity, peak_equity, max_drawdown_percent):
    """
    Cek apakah drawdown sudah mencapai batas
    """
    drawdown = (peak_equity - current_equity) / peak_equity
    max_drawdown = max_drawdown_percent / 100
    
    if drawdown >= max_drawdown:
        return True, f"Drawdown limit reached: {drawdown:.2%}"
    return False, f"Current drawdown: {drawdown:.2%}"

# Contoh penggunaan
current_equity = 900
peak_equity = 1200
max_drawdown_percent = 20

limit_reached, message = check_drawdown_limit(current_equity, peak_equity, max_drawdown_percent)
print(message)
```

### 2. **Daily/Weekly Equity Limits**
```python
def daily_equity_management(starting_equity, current_equity, daily_loss_limit, daily_profit_target):
    """
    Manajemen equity harian
    """
    daily_pnl = current_equity - starting_equity
    daily_pnl_percent = (daily_pnl / starting_equity) * 100
    
    # Cek batas kerugian harian
    if daily_pnl_percent <= -daily_loss_limit:
        return "STOP_TRADING", f"Daily loss limit reached: {daily_pnl_percent:.2f}%"
    
    # Cek target profit harian
    if daily_pnl_percent >= daily_profit_target:
        return "CONSIDER_STOP", f"Daily profit target reached: {daily_pnl_percent:.2f}%"
    
    return "CONTINUE", f"Daily P&L: {daily_pnl_percent:.2f}%"
```

## 📊 Implementasi Praktis

### 1. **Equity Monitoring System**
```python
class EquityMonitor:
    def __init__(self, initial_equity):
        self.initial_equity = initial_equity
        self.peak_equity = initial_equity
        self.current_equity = initial_equity
        self.equity_history = [initial_equity]
        self.drawdown_history = []
    
    def update_equity(self, new_equity):
        self.current_equity = new_equity
        self.equity_history.append(new_equity)
        
        # Update peak equity
        if new_equity > self.peak_equity:
            self.peak_equity = new_equity
        
        # Calculate drawdown
        drawdown = (self.peak_equity - new_equity) / self.peak_equity
        self.drawdown_history.append(drawdown)
    
    def get_equity_stats(self):
        return {
            'current_equity': self.current_equity,
            'peak_equity': self.peak_equity,
            'total_return': (self.current_equity / self.initial_equity - 1) * 100,
            'max_drawdown': max(self.drawdown_history) * 100 if self.drawdown_history else 0,
            'current_drawdown': self.drawdown_history[-1] * 100 if self.drawdown_history else 0
        }
```

### 2. **Position Sizing Based on Equity**
```python
class EquityBasedPositionSizing:
    def __init__(self, base_risk_percent=2, max_risk_percent=5):
        self.base_risk_percent = base_risk_percent
        self.max_risk_percent = max_risk_percent
    
    def calculate_position_size(self, equity, recent_performance, stop_loss_distance):
        """
        Calculate position size based on equity and recent performance
        """
        # Adjust risk based on recent performance
        if recent_performance > 0.1:  # Recent wins
            risk_percent = min(self.base_risk_percent * 1.2, self.max_risk_percent)
        elif recent_performance < -0.1:  # Recent losses
            risk_percent = self.base_risk_percent * 0.8
        else:
            risk_percent = self.base_risk_percent
        
        # Calculate position size
        risk_amount = equity * (risk_percent / 100)
        position_size = risk_amount / stop_loss_distance
        
        return position_size, risk_percent
```

## 🚨 Aturan Penting Equity Trading

### 1. **Never Risk More Than You Can Afford**
```python
def validate_risk_amount(equity, risk_amount, max_risk_percent=5):
    """
    Validasi jumlah risiko tidak melebihi batas
    """
    max_risk = equity * (max_risk_percent / 100)
    if risk_amount > max_risk:
        return False, f"Risk amount ${risk_amount} exceeds maximum ${max_risk}"
    return True, "Risk amount is acceptable"
```

### 2. **Equity Curve Trading Rules**
```python
def equity_curve_signal(equity_history, lookback_period=20):
    """
    Generate signal berdasarkan equity curve
    """
    if len(equity_history) < lookback_period:
        return "INSUFFICIENT_DATA"
    
    recent_equity = equity_history[-lookback_period:]
    equity_trend = (recent_equity[-1] - recent_equity[0]) / recent_equity[0]
    
    if equity_trend > 0.05:  # Equity naik 5%
        return "AGGRESSIVE"  # Bisa lebih agresif
    elif equity_trend < -0.05:  # Equity turun 5%
        return "CONSERVATIVE"  # Lebih konservatif
    else:
        return "NORMAL"  # Trading normal
```

## 💡 Tips Praktis

### 1. **Compound Growth Strategy**
```python
def compound_growth_target(initial_equity, monthly_target_percent, months):
    """
    Hitung target pertumbuhan compound
    """
    monthly_multiplier = 1 + (monthly_target_percent / 100)
    final_equity = initial_equity * (monthly_multiplier ** months)
    return final_equity

# Contoh: Target 5% per bulan selama 12 bulan
initial = 1000
monthly_target = 5
months = 12

final_equity = compound_growth_target(initial, monthly_target, months)
print(f"Target equity setelah {months} bulan: ${final_equity:.2f}")
```

### 2. **Risk-Adjusted Returns**
```python
def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """
    Hitung Sharpe Ratio untuk mengukur risk-adjusted return
    """
    import numpy as np
    
    excess_returns = np.array(returns) - risk_free_rate
    return np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) != 0 else 0
```

## 🎯 Kesimpulan

### Prinsip Utama Equity-Based Trading:
1. **Selalu hitung risiko berdasarkan equity saat ini**
2. **Gunakan position sizing yang proporsional**
3. **Monitor drawdown secara ketat**
4. **Sesuaikan strategi berdasarkan performa equity**
5. **Tetapkan batas kerugian harian/mingguan**

### Keuntungan:
- ✅ Risiko selalu terkontrol
- ✅ Pertumbuhan compound yang optimal
- ✅ Perlindungan modal yang lebih baik
- ✅ Adaptif terhadap kondisi pasar

### Risiko:
- ❌ Pertumbuhan lebih lambat saat equity kecil
- ❌ Memerlukan disiplin tinggi
- ❌ Kompleks untuk pemula

**Ingat:** Equity-based trading adalah tentang konsistensi dan perlindungan modal jangka panjang, bukan keuntungan cepat dalam waktu singkat.