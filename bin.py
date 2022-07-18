from datetime import datetime, timedelta
from bs4 import BeautifulSoup as bs
import requests

##CUSTOM routine for the coventry council bin website
#Returns a dictionary with the next collection date, and the bins to collect
def getnextcollectioninfo():
    #Get current datetime
    now = datetime.now()
    current_year = now.year

    #Retrieve webpage
    webpage = requests.get("https://www.coventry.gov.uk/binswednesdayb")
    #Get soup object from webpage
    soup = bs(webpage.text, 'html.parser')

    #Determine which months listing we need by getting the last bin date
    #of the first month.
    #Get the required string and split off the date text
    month0_last_date_txt = soup.find_all(class_='editor')[0].find_all('li')[-1].text.split(":")[0]
    #Parse the date text into a datetime object
    month0_last_date = datetime.strptime(month0_last_date_txt, '%A %d %B')
    month0_last_date = month0_last_date.replace(current_year)
    #If now is before the last date in month 0, use month 0
    #Otherwise it should be month 1
    idx_to_use = 0 if now < month0_last_date else 1

    #Get all the bin listings for the determined month
    month_listings = soup.find_all(class_='editor')[idx_to_use].find_all('li')

    return_date_text = ""
    return_bin_text = ""

    #Iterate until we determine the correct one
    for listing in month_listings:
        split_text = listing.text.split(":")
        date_text = split_text[0]
        bin_text = split_text[1]
        date = datetime.strptime(date_text, '%A %d %B')
        date = date.replace(current_year)

        #If 7 days from now is past the bin date then this is the correct bin
        if now + timedelta(days=7) > date and now < date:
            return_date_text = date_text
            return_bin_text = bin_text
            break

    bins = ""
    if "green" in return_bin_text:
        bins = "green-lidded bin"
    elif "brown" in return_bin_text:
        bins = "brown and blue-lidded bins"
    else:
        bins = "UNRECOGNISED BIN"

    binfo = {'DATE': return_date_text, 'BINS': bins}

    return binfo

#Simple method to convert the dictionary to a string format
def getnextcollection():
    binfo = getnextcollectioninfo()

    return_string = "The next collection is for the " + binfo['BINS'] + " on " + binfo['DATE'] + "."

    return return_string