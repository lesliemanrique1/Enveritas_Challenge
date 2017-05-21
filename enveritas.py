import pandas as pd
import numpy as np
from datetime import datetime
from fuzzywuzzy import fuzz
import sys 
import math


def survey_length(df):
	df["started_time"] = df["started_time"].apply(lambda x : datetime.strptime(x,"%m/%d/%y %H:%M"))
	df["ended_time"] = df["ended_time"].apply(lambda x : datetime.strptime(x,"%m/%d/%y %H:%M"))
	df["survey_length"] = df["ended_time"] - df["started_time"]
	return df



def percent_shortest(df,perc=.10):
	xpercent = int(len(df["survey_length"]) * perc)
	sorted_percentile = sorted(df["survey_length"])[0:xpercent]
	def matchesPercentile(x):
	    if x in sorted_percentile:
	        return True
	    return False
	df["shortest"] = map(matchesPercentile,df["survey_length"])
	return df


def performance_measure(df):
	performance = list()
	fail = ['endosulfan', 'gramaxon', 'paraquat', 'preglone', 'parathion', 'terbufos', 'thiodan', 'vidate']
	for index, row in df.iterrows():
		if row["uses_chemicals"] == 0:
			performance.append("NA")
		else:
			chemicals = [row["herbicides"],row["other_herbicides"],row["fertilizers"],row["other_fertilizers"],row["insecticides"],row["other_insecticides"]]
			chem_fails = []
			for chem in chemicals:
			    def check_fails(x):
			        try:
			            return fuzz.partial_ratio(chem,x)
			        except:
			            return 0 
			    fail_ratios = map(check_fails,fail)
			    chem_fails.append(max(fail_ratios))
			if max(chem_fails)>85:
				performance.append("F")
			else:
				performance.append("P")

	df["performance"] = performance

	return df



if __name__ == "__main__":
	path = sys.argv[1]
	#reads the csv into a pandas dataframe
	df = pd.read_csv(path)
	#adds a new column "survey_length" 
	df = survey_length(df)
	#adds a boolean column "shortest" that represents whether or not the survey is among the 10% of shortest surveys in the dataset.
	df = percent_shortest(df)
	#adds a column "performance" that represents the farmer's performance on the "No Banned Pesticides" criterion
	df = performance_measure(df)
	df.to_csv('out.csv', sep=',')


