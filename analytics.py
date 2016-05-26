import os
import rsa
import sys
import json
import math
import time
import atexit
import base64
import random
import signal
import hashlib
import argparse
import datetime
import queue
import pprint

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import logging
import logging.handlers

pid = '/tmp/analytics.pid'
pp = pprint.PrettyPrinter(indent=4)
log = logging.getLogger("Analytics")

# Configurations
pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 10)

def setup_logging(debug):
    formatter = logging.Formatter("[%(asctime)s] (%(levelname)s) %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    if debug:
        log.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    log.addHandler(ch)

def setup_arguments():
    parser = argparse.ArgumentParser(description='Hacking Labs Observatory')
    parser.add_argument('-d', action='store_true', dest='debug',default=False, help='Enable debug logging')
    parser.add_argument('-t', action='store', type=str, required=True, dest='data',default=False,help='Location of CSV file containing results')
    parser.add_argument('-p', action='store', type=str, required=False, default='analytics',dest='result',help='Directory to which the results of the analytics are written')
    return parser.parse_args()

def create_data_frame(path):
    df = pd.read_csv(path, skiprows=6)

    gender_scale = {'m':'Male','f':'Female'}
    age_scale = {'a':'18-25', 'b':'26-35', 'c':'36-45', 'd':'46-55','e':'56-90'}
    usage_scale = {'a':'Never', 'b':'Sometimes', 'c':'Often', 'd':'Very Often'}
    verification_scale = {'a':'Yes, always','b':'Yes, sometimes','c':'Every now and then', 'd':'No never'}

    # Set the appropiate columns to categories
    for col in ["Gender","Age","Usage",'Connection Secure', 'Connection Secure (Banking)']:
        df[col] = df[col].astype('category')

    # Assign appropiate names for categories
    df['Gender'] = df['Gender'].apply(lambda x: gender_scale[x])
    df['Age'] = df['Age'].apply(lambda x: age_scale[x])
    df['Usage'] = df['Usage'].apply(lambda x: usage_scale[x])
    for col in ['Connection Secure', 'Connection Secure (Banking)']:
        df[col] = df[col].apply(lambda x: verification_scale[x])

    log.info('Finished importing, [%d] rows to DataFrame', df.shape[0])
    log.debug("\n%s",df[['Gender','Age','Usage']].head())
    return df

def create_demographic_graph(df):
    group = df[["Gender","Age"]].groupby(['Gender','Age']).size()
    plot = group.plot(kind="pie")
    save_figure(plot, "demographic")
    log.info("Generated Demographic chart")

def save_figure(plot, name):
    fig = plot.get_figure()
    fig.savefig(os.path.join(args.result, name))
    log.debug('Save figure (%s)', name)

def main():

    log.info("Cyber Crime Science Analytics started")

    df = create_data_frame(args.data)

    # Create charts
    create_demographic_graph(df)

    log.info("Analytics ended")

if __name__ == "__main__":

    global args
    args = setup_arguments()
    setup_logging(args.debug)

    main()
