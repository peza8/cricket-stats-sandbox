"""
    Sandbox file for playing with cricket stats
    Josh Perry
"""

import matplotlib.pyplot as plt
import numpy as np
import csv 
import time
import urllib2
from bs4 import BeautifulSoup

fetch_data = False
graph_result = True

class TestMatch:
    def __init__(self, row, i):
        #  0      1      2     3    4     5      6      7          8        9      10
        # Team, Score, Overs, RPO, Lead, Inns, Result, Opposition, Ground, Date
        self.team1      = row[0]
        self.inns_no    = row[5]
        self.result     = row[6]
        self.date       = row[10]
        self.index      = i
        self.lost       = False

        inns_str = row[1]
        inns_comp = inns_str.split("/")
        self.inns_score = int(inns_comp[0])

        # Assess team batting first win / loss
        if self.result == "lost":
            self.lost = True

class InningsInterval:
    def __init__(self, l_bound, u_bound):
        self.lower = l_bound
        self.upper = u_bound
        self.match_count = 0
        self.loss_count  = 0
        self.loss_prob   = 0.0

    def addMatch(self, match):
        self.match_count += 1

        # Assess win / loss
        if match.lost:
            self.loss_count += 1
        self.loss_prob = float(self.loss_count)/float(self.match_count)

    def addStats(self, matches, losses, prob):
        self.match_count = int(matches)
        self.loss_count = int(losses)
        if self.match_count > 0:
            self.loss_prob = float(losses)/float(matches)

def GetTestData():
    print("Fetching html data")
    matches = []
    start_page = 1
    max_results = 305

    for page_no in range(start_page, max_results):
        # Could well change !!
        print("Fetching page %i" % page_no)
        url_p1 = "http://stats.espncricinfo.com/ci/engine/stats/index.html?class=11;"
        url_p2 = "page=" + str(page_no) + ";"
        url_p3 = "result=1;result=2;result=3;result=4;spanmin1=15+Mar+1980;spanval1=span;template=results;type=team;view=innings"
        url_str = url_p1 + url_p2 + url_p3 
        
        # Fetch html and wait 1s
        page = urllib2.urlopen(url_str)
        time.sleep(1)

        # parse the html using beautiful soup and store in variable `soup`
        soup = BeautifulSoup(page, "html.parser")

        # Unique element = 'engineTable'
        # name_box = soup.find(‘h1’, attrs={‘class’: ‘engineTable’})
        raw_matches_html = soup.find_all('tr')
        start_index = 7
        i = 0
        
        for match_raw in raw_matches_html:
            # Skip first 7 entries - garbage
            if (i < start_index):
                i += 1
                continue

            line = match_raw.text.strip()
            match_comp = line.split("\n")
            if (len(match_comp) < 10) or len(match_comp[1]) == 0:
                # Catches odd entries
                continue
           
            match = TestMatch(match_comp, i-7+page_no)
            if (match.inns_no == "1"):
                matches.append(match)
                i += 1

    return matches

def GetCSVData(file_path):
    print("Getting CSV data as string")
    rows = []
    
    with open(file_path, 'r') as raw_data:
        reader = csv.reader(raw_data)
        reader.next() # skip column headers
        for row in reader: 
            rows.append(row) 

    raw_data.close()
    print("Got all data from csv. Closing file.")
    return rows

def ComputeFirstInningsLossRate(matches):
    # Generate x-axis values
    first_innings_loss_rates = []
    step = 10

    for runs in range(0, 1000, step):
        interval = InningsInterval(runs, runs+step)
        first_innings_loss_rates.append(interval)

    # Check all the games for the results
    for match in matches:
        # Get correct interval base on score
        index = match.inns_score//10
        interval = first_innings_loss_rates[index] # Needs to return pointer ?
        interval.addMatch(match)
    
    print("Computed first innings loss rates")
    return first_innings_loss_rates

def WriteInnsDataToCSV(first_inns_losses, path):
    print("Writing first innsings losses to file")
    with open(path, "w") as csv_target:
        csv_writer = csv.writer(csv_target)
        csv_writer.writerow(["Lower bound", "Upper bound", "Match count", "Loss count", "loss probability"])

        for interval in first_inns_losses:
            row = [interval.lower, interval.upper, interval.match_count, interval.loss_count, interval.loss_prob]
            csv_writer.writerow(row)
    
        csv_target.close()

    print("Completed CSV write")

def GetIntervalDataFromRows(csv_rows):
    # lower bound, upper bound, match count, loss count, loss prob
    intervals = []
    for row in csv_rows:
        interval = InningsInterval(row[0], row[1])
        interval.addStats(row[2],row[3],row[4])
        intervals.append(interval)
    return intervals

def WindowFilter(y_data):
    print("Applying simple digital window filter (triangle)")
    data_points = len(y_data)
    f_y = []
    ws = 2
    weights = [0.1, 0.2, 0.4, 0.2, 0.1]

    for i in range(0, data_points):
        if i<2 or i > (data_points-3):
            f_y.append(y_data[i])
        else:
            weighted_prob = 0
            for j in range(-2, 3):
                weighted_prob += y_data[i+j]*weights[j]
            f_y.append(weighted_prob)

    print("Completed low pass filter")
    return f_y
        

def GraphIntervals(intervals):
    x_data = []
    y_data =[]
    for interval in intervals:
        x = (float(interval.lower) + float(interval.upper))/2
        y = interval.loss_prob * 100.0
        x_data.append(x)
        y_data.append(y)
    
    

    fig = plt.figure()
    g1 = fig.add_subplot(211)
    g1.set_ylabel('Probability of loss')
    g1.set_xlabel('1st innings runs scored')
    g1.set_title('First innings scores vs probability of loss')
    plt.xlim(50, 680)
    g1.plot(x_data, y_data)

    # Look at filtered data
    """
    y_filtered = WindowFilter(y_data)
    g2 = fig.add_axes([0.13, 0.08, 0.8, 0.35])
    plt.xlim(20, 680)
    g2.plot(x_data, y_filtered)
    """

    plt.show()

def main():
    print("Firing up cricket stats program")
    innings_data_file = "./data/first_inns_loss_rate.csv"
    if fetch_data:
        matches = GetTestData()
        loss_rate = ComputeFirstInningsLossRate(matches)
        WriteInnsDataToCSV(loss_rate, innings_data_file)

    # Present data 
    if graph_result:
        rows = GetCSVData(innings_data_file)
        intervals = GetIntervalDataFromRows(rows)
        GraphIntervals(intervals)
    
    print("Completed cricket script")

main()