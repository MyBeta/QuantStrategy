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
period = "1y"           # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
interval = "1h"         # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
force_update = False    # False = search for existing data inside pickle file
                        #   True = load new data from Yahoo in any case
                        
# Download data and save in pickle
pickle_fn = "history_" + ticker + ".pkl"
if force_update or not exists(pickle_fn):
    tick_yf = yf.Ticker(ticker)
    hist_df = tick_yf.history(period=period, interval=interval)
    hist_df.to_pickle(pickle_fn)
else:
    hists_df = pd.read_pickle(pickle_fn)
    
    

