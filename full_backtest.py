import asyncio
import websockets
import json
import pandas as pd
from ict_engine import scan_for_setups

TOKEN = "X2XRGRTknnePYaJ"
SYMBOL = "frxUSOIL"
LOT_SIZE = 0.01
PIP_VALUE = 0.10

async def get_data_chunk(end_epoch):
    uri = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    async with websockets.connect(uri) as ws:
        request = {
            "ticks_history": SYMBOL, 
            "adjust_start_time": 1, 
            "count": 5000, 
            "end": str(end_epoch), 
            "granularity": 900, 
            "style": "candles"
        }
        await ws.send(json.dumps(request))
        response = json.loads(await ws.recv())
        
        actual_sym = "USOIL"
        if 'error' in response:
            actual_sym = "R_10 (Fallback)"
            request['ticks_history'] = "R_10"
            await ws.send(json.dumps(request))
            response = json.loads(await ws.recv())
            
        candles = response.get('candles', [])
        return candles, actual_sym

async def get_6_month_data():
    print("Fetching 6 months of data...")
    chunk1, sym1 = await get_data_chunk("latest")
    if not chunk1: return None, "NONE"
    oldest_epoch = chunk1[0]['epoch']
    chunk2, sym2 = await get_data_chunk(oldest_epoch)
    
    actual_symbol = sym1 # Use symbol from first chunk
    
    all_candles = chunk2 + chunk1
    seen = set()
    unique_candles = [c for c in all_candles if not (c['epoch'] in seen or seen.add(c['epoch']))]
    unique_candles.sort(key=lambda x: x['epoch'])
    
    df = pd.DataFrame(unique_candles)
    df['epoch'] = pd.to_datetime(df['epoch'], unit='s')
    df.rename(columns={'epoch': 'time', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'}, inplace=True)
    df.set_index('time', inplace=True)
    return df[['Open', 'High', 'Low', 'Close']], actual_symbol

def run_backtest(df, symbol):
    # DEBUG INFO
    print(f"\n=== DATA DEBUG ===")
    print(f"Actual Symbol: {symbol}")
    print(f"Price Range: ${df['Low'].min():.2f} to ${df['High'].max():.2f}")
    print(f"================\n")
    
    setups = scan_for_setups(df)
    
    if not setups:
        print("\n[PROTECTED] No setups found. $15 account preserved.")
        return

    results = []
    for setup in setups:
        entry_price = setup['entry']
        sl = setup['sl']
        tp = setup['tp']
        
        future_df = df.loc[setup['time']:]
        outcome, exit_price = "OPEN", entry_price
        
        for i, (time, row) in enumerate(future_df.iterrows()):
            if i == 0: continue 
            if row['Low'] <= sl:
                outcome, exit_price = "LOSS", sl
                break
            elif row['High'] >= tp:
                outcome, exit_price = "WIN", tp
                break
                    
        pips = (exit_price - entry_price) * 10
        dollar_pnl = pips * PIP_VALUE
        results.append({
            'time': setup['time'], 
            'outcome': outcome, 
            'pips': pips, 
            'dollars': dollar_pnl, 
            'target_rr': setup['rr'], 
            'sl': sl, 
            'tp': tp
        })

    wins = [r for r in results if r['outcome'] == "WIN"]
    losses = [r for r in results if r['outcome'] == "LOSS"]
    total = len(wins) + len(losses)
    wr = (len(wins) / total * 100) if total > 0 else 0
    dollars_w = sum(r['dollars'] for r in wins)
    dollars_l = sum(abs(r['dollars']) for r in losses)
    pf = (dollars_w / dollars_l) if dollars_l > 0 else float('inf')

    print("\n" + "="*60)
    print("   USOIL $15 ACCOUNT BACKTEST (0.01 LOTS)        ")
    print("="*60)
    print(f" Data Window:          {df.index[0].date()} to {df.index[-1].date()}")
    print(f" Total Setups:         {len(results)}")
    print(f" Closed Trades:        {total} ({len(wins)}W / {len(losses)}L)")
    print("-" * 60)
    print(f" Win Rate:             {wr:.1f}%")
    print(f" Profit Factor:        {pf:.2f}")
    print(f" Total Dollar P/L:     ${dollars_w - dollars_l:+.2f}")
    print("="*60)
    
    if results:
        print("\n Trade Log (Exact impact on $15 account):")
        for r in results:
            e = "WIN " if r['outcome']=="WIN" else "LOSS" if r['outcome']=="LOSS" else "OPEN"
            print(f" [{e}] {r['time'].date()} | ${r['dollars']:+.2f} | Pips: {r['pips']:+.1f} | RR: {r['target_rr']:.1f}:1 | SL: {r['sl']:.2f} -> TP: {r['tp']:.2f}")

if __name__ == "__main__":
    df, symbol = asyncio.run(get_6_month_data())
    if df is not None:
        run_backtest(df, symbol)
