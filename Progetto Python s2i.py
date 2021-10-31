import requests
import json
from collections import OrderedDict
from datetime import datetime

class Download:

    def __init__(self):
        self.url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
        self.params = {
            'start': 1,
            'limit': 100,
            'convert': 'USD'
        }
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': 'inserire chiave privata CMC'
        }


    def fetchCurrencies(self):
        r = requests.get(url=self.url, params=self.params, headers=self.headers).json()
        return r['data']


downloadInfo = Download()
currencies = downloadInfo.fetchCurrencies() # salvo i dati del JSON in currencies

maxVol = None  # dizionario dove salvo codice e volume della criptovaluta con il maggior volume nelle 24 ore
costOver76 = 0  # variabile dove salvo il costo per acquistare un'unità di tutte le criptovalute il cui volume delle ultime 24 ore sia superiore a 76.000.000$
lessInfoAboutCurrencies = {}  # in questo dizionario salvo solo le informazioni che mi servono per il 3° task
topTwenty = []  # lista dove salvo le prime 20 criptovalute, la utilizzero per il 3° e 5° task

for currency in currencies:

    # 1) Criptovaluta con il volume maggiore nelle ultime 24 ore
    if not maxVol or currency['quote']['USD']['volume_24h'] > maxVol['volume']:
        maxVol ={'cripto': currency['symbol'], 'volume': currency['quote']['USD']['volume_24h']}

    # 4) Costo per comprare un'unità di tutte le  cripto che superano i 76 milioni di dollari di volume giornaliero
    if currency['quote']['USD']['volume_24h'] > 76000000:
        costOver76 += currency['quote']['USD']['price']

    # creo la lista delle 20 cripto più capitalizzate
    if currency['cmc_rank'] <= 20:
        topTwenty.append(currency)

    # raccolgo in un dizionario solo codice e incremento percentuale giornaliero delle criptovalute
    lessInfoAboutCurrencies[currency['symbol']] = currency['quote']['USD']['percent_change_24h']

# 2) prendo le migliori e peggiori 10 criptovalute

sortedTuples = sorted(lessInfoAboutCurrencies.items(), key=lambda x: x[1])  # ordino le criptovalute per incremento percentuale giornaliero, in una lista di tuple,
                                                                            # il primo elemento della tupla è il codice della cripto,
                                                                            # il secondo l'incremento percentuale giornaliero

worstTenTuples = sortedTuples[:10]
bestTenTuples = sortedTuples[-1:-11:-1]

bestTenDict = OrderedDict()
for k, v in bestTenTuples:
    bestTenDict[k] = v

worstTenDict = OrderedDict()
for k, v in worstTenTuples:
    worstTenDict[k] = v

# Blocco di codice dove vado a svolgere il 3° e 5° task sfruttando la lista delle 20 criptovalute più capitalizzate
costTop20 = 0
costYesterday = 0

for currency in topTwenty:
    # 3) trovo il costo per comprare una singola unità delle top 20 cripto
    costTop20 += float(currency['quote']['USD']['price'])

    # in questo blocco calcolo quanto mi sarebbe costato comprare una singola unità delle top 20 cripto il giorno prima
    var = currency['quote']['USD']['price'] * abs(currency['quote']['USD']['percent_change_24h']) / 100  # variazione di prezzo rispetto al giorno prima
    yesterdayPrice = 0
    if currency['quote']['USD']['percent_change_24h'] > 0:
        yesterdayPrice = currency['quote']['USD']['price'] - var
    elif currency['quote']['USD']['percent_change_24h'] == 0:
        yesterdayPrice = currency['quote']['USD']['price']
    else:
        yesterdayPrice = currency['quote']['USD']['price'] + var

    costYesterday += yesterdayPrice

# calcolo il ritorno in percentuale nel avere acquistato le top 20 il giorno precedente
roi = (costTop20-costYesterday)/costYesterday*100

# creo dizionario dei dati che voglio scrivere nel file JSON
data = {'1) max_daily_volume': maxVol,
        '2) best_&_worst_10_cripto': {'best_cripto': bestTenDict,
               'worst_cripto': worstTenDict},
        '3) cost_top_20': costTop20,
        '4) cost_over_76': costOver76,
        '5) roi': roi
        }

# scrivo nel file JSON
with open(f'{datetime.now()}.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)



