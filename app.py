import requests

class SecEdgar:
    def __init__(self, fileurl):
        self.fileurl = fileurl
        self.namedict = {}
        self.tickerdict = {}
        self.headers = {'User-Agent': 'MLT CP abdul586@umn.edu'}

        r = requests.get(self.fileurl, headers=self.headers)
        self.filejson = r.json()

        self.cik_json_to_dict()

    def cik_json_to_dict(self):
        for item in self.filejson.values():
            if 'title' in item and 'cik_str' in item and 'ticker' in item:
                name = item['title']
                cik = str(item['cik_str'])
                ticker = item['ticker']
                self.namedict[name] = (cik, name, ticker)
                self.tickerdict[ticker] = (cik, name, ticker)

    def name_to_cik(self, company_name):
        return self.namedict.get(company_name)

    def ticker_to_cik(self, ticker):
        return self.tickerdict.get(ticker)

# Example usage
if __name__ == "__main__":
    sec_edgar = SecEdgar('https://www.sec.gov/files/company_tickers.json')
    print(sec_edgar.name_to_cik("iCoreConnect Inc."))
    print(sec_edgar.ticker_to_cik("ICCRW"))
