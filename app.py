import requests

class SecEdgar:
    """
    The SecEdgar class is designed to interact with the U.S. Securities and Exchange Commission (SEC) EDGAR system. 
    Its primary purpose is to allow users to retrieve company-specific filings, such as 10-K (annual) and 10-Q (quarterly) reports, based on the company's CIK (Central Index Key) number, name, or ticker symbol. 

    This class:
    - fetches and processes the JSON data that contains mappings between company names, tickers, and their corresponding CIKs.
    - retrieves filing data for a specific company using the CIK, including document URLs for the filings.
    - allows users to search for a company by its name or ticker and then retrieve the desired filings.
    """
    def __init__(self, fileurl, headers):
        """
        Initializes the SecEdgar object with the URL to fetch CIK data and HTTP headers for the request.
        
        Parameters:
        - fileurl: The URL to the JSON file containing the company names, tickers, and CIK mappings.
        - headers: HTTP headers to be used in the requests, including the User-Agent for proper identification when making requests to the SEC's servers.
        
        The CIK data is fetched and stored in dictionaries for fast lookup.
        """
        self.fileurl = fileurl  # url to fetch cik data
        self.headers = headers  # headers for request
        self.namedict = {}  # stores company names to cik mappings
        self.tickerdict = {}  # stores tickers to cik mappings
        self.filejson = self.fetch_json_data(self.fileurl)  # fetch the json data
        if self.filejson:
            self.cik_json_to_dict()  # populate dictionaries if data is available

    def list_all_companies(self):
        print("List of Companies Available:")  # header for output
        for name, details in self.namedict.items():
            print(f"Company Name: {name}, Ticker: {details[2]}, CIK: {details[0]}")  # print company details

    def fetch_json_data(self, url):
        try:
            response = requests.get(url, headers=self.headers)  # send request to fetch data, HTTP status code 200 indicates a successful request
            response.raise_for_status()  # raises exception for request errors (such as 404 if the URL is incorrect, or 500 if the server has an issue)
            return response.json()  # return json response
        except requests.RequestException as e:
            print(f"Error fetching data from {url}: {e}")  # print error if request fails
            return None

    def cik_json_to_dict(self):
        for item in self.filejson.values():
            if 'title' in item and 'cik_str' in item and 'ticker' in item:  # check necessary fields
                name = item['title']  # company name
                cik = str(item['cik_str']).zfill(10)  # pad cik with zeros since the EDGAR system standardizes CIKs to be 10 digits
                ticker = item['ticker']  # company ticker (ex A)
                self.namedict[name] = (cik, name, ticker)  # store name to cik mapping
                self.tickerdict[ticker] = (cik, name, ticker)  # store ticker to cik mapping

    def name_to_cik(self, company_name):
        return self.namedict.get(company_name)  # lookup cik by company name

    def ticker_to_cik(self, ticker):
        return self.tickerdict.get(ticker)  # lookup cik by ticker

    def get_filings(self, cik, form_types):
        submissions_url = f'https://data.sec.gov/submissions/CIK{cik}.json'  # url for filings
        submissions = self.fetch_json_data(submissions_url)  # fetch filings data
        if not submissions:
            return []

        filings = submissions.get('filings', {}).get('recent', {})  # get recent filings
        form_list = filings.get('form', [])  # list of forms
        accession_list = filings.get('accessionNumber', [])  # list of accession numbers
        primary_doc_list = filings.get('primaryDocument', [])  # list of primary documents
        doc_desc_list = filings.get('primaryDocDescription', [])  # list of descriptions
        filing_dates = filings.get('filingDate', [])  # list of filing dates

        results = []
        for form_type, accession_number, primary_doc, doc_desc, filing_date in zip(form_list, accession_list, primary_doc_list, doc_desc_list, filing_dates):
            if form_type in form_types:  # check if form type matches
                document_url = f'https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number.replace("-", "")}/{primary_doc}'
                results.append({
                    'form_type': form_type,
                    'accession_number': accession_number,
                    'filing_date': filing_date,
                    'document_url': document_url,
                    'description': doc_desc if doc_desc else "No description available"  # add description or default
                })
        return results

    def annual_filing(self, cik, year):
        filings = self.get_filings(cik, ['10-K'])  # fetch 10-K filings
        for filing in filings:
            if filing['filing_date'].startswith(str(year)):  # check if filing matches the year
                return filing
        print(f"No 10-K found for {year}.")
        return None

    def quarterly_filing(self, cik, year, quarter):
        filings = self.get_filings(cik, ['10-Q'])  # fetch 10-Q filings
        for filing in filings:
            filing_year, filing_month = filing['filing_date'][:4], int(filing['filing_date'][5:7])
            if str(year) == filing_year and (filing_month - 1) // 3 + 1 == int(quarter):  # check if filing matches the year and quarter
                return filing
        print(f"No 10-Q found for Q{quarter} {year}.")
        return None

if __name__ == "__main__":
    sec_edgar = SecEdgar(
        fileurl='https://www.sec.gov/files/company_tickers.json',  # url for company tickers
        headers={'User-Agent': 'MLT CP abdul586@umn.edu'}  # header for requests
    )

    query = input("Enter the company name or ticker: ")  # get user input
    
    # try to find the cik by company name
    company_info = sec_edgar.name_to_cik(query)
    
    if not company_info:
        # if not found by name, try to find the cik by ticker
        company_info = sec_edgar.ticker_to_cik(query)
    
    if company_info:
        cik = company_info[0]  # extract cik
        year = input("Enter the year for the filing: ")  # get year input
        filing_type = input("Type of filing (annual or quarterly): ").lower()  # get filing type input

        if filing_type == 'annual':
            annual_filing = sec_edgar.annual_filing(cik, year)
            if annual_filing:
                print(f"Accession Number: {annual_filing['accession_number']}\nDocument URL: {annual_filing['document_url']}\nDescription: {annual_filing['description']}\n")
            else:
                print(f"No 10-K found for {year}.")
        elif filing_type == 'quarterly':
            quarter = input("Enter the quarter (1-4): ")  # get quarter input
            quarterly_filing = sec_edgar.quarterly_filing(cik, year, quarter)
            if quarterly_filing:
                print(f"Accession Number: {quarterly_filing['accession_number']}\nDocument URL: {quarterly_filing['document_url']}\nDescription: {quarterly_filing['description']}\n")
            else:
                print(f"No 10-Q found for Q{quarter} {year}.")
        else:
            print("Invalid filing type entered. Please choose 'annual' or 'quarterly'.")
    else:
        print(f"No company found for '{query}'. Make sure it's a publicly-traded company.")
