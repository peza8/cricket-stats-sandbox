## Get Cricket Data

Scripts for scraping [espncricinfo.com](http://www.espncricinfo.com/) and data on over 43,000 cricket matches.
Initial repo is extremely sparse and specific in the stats analytics, but will be generalized in future. More work to come

## Quickstart
---

  1. A requirements.txt file has yet to be setup, so the dependancies will have to be installed individually with pip. 
  2. Will run with python 2.7 or 3.x
  3. Run `$ python main.py`

## Data
---

Data is written to the data dir, and is in csv form. This can be exported if necessary.

## First insight: Prob of loss vs 1st innings score
---

The current code produces a graph of the probability of loss vs 1st innings score. Intuitively you'd expect this to monotonically decrease, but there are some oddities. It's also cool to see the actual probabilities - i.e. after 450, there's near 0% chance of loss. 