#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 12:43:15 2023

@author: Michael Bögli

Script to Scrape Crypto Data and Generate Trading Signals
"""

## Imports
import yfinance as yf
import pandas as pd
from os.path import exists

## Settings
ticker = "ADA-USD"
period = "2y"           # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
interval = "1h"         # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
force_update = False    # False = search for existing data in pickle file
                        #   True = load new data from Yahoo in any case
long_only = True        # want allow short positions too? -> then set this to False
    
## Main App

# Download data and save in pickle file (pickle_fn)
pickle_fn = "history_" + ticker + ".pkl"
if force_update or not exists(pickle_fn):
    tick_yf = yf.Ticker(ticker)
    hist_df = tick_yf.history(period=period, interval=interval)
    hist_df.to_pickle(pickle_fn)
else:
    hist_df = pd.read_pickle(pickle_fn)
spot_px = hist_df["Close"]
    
# Generate Trading Signals: Using simple trend following strategy with moving averages
# calculate moving averages (MA)
ma_1_window_size = 500
ma_1 = spot_px.rolling(ma_1_window_size, min_periods=ma_1_window_size).mean()
    
# signals: buy when spot is higher than MA, sell when spot is lower than MA
# signal =  0 -> no exposure
# signal =  1 -> long position
# signal = -1 -> short position
zeros = pd.Series(spot_px.size*[0], index=hist_df.index)    # series of zeros
signal = zeros.mask(spot_px > ma_1, 1)                      # signal =  1 if spot>MA
if not long_only: 
    signal = signal.mask(spot_px < ma_1, -1)                # signal = -1 if spot<MA
    
# save signals
signal.to_pickle("signal_" + ticker + ( "_long_only" if long_only else "") + ".pkl" )
