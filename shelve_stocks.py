"""the following is how to use shelves. Make {ticker:[prices],"date":[dates]}
http://stackoverflow.com/questions/29657902/appending-a-value-to-a-key-in-python
need to change to absolute value 10% difference...

note, on 2/17/17 get_quote got the 52 week max
"""
import urllib.request
import re
import shelve
import datetime
#view-source:http://slickcharts.com/sp500 - S&P 500 companies

def get_quote(symbol):
    """finds the quote for a stock"""
    base_url = 'http://finance.google.com/finance?q='
    content = urllib.request.urlopen(base_url + symbol).read()
    content=content.decode()
    try:
        sym=r"(\",values:\[\""+symbol+r"\",\")"
        m=re.split(sym,content)
        relevent=m[2].replace(",","")#if you don't remove commas,
        #the thousands comma messes up the decims search
        decims=r"[0-9]+\.+[0-9]+\w"
        k=re.search(decims,relevent)
    except Exception:
        return "NO QUOTE"
    return k.string[k.start():k.end()]
def find_symbols():
    """retrieves all symbols from the S&P 500"""
    web_pg=urllib.request.urlopen("http://slickcharts.com/sp500").read()
    web_pg=web_pg.decode()
    splits=re.split(r"(name=\"symbol\" value=\")",web_pg)#before sym location
    symbols=list()
    for sym in range(2,len(splits),2):
        k=re.search(r"(\"/>)",splits[sym])#after sym location
        symbols.append(k.string[:k.start()])
    return symbols

def sym_price_gen():
    """generates (ticker, price) tuples.
this origionally used yield but I shortened it to map and zip"""
    symbols=find_symbols()
    return zip(symbols,map(get_quote,symbols))

def open_db(db="sNp_shelve"):
    """opens the dbm"""
    return shelve.open(db,"c",writeback=True)

def update_db(db):
    """updates the dbm and checks if any lost > 10%"""
    stocks_prices=sym_price_gen()
    today=datetime.datetime.now()
    db.setdefault("date",[]).append([today,])#[today,] is important
    #if you close before all are done errors are caught next time
    for ticker,price in stocks_prices:
        
        try:#catches no value for db[ticker] and cant convert to float
            price=float(price)
            db.setdefault(ticker,{today:price})
            db[ticker][today]=price#error?
            last_price=db[ticker][db["date"][-2][0]]# list in list in dict
            #print("ok")
            change=price-last_price
            if abs(change)>last_price*.1:#should fix it.
                db["date"][-1].append(ticker)
                print(ticker, " changed 10%. it was at ", last_price," it's now at ", price)
        except ValueError:
            #print("\nNo price for ",ticker," ln 68")
            #cant convert to float
            #print(ticker, price)
            pass
        except KeyError:
            print("\nKey error with ", ticker," maybe new on SnP? ln 73.")
            #no date[-2], or no last_price
            #entire program might not have run last time
    print("update complete")
            

def main():
    """runs the whole thing"""
    try:
        sNp=open_db()
        update_db(sNp)
    except (urllib.error.HTTPError,KeyboardInterrupt) as e:
        print("NO")
    sNp.close()
    

if __name__=="__main__":
    #pass
    main()
    input("input anything to exit")    

#AGN == NO QUOTE
#d, mac and ph are both apple?
#mnst is actually vvm?
#fox is foxa?
#L (lowes) doesnt come up automatically
#prgo == NO QUOTE
#HP is actually HPQ
#many companies have different classes of shares
#ENDP==NO QUOTE

