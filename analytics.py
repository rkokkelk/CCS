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
import matplotlib
import matplotlib.pyplot as plt

import logging
import logging.handlers

pid = '/tmp/analytics.pid'
pp = pprint.PrettyPrinter(indent=4)
log = logging.getLogger("Analytics")

# Configurations
matplotlib.style.use('ggplot')
pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 10)

colors = {'g':'darksage','r':'orangered','b':'deepskyblue','y':'gold'}

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

    df['Total'] = df['Question 1'] + df['Question 2'] + df['Question 3'] + df['Question 4'] + df['Question 5'] + df['Question 6']

    log.info('Finished importing, [%d] rows to DataFrame', df.shape[0])
    log.debug("\n%s",df[['Gender','Age','Usage','Total']])
    return df

def create_total_score_gender_graph(df):
    data = pd.crosstab(df['Gender'],df['Total'])
    plot = data.plot(kind='bar')
    save_figure(plot, 'score_gender')
    log.info('Generated total gender usage')

def create_total_score_graph(df):
    plot = df[['Age','Total']].sort_values(by='Total').plot(kind='barh')
    save_figure(plot,'total_score')
    log.info('Generated total_score graph')

def create_questions_score_graph(df):
    boolean_scale = {-1: 'Incorrect',1:'Correct'}
    for q in range(1,7):
        col = 'Question %d' % q
        df[col] = df[col].apply(lambda x: boolean_scale[x])
        group = df[["Age",col]].groupby([col,'Age']).size()
        group = group.unstack(level=0)
        group = group.fillna(0)
        plot = group.plot(kind='barh',stacked=True)
        save_figure(plot,col+'_score')
    log.info('Generated questions score graph')

def create_demographic_graph(df):
    group = df[["Gender","Age"]].groupby(['Gender','Age']).size()
    plot = group.plot(kind="pie",autopct='%d')
    log.debug("\n%s", group)
    save_figure(plot, "demographic")
    log.info("Generated Demographic chart")

def create_internet_usage(df):
    data = pd.crosstab(df['Age'],df['Usage'])
    plot = data.plot(kind='barh',stacked=True)
    save_figure(plot, 'internet_usage')
    log.info('Generated internet usage')

def create_secure_usage_graph(df):
    data = pd.crosstab(df['Age'],df['Connection Secure'])
    plot = data.plot(kind='barh',stacked=True)
    save_figure(plot, 'verifying_connection')

    data = pd.crosstab(df['Age'],df['Connection Secure (Banking)'])
    plot = data.plot(kind='barh',stacked=True)
    save_figure(plot, 'verifying_connection_banking')
    log.info('Generated Secure connection graphs')

def create_overal_graph(df):
    df2 = df[['Total']]
    df2['total_security'] = df['Padlock']+df['Internet Safety']
    df2 = df2.groupby(['total_security','Total']).size().reset_index(name='Count')
    log.debug("\n%s",df2)
    plot = df2.plot(kind='scatter',x='total_security',y='Total',s=df2['Count']*150)
    save_figure(plot, 'scatter_total_score')
    log.info('Generated scattered total score')

def save_figure(plot, name):
    fig = plot.get_figure()
    fig.savefig(os.path.join(args.result, name))
    log.debug('Save figure (%s)', name)

def main():

    log.info("Cyber Crime Science Analytics started")

    df = create_data_frame(args.data)

    # Create charts
    create_demographic_graph(df)
    create_total_score_gender_graph(df)
    create_internet_usage(df)
    create_overal_graph(df)
    create_total_score_graph(df)
    create_questions_score_graph(df)
    create_secure_usage_graph(df)

    log.info("Analytics ended")

if __name__ == "__main__":

    global args
    args = setup_arguments()
    setup_logging(args.debug)

    main()
