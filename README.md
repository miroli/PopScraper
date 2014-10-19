PopScraper
==========

A Python scraper for www.popfakta.se, an ASP.NET-powered webpage. On initialization, the PopScraper object starts a session which persists cookies in subsequent requests. After each `200 OK` response, the scraper parses out the `__VIEWSTATE`, `__VIEWSTATEGENERATOR` and `__EVENTVALIDATION` parameters and passes them along in the next request. 

###Installation
Download the zip file for this repository, or run
      
    git clone git@github.com:vienno/PopScraper.git
at the command line. Then install the required packages, using pip.

    pip install -r requirements.txt
    
###Usage
PopScraper supports search by artist, start year and end year. The results are saved to `results.csv` per default, but this can be configured with the `filename` parameter on initialization. One "page" is equivalent to 50 records.

    import PopScraper
    
    # Get all records from Håkan Hellström
    scraper = PopScraper(artist='Håkan Hellström', filename='hakan.csv')
    scraper.fetch_all()
    
    # Get all records from 2006 and later
    scraper = PopScraper(year_start='2006', filename='2006.csv')
    scraper.fetch_all()
    
    # Use fetch instead of fetch_all to grab just the first page
    scraper.fetch()
    
###Environment
PopScraper is tested with Python 2.7 on OS X Mavericks.
