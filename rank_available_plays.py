#!/usr/bin/python

# this is the play ranking file...

import os,sys,time,cPickle
import pandas as pd
from pandas import DataFrame
from pandas import Series
from pandas import Timestamp
from pandas.io.data import Options


def get_options_dict(ticker_list,warm_dict=None):

    if not warm_dict:
        tdict={}
    else:
        tdict=warm_dict

    for ticker in ticker_list:

        if not tdict.has_key(ticker):

            print '****\n****\n**** getting for %s\n****\n****' % ticker
            op   = Options(ticker, 'yahoo')

            try:

                data = op.get_all_data()
                up   = op.underlying_price
                time.sleep(1200)
                tdict[ticker]={'data':data,'up':up}

            except pd.io.data.RemoteDataError:

                print'Request Refused, Dumping and Exiting...'
                cPickle.dump(tdict,open('warm_dict.pkl','wb'))
                sys.exit(0)


        

    return tdict


def scout_expiry(tdict,expiration=None,gap_down=0.96,gap_up=1.04,credit_min=0.20,margin_max=12,rom_min=0.02):

    adict={}

    for ticker in tdict.keys():
        
        print '****\n****\n**** running for %s\n****\n****' % ticker

        if expiration is None:
            expiration=tdict[ticker]['data'].index.levels[1][0]

            
        #bullish put spread analysis...
        out=tdict[ticker]['data'].xs('put',level='Type').xs(expiration,level='Expiry')
        out.to_csv('out2.txt')
        os.system("cat out2.txt |sed 's/\%//g'|sed 's/\+//g'|cut -d',' -f1-10 |awk 'NR>1'> t; mv t out.txt")
        df=pd.read_csv('out.txt',names=["strike","sym","last","bid","ask","chg","pct","vol","oi","iv"])
        strikes = out.index.levels[0]

        bulls={}
        strikes = strikes[strikes<gap_down*tdict[ticker]['up']]

        for s in strikes:

            if (s*2 - (int(s*2)))==0.0:

                dfs=df[df.strike<=s].copy()

                if len(dfs)>0:

                    lastbid    = dfs.tail(n=1).bid.values[0]
                    laststrike = dfs.tail(n=1).strike.values[0]

                    dfs['credit'] = lastbid - dfs.ask
                    dfs['margin'] = laststrike - dfs.strike
                    dfs['rom'] = dfs.credit/dfs.margin
                    dfs['top_strike']=laststrike
                    dfs['safe_zone'] = (tdict[ticker]['up'] - laststrike)/tdict[ticker]['up']

                    dfsf = dfs[dfs.credit>credit_min][dfs.margin<margin_max][dfs.rom>rom_min].copy()
                    dfsf=dfsf[['sym','top_strike','strike','safe_zone','margin','credit','rom','vol','oi','iv']]

                    if len(dfsf)>0:
                        
                        if not bulls.has_key(laststrike):

                            bulls[laststrike]=dfsf


        #bearish call spread analysis...                                     

        out=tdict[ticker]['data'].xs('call',level='Type').xs(expiration,level='Expiry')
        out.to_csv('out2.txt')
        os.system("cat out2.txt |sed 's/\%//g'|sed 's/\+//g'|cut -d',' -f1-10 |awk 'NR>1'> t; mv t out.txt")
        df=pd.read_csv('out.txt',names=["strike","sym","last","bid","ask","chg","pct","vol","oi","iv"])
        strikes = out.index.levels[0]

        bears={}
        strikes = strikes[strikes>gap_up*tdict[ticker]['up']]

        for s in strikes:

            if (s*2 - (int(s*2)))==0.0:

                dfs=df[df.strike>=s].copy()

                if len(dfs)>0:

                    lastbid    = dfs.head(n=1).bid.values[0]
                    laststrike = dfs.head(n=1).strike.values[0]

                    dfs['credit'] = lastbid - dfs.ask
                    dfs['margin'] = dfs.strike - laststrike
                    dfs['rom'] = dfs.credit/dfs.margin
                    dfs['top_strike']=laststrike
                    dfs['safe_zone'] = (laststrike - tdict[ticker]['up'])/tdict[ticker]['up']

                    dfsf = dfs[dfs.credit>credit_min][dfs.margin<margin_max][dfs.rom>rom_min].copy()
                    dfsf=dfsf[['sym','top_strike','strike','safe_zone','margin','credit','rom','vol','oi','iv']]

                    if len(dfsf)>0:

                        if not bears.has_key(laststrike):

                            bears[laststrike]=dfsf


        v={'bulls':bulls,'bears':bears}

        adict[ticker]=v

    return adict



def run(ticker_list):

    tdict = get_options_dict(ticker_list)
    adict = scout_expiry(tdict,expiration=None)

    cPickle.dump(adict,open('./dump_result.pkl','wb'))
    
    return adict

if __name__ == "__main__":

    f=open('wkly_equity_symbols.txt')
    d=f.readlines()
    f.close()

    d=[dd.rstrip('\n').lower() for dd in d]
    run(d)




