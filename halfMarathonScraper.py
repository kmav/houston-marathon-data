from bs4 import BeautifulSoup
import urllib
import csv

#URL Link Format: 'http://results.houstonmarathon.com/YEAR/?page=1&event=HALF&num_results=1000&pid=list' 
# --> Retrieves 1000 Results for the YEAR Houston HALF Marathon


date = "2016"

#This page lists all the links for each runner's statistics - we need to get all of these links
r = urllib.urlopen("http://results.houstonmarathon.com/" + date + "/?page=1&event=HALF&num_results=1000&pid=list").read()
soup = BeautifulSoup(r, "lxml")

#Base URL for forming new URLs
baseURL = "http://results.houstonmarathon.com/" + date + "/"

#Identifies the number of pages of links to go through
numPages = int(soup.select("#cbox-left > div.cbox-content > div.list > div.pages > a:nth-of-type(4)")[0].string)

links = []

for page in range(1,numPages+1):

	r = urllib.urlopen("http://results.houstonmarathon.com/" + date + "/?page=" + str(page) + "&event=HALF&num_results=1000&pid=list").read()
	linkListings = BeautifulSoup(r, "lxml")

	#Forms the URL to the runner's statistics page and appends it
	for sibling in linkListings.select("#cbox-left > div.cbox-content > div.list > table > tbody > tr"):
		newURL = baseURL + sibling.select("td:nth-of-type(4) > a")[0]["href"]
		links.append(newURL)

	print "done scraping page" + str(page)

#Scrapes each runner's statistics page and writes the relevant statistic to a csv

with open('halfMarathon2016.csv', 'w') as csvfile:
	fieldnames = ['bibNum', 'gender', 'finishNet', 'finishNetConverted', '5K', '10K', '15K', '20K', '25K']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()

	for link in links:

		r = urllib.urlopen(link).read()
		soup = BeautifulSoup(r, "lxml")

		runner = {}

		runner["bibNum"] = soup.select("#cbox-left > div.cbox-content > div.detail > div.detail-content > div.detail-channel.channel-left > div.detail-box.box-general > div > table > tbody > tr.list-highlight.f-start_no_text > td.f-start_no_text.last")[0].string
		runner["gender"] = soup.select("#cbox-left > div.cbox-content > div.detail > div.detail-content > div.detail-channel.channel-left > div.detail-box.box-general > div > table > tbody > tr.list-highlight.f-sex > td.f-sex.last")[0].string
		runner["finishNet"] = soup.select("#cbox-left > div.cbox-content > div.detail > div.detail-content > div.detail-channel.channel-right > div.detail-box.box-splits > div > table > tbody > tr.f-time_finish_netto.split > td.time")[0].string
		
		hours = int(runner["finishNet"][0:2])
		minutes = int(runner["finishNet"][3:5])
		seconds = int(runner["finishNet"][6:8])
		
		runner["finishNetConverted"] = 60*60*hours + 60*minutes + seconds

		i = 5
		for sibling in soup.select("#cbox-left > div.cbox-content > div.detail > div.detail-content > div.detail-channel.channel-right > div.detail-box.box-splits > div > table > tbody > tr"):
			split = str(i) + "K"
			runner[split] = sibling.select("td:nth-of-type(6)")[0].string
			i += 5

		writer.writerow(runner)


