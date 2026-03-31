import asyncio
import websockets
import json
import pandas as pd
from ict_engine import scan_for_setups

TOKEN = "X2XRGRTknnePYaJ"
SYMBOL = "frxUSOIL" # Will trade real USOIL once funded
LOT_SIZE = 0.01

async def live_trade():
    uri = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    print("Connecting to Deriv Live Server...")
    async with websockets.connect(uri) as ws:
        # 1. Authorize Account
        await ws.send(json.dumps({"authorize": TOKEN}))
        auth_resp = json.loads(await ws.recv())
        
        if 'error' in auth_resp:
            print(f"❌ Auth Failed: {auth_resp['error']['message']}")
            return
            
        print(f"✅ Logged in as: {auth_resp['authorize']['fullname']}")
        
        # 2. Check Balance
        await ws.send(json.dumps({"balance": 1, "currency": "USD"}))
        bal_resp = json.loads(await ws.recv())
        balance = bal_resp['balance']['balance']
        print(f"💰 Account Balance: ${balance:.2f}")
        
        # 3. Get Live Data & Scan
        print("⏳ Scanning for live setups...")
        await ws.send(json.dumps({"ticks_history": SYMBOL, "adjust_start_time": 1, "count": 5000, "end": "latest", "granularity": 900, "style": "candles"}))
        data_resp = json.loads(await ws.recv())
        
        if 'error' in data_resp:
            print(f"❌ Cannot fetch {SYMBOL}: {data_resp['error']['message']}")
            print("Note: Deriv Demo accounts sometimes restrict USOIL historical data.")
            return
            
        df = pd.DataFrame(data_resp['candles'])
        df['epoch'] = pd.to_datetime(df['epoch'], unit='s')
        df.rename(columns={'epoch': 'time', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'}, inplace=True)
        df.set_index('time', inplace=True)
        df = df[['Open', 'High', 'Low', 'Close']]
        
        setups = scan_for_setups(df)
        
        if not setups:
            print("\n🛡️ No setups right now. The bot would currently be waiting.")
            return
            
        # 4. Execute Trade (Take the most recent setup)
        trade = setups[-1]
        entry = trade['entry']
        sl = trade['sl']
        tp = trade['tp']
        
        print("\n" + "="*40)
        print(" 🚀 EXECUTING TRADE 🚀 ")
        print("="*40)
        print(f"Symbol: {SYMBOL}")
        print(f"Lot Size: {LOT_SIZE}")
        print(f"Direction: BUY")
        print(f"SL: {sl:.2f} | TP: {tp:.2f}")
        
        # Deriv CFD Trade Execution
        buy_request = {
            "cfd_order": {
                "action": "buy",
                "symbol": SYMBOL,
                "quantity": LOT_SIZE,
                "stop_order": sl,
                "limit_order": tp
            }
        }
        
        await ws.send(json.dumps(buy_request))
        trade_resp = json.loads(await ws.recv())
        
        if 'error' in trade_resp:
            print(f"\n❌ Trade Execution Blocked: {trade_resp['error']['message']}")
            if "Restricted" in trade_resp['error']['message']:
                print("💡 Reason: Deriv requires a funded account to place CFD trades on USOIL.")
        else:
            print(f"\n✅ TRADE PLACED SUCCESSFULLY!")
            print(f"Contract ID: {trade_resp.get('cfd_order', {}).get('id', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(live_trade())
