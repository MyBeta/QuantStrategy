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

def get_time_series(ticker: str=ticker, force_update: bool=force_update, 
                    period: str=period, interval: str=interval) -> pd.DataFrame:
    """Download data, clean it, and save it inside pickle file (pickle_fn) and return it as DataFrame.
    `ticker` from Yahoo Finance, `force_update`, `period`, `interval` are discussed above"""
    
    pickle_fn = "history_" + ticker + ".pkl"
    
    if force_update or not exists(pickle_fn):
        # download data from Yahoo Finance
        tick_yf = yf.Ticker(ticker)
        hist_df = tick_yf.history(period=period, interval=interval)
        
        # check for obivous data issues (>+100% jump and >-50% drop before/after the same one datapoint)
        pct_changes = hist_df["Close"].pct_change()
        possible_data_issue = pct_changes[(pct_changes > 1.0) | (pct_changes < -0.5)]
        location_of_possible_data_issue = possible_data_issue.index.to_series().map(lambda i: hist_df.index.get_loc(i))
        # check if the location of the jump/drop are immediately after each other 
        # -> in that case drop the first datapoint
        drop = location_of_possible_data_issue[(location_of_possible_data_issue.diff() == 1).shift(-1) == True]
        hist_df = hist_df.drop(drop.index)
        hist_df.to_pickle(pickle_fn)
    else:
        hist_df = pd.read_pickle(pickle_fn)
        
    return hist_df["Close"]
    
def get_signals_from_MA1(spot_px: pd.DataFrame, ma_1_window_size: int = 500, 
                         long_only: bool=long_only) -> (pd.DataFrame, pd.DataFrame):
    """Generate Trading Signals: Using a simple trend following strategy with one moving average.
    Save the trading signal inside a pickle file and return it as DataFrame together with the moving average.
    `spot_px` are the prices, on which we like to generate trading signals on,
    `ma_1_window_size` specifies the window size over which the moving average is being calculated."""
    
    # calculate moving averages (MA)
    ma_1 = spot_px.rolling(ma_1_window_size, min_periods=ma_1_window_size).mean()
        
    # signals: buy when spot is higher than MA, sell when spot is lower than MA
    # signal =  0 -> no exposure
    # signal =  1 -> long position
    # signal = -1 -> short position
    zeros = pd.Series(spot_px.size*[0], index=spot_px.index)    # series of zeros
    signal = zeros.mask(spot_px > ma_1, 1)                      # signal =  1 if spot>MA
    if not long_only: 
        signal = signal.mask(spot_px < ma_1, -1)                # signal = -1 if spot<MA
        
    # save signals
    signal.to_pickle("signal_" + ticker + ( "_long_only" if long_only else "") + ".pkl" )

    return (signal, ma_1)


    
    
    
    