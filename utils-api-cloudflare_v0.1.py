"""
Author: Juan Almanza
Date: 1/31/2024
Version 0.1
Purpose: Faciliate retrieving domain data from Cloudflare via API.
Details: Requires reference to a file containing API key data. Will retrieve live/active domains and all records for each of those domains. The resulting record sets are saved as a CSV.

Notes: Currently does not support pagination on API responses.

"""

#Import libraries
import datetime
import json
import requests
import time
import argparse
import pandas
import os
from pathlib import Path
from math import ceil as mceil

#Script execution begins
print("==============================")
print("Start script [" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "]...\n")

#Verbose output print method
def printv(msg):
    if args["verbose"]:
        print(str(msg))

def cexit():
    print("\nExiting script [" + datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S") + "]...")
    print("==============================")
    quit()

#Parse arguments
parser = argparse.ArgumentParser(description = "This script is a work in progress. It is meant to faciliate retrieving domain data from Cloudflare via API.", formatter_class = argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-k", "--keypath", help = "Absolute or relative directory path where the file containing API key data is located. If omitted, the current working directory is searched.")
parser.add_argument("-s", "--storepath", help = "Absolute or relative directory path where API responses will be saved. If omitted, the current working directory is used.")
parser.add_argument("-v", "--verbose", action = "store_true", help = "Increase script verbosity. Default is false.")
args = vars(parser.parse_args())

#Path to API key data
if args["keypath"]:
    if Path(args["keypath"]).is_file():
        path_keys = os.path.abspath(args["keypath"])
    else:
        if Path(os.getcwd() + args["keypath"]).is_file():
            path_keys = os.getcwd() + args["keypath"]
        else:
            print("\nERROR: API key file path argument is not a file or insufficient permissions! Exiting...\n")
            exit()
else:
    print("\nERROR: Mandatory argument for API key file path was not provided. Exiting...\n")

#Path to configuration files
if args["storepath"]:
    if Path(args["storepath"]).is_dir() and not Path(args["storepath"]).is_file():
        path_save = args["storepath"]
    else:
        print("\nERROR: Search path argument is not a directory or insufficient permissions! Exiting...\n")
        exit()
else:
    if Path(os.getcwd()).is_dir():
        path_save = os.getcwd()
    else:
        print("\nERROR: No search path argument provided and writing to current working directory is not permitted! Exiting...\n")
        exit()

#Read API key data. Max lines read is 20. Lines beginning with symbol # are treated as comments.
keydata = []
print("Attempting to ingest API key data from file: " + str(path_keys))
with open(path_keys, 'r') as k:
    for l, line in enumerate(k):
        if l < 10:
            if (len(keydata) < 3):
                if line[:1] == "#":
                    continue
                else:
                    keydata.append(str(line).rstrip('\n'))
#Check if we ingested the necessary data
if len(keydata) < 3:
    print("ERROR: Maximum number of non-comment lines read from API key data file (10) and failed to find expected data. Verify file contents and try again.")
    cexit()

#Variables
api_responses = []
url_base = "https://api.cloudflare.com/client/v4/"
cf_account_id = str(keydata[0])
headers = {
    "Content-Type": "application/json",
    "X-Auth-Email": str(keydata[1]),
    "Authorization": "Bearer " + str(keydata[2])
}

#Get all domains for account
print("Retrieving all domains...")
domain_list = []
domain_list_response = json.loads(str(requests.get(url_base + "/zones", headers=headers).text))
if not domain_list_response["success"]:
    print("API call failed with reason:\n" + json.dumps(domain_list_response["errors"], sort_keys=True, indent=4))
else:
    print("Successfully retrieved [" + str(domain_list_response["result_info"]["total_count"]) + "] domains...")
    for d in domain_list_response["result"]:
        print("\tDomain: " + d["name"] + "\t\tStatus: " + d["status"])
        if d["status"] == "active":
            domain_list.append(d["id"])

#Get all records for each domain
print("Retrieving all records for domain list. It will take at least " + str(mceil(len(domain_list) * 1.1)) + " seconds due to API rate-limiting...")
for domain in domain_list:
    time.sleep(1.1)
    t_combined_url = url_base + "/zones/" + str(domain) + "/dns_records"
    r = json.loads(str(requests.get(t_combined_url, headers=headers).text))
    if r["success"]:
        print("Successfully retrieved [" + str(r["result_info"]["total_count"]) + "] records for domain:\t" + r["result"][0]["zone_name"])
        #Save "result" JSON object
        df = pandas.json_normalize(r["result"])
        df.to_csv(os.path.join(path_save, r["result"][0]["zone_name"] + "_records_" + datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S") + ".csv"))

#Exit notify
cexit()
