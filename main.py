import pytz
import json
import argparse
import dateparser
from time import sleep
from datetime import datetime


parser = argparse.ArgumentParser(description='Get full historical candlestick data of a symbol from the Kocoin exchange')

parser.add_argument('-m', '--mode', type=str, required=False, default="Spot",
                    help="Mode selection(Optional): Spot or Futures (just Spot mode is available now.)")
parser.add_argument('-k', '--klimit', type=int, required=False, default=1500,
                    help="Kline Limit of Exchange(Optional): In Kocoin exchange, this number is 1500.")
parser.add_argument('-s', '--symbol', type=str, required=True,
                    help="Symbol name(Required), for example: BTC-USDT")
parser.add_argument('-i', '--interval', type=str, required=True,
                    help="TimeFrame(Required), In Kocoin exchange, choose between: [1min, 3min,5min,15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week]")
parser.add_argument('-start', '--start', type=str, required=False, default='1 Dec, 2010',
                    help="Start time(Optional)")
parser.add_argument('-end', '--end', type=str, required=False, default='now UTC',
                    help="End time(Optional)")
parser.add_argument('-key', '--api_key', type=str, required=True,
                    help="API Key(Required)")
parser.add_argument('-secret', '--api_secret', type=str, required=True,
                    help="API Secret(Required)")
parser.add_argument('-passphrase', '--api_passphrase', type=str, required=True,
                    help="API Passphrase(Required)")


def date_to_seconds(date_str):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    d = dateparser.parse(date_str)
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    return int((d-epoch).total_seconds())


def get_historical_klines_tv(symbol, interval, start, end):
    
    global kline_limit, client, i_to_s
    
    has_next = False
    new_start = []
    new_end = []
    klines = {}

    kline_res = client.get_kline_data(symbol, interval, start, end)
    # 0 time	  Start time of the candle cycle
    # 1 open	  Opening price
    # 2 close	  Closing price
    # 3 high	  Highest price
    # 4 low	      Lowest price
    # 5 volume	  Transaction volume
    # 6 turnover  Transaction amount
    if len(kline_res):
        for k in range(0, len(kline_res)):
            klines[kline_res[k][0]] = {
                "open":       kline_res[k][1],
                "close":      kline_res[k][2],
                "high":       kline_res[k][3],
                "low":        kline_res[k][4]
                }

    if len(kline_res)==kline_limit: 
        has_next = True
        new_end = end - kline_limit*i_to_s[interval]
        new_start = new_end - kline_limit*i_to_s[interval]
    
    return klines, has_next, new_start, new_end


def GetAllTimeData(start, end, symbol, interval):
    Data = {}
    has_next = True
    while has_next:
        try:
            print("start:", datetime.fromtimestamp(start).strftime('%Y-%m-%d %H:%M:%S'),
                  "end:", datetime.fromtimestamp(end).strftime('%Y-%m-%d %H:%M:%S'))
            klines, has_next, start, end = get_historical_klines_tv(symbol, interval, start, end)
            print("done")
            Data.update(klines)
            sleep(5)
        except:
            print("failed")
            sleep(5)
            print("retry...")
            sleep(5)
            continue
        
    return Data


            
if __name__ == "__main__":
    
    args = parser.parse_args()
    if args.mode=="Spot":
        from kucoin.client import Client
        client = Client(args.api_key,
                        args.api_secret,
                        args.api_passphrase)
        
        i_to_s = {"1min":   int(1*60),
                  "3min":   int(3*60),
                  "5min":   int(5*60),
                  "15min":  int(15*60),
                  "30min":  int(30*60),
                  "1hour":  int(1*3600),
                  "2hour":  int(2*3600),
                  "4hour":  int(4*3600),
                  "6hour":  int(6*3600),
                  "8hour":  int(8*3600),
                  "12hour": int(12*3600),
                  "1day":   int(24*3600),
                  "1week":  int(24*3600*7)}
      
        kline_limit = args.klimit

        print("start downloading...")
        s = datetime.now()
        Data = GetAllTimeData(date_to_seconds(args.start),
                              date_to_seconds(args.end),
                              args.symbol,
                              args.interval)
        e = datetime.now()
        print("download is finished.")
        print("Elapsed Time: ", e-s)
        with open("Kucoin_{}_{}_allTime.json".format(args.symbol, args.interval), 'w') as f:
            f.write(json.dumps(Data))

