#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 12:39:51 2018

@author: dongyanglu
"""

import pandas as pd
import difflib
from datetime import datetime
import json


class stats_analysis:
    
    def __init__(self):
        
        pass
    
    def import_data(self, path):
        df = pd.read_csv(path, delimiter="\t")
        return df
    
    def process_datatype(self, df):
      
        df = df.dropna(subset=['Problem Start Time', 'Time'], how='any')
    #    df = df.drop(df[df['Duration (sec)']=='.'].index)
        try:
            df['Duration (sec)'][df['Duration (sec)']=='.'] = 0.0
            df['Duration (sec)'] = df['Duration (sec)'].astype(float)
        except:
            pass
        try:
            df['Time'] = df['Time'].apply(lambda s : datetime.strptime(s, "%Y-%m-%d %H:%M:%S")) 
        except:
            print ('fail to process Time')
        try:
            df['Problem Start Time'] = df['Problem Start Time'].apply(lambda s : datetime.strptime(s, "%Y-%m-%d %H:%M:%S")) 
        except:
            print ('fail to process Problem Start Time')
        return df
    
    def get_overlap(self, l):
        s1 = l.iloc[0]
        for i,s2 in enumerate(l):    
            s = difflib.SequenceMatcher(None, s1, s2)
            pos_a, pos_b, size = s.find_longest_match(0, len(s1), 0, len(s2)) 
            s1 = s1[pos_a:pos_a+size]
        return s1

    def stu_list(self, df):
        stu = {s:df[df['Anon Student Id']==s] for s in df['Anon Student Id'].unique()}
        return stu
    
    def create_meta(self, df):
        stu = {s:df[df['Anon Student Id']==s] for s in df['Anon Student Id'].unique()}
        meta = {}
        meta['students'] = []
        
        for s in stu:
            meta['students'].append({
                    'studentid': s,
                    'fields': self.stats_anal(stu[s])
                    })
        return meta
    
    def stats_anal(self, df):
        datatype = dict(df.dtypes)
        fields = []
        for i in df.columns:
            if df[i].isnull().values.all() == False:
                if datatype[i] == 'object':
                    fields.append(self.summarize_categorical(df,i))
                    
                elif datatype[i] == 'float' or datatype[i] == 'int':
                    fields.append(self.summarize_numerical(df,i))
                    
                elif datatype[i] == 'datetime64[ns]':
                    fields.append(self.summarize_datetime(df,i))
        return fields
    
    def summarize_categorical(self, df, col):
        datatype = dict(df.dtypes)
        l = []
        try:
            l = [len(i) for i in df[col]]
        except:
            pass
        d = {}
        d['name'] = col
        d['datatype'] = str(datatype[col])
        d['total num of values'] = len(df[col])
        d['num of unique values'] = len(df[col].unique())
        if l:
            d['max length'] = max(l)
            d['min length'] = min(l)
            d['overlap characters'] = self.get_overlap(df[col])
        return d
    
    def summarize_numerical(self, df, col):
        datatype = dict(df.dtypes)
        d = {}
        d['name'] = col
        d['datatype'] = str(datatype[col])
        d['num of unique values'] = len(df[col].unique())
        d['max'] = int(df[col].max())
        d['min'] = int(df[col].min())
    #    d['mode'] = str(df[col].mode().iloc[0])
        try:
            d['mean'] = df[col].mean()
            d['std'] = df[col].std()
        except:
            pass
        return d
            
    def summarize_datetime(self, df, col):
        datatype = dict(df.dtypes)
        d = {}
        d['name'] = col
        d['datatype'] = str(datatype[col])
        d['duration'] = (df[col].iloc[-1] - df[col].iloc[0]).total_seconds()
        return d

if __name__ == "__main__":
    path = 'ds2174_tx_2018_0604_111423/Geometry Area (1996-97) [2017 Summer School].txt'
    obj = stats_analysis()
    df = obj.import_data(path)
    df = obj.process_datatype(df)
    datatype = dict(df.dtypes)
    meta = obj.create_meta(df)
    
    with open('report.json', 'w') as f:
        json.dump(meta, f, sort_keys=True, indent=4)












    
    