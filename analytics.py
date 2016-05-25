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
try:
    syslog = logging.handlers.SysLogHandler(address='/dev/log')
    syslog.setLevel(logging.WARN)
    syslog.setFormatter(formatter)
    log.addHandler(syslog)

except:
	pass

def setup_arguments():
    parser = argparse.ArgumentParser(description='Hacking Labs Observatory')
    parser.add_argument('-d', action='store_true', dest='debug',default=False, help='Enable debug logging')
    parser.add_argument('-t', action='store', type=str, required=True, dest='data',default=False,help='Location of CSV file containing results')
    parser.add_argument('-p', action='store', type=str, required=False, default='analytics',dest='result',help='Directory to which the results of the analytics are written')
    return parser.parse_args()

def create_data_frame(path):
    df = pd.read_csv(path)
    return df

def save_figure(plot, name):
    fig = plot.get_figure()
    fig.savefig(os.path.join(args.result, name))
    log.debug('Save figure (%s)', name)

def main():

    log.info("Hacking Labs Analytics started")

    path = args.data
    df = create_data_frame(path)

    log.info('Finished importing, [%d] rows to DataFrame', df.shape[0])
    print(df.head())

    log.info("Analytics ended")

if __name__ == "__main__":

    global args
    args = setup_arguments()
    setup_logging(args.debug)

    main()
