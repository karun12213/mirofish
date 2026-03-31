import pandas as pd
import numpy as np

def scan_for_setups(df):
    print("Scanning for USOIL Setups (Small Account Optimized)...")
    
    df['EMA_100'] = df['Close'].ewm(span=100, adjust=False).mean()
    
    # Oil parameters: Sweeps ~15 cents, Displacement ~25 cents
    obs = []
    for i in range(2, len(df)):
        o = df['Open'].iloc[i-1]
        c = df['Close'].iloc[i-1]
        n = df['Open'].iloc[i]
        if c - o > 0.25 and n > c:
            obs.append({'index': i, 'high': c, 'low': o})
            
    valid_setups = []
    
    for i in range(100, len(df)):
        entry = df['Close'].iloc[i]
        ema = df['EMA_100'].iloc[i]
        
        # 1. Must be above 100 EMA
        if entry < ema:
            continue
        
        # 2. Swing Low (Last 12 candles)
        lookback = df.iloc[i-12:i]
        swing_low = lookback['Low'].min()
        
        # 3. Sweep: Wick goes 15 cents below swing low, closes above it
        curr_low = df['Low'].iloc[i]
        curr_close = df['Close'].iloc[i]
        curr_open = df['Open'].iloc[i]
        
        if not (curr_low < swing_low - 0.15 and curr_close > swing_low and curr_close > curr_open):
            continue
            
        # 4. Fib OTE
        recent_high = df['High'].iloc[:i].tail(60).max()
        diff = recent_high - swing_low
        fib_top = recent_high - (diff * 0.705)
        fib_bot = recent_high - (diff * 0.790)
        
        if not (fib_bot <= curr_close <= fib_top):
            continue
            
        # 5. Order Block within 10 cents
        has_ob = False
        for ob in obs:
            if ob['index'] < i and ob['low'] <= (swing_low + 0.10) and ob['high'] >= (swing_low - 0.10):
                has_ob = True
                break
        if not has_ob:
            continue
            
        # 6. SL under Swing Low (Tight for small account)
        sl = swing_low - 0.05
        risk = entry - sl
        
        # Block massive stops to protect $15 account
        if risk > 0.40: 
            continue
            
        # 7. TP at previous liquidity
        past_high = df['High'].iloc[:i].tail(200).max()
        tp = past_high
        
        # 8. 3:1 RR minimum
        rr = (tp - entry) / risk if risk > 0 else 0
        if rr < 3.0:
            continue
            
        valid_setups.append({
            'time': df.index[i],
            'type': 'LONG',
            'entry': entry,
            'sl': sl,
            'tp': tp,
            'rr': rr,
            'pips_risked': risk * 10 # Convert to pips for dollar calc
        })
        
    return valid_setups
