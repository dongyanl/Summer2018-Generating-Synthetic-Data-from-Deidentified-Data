#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 13:52:12 2018

@author: dongyanglu
"""

import pandas as pd
import difflib
from datetime import datetime
import random
import collections
from collections import OrderedDict
import numpy as np
from scipy import stats
from copulas.multivariate.GaussianCopula import GaussianCopula
import statsanalysis

class modeler:
    
    def __init__(self):
        pass

    def process_missing(self,df):
        
        for col in df.columns:
            if df[col].isnull().values.all() == False:
                if df[col].isnull().values.any() == True:
                    df[col + '_isoriginal'] = 'Yes'
                    for i in range(len(df[col])):
                        if pd.isnull(df[col].iloc[i]):
                            df[col].iloc[i] = random.choice(df[col].unique())
                            df[col + '_isoriginal'].iloc[i] = 'No'
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
    
    def process_categorical(self, df):
        cated = {}
        for col in df.columns:
            if df[col].isnull().values.all() == False and df[col].dtypes == 'object':
                l = list(df[col])
                c = collections.Counter(l)
                d = OrderedDict((i[0],float(i[1])/len(l)) for i in c.most_common(len(c)))
                interval = [sum(list(d.values())[:i]) for i in range(len(d)+1)]
                d = OrderedDict((list(d.keys())[i],(interval[i],interval[i+1])) for i in range(len(d)))
                for i in range(len(df[col])):
                    a = d[df[col].iloc[i]][0]
                    b = d[df[col].iloc[i]][1]
                    mu = (a+b)/2
                    sig = (b-a)/6
                    df[col].iloc[i] = np.random.normal(loc=mu,scale=sig)
                cated[col] = d
#            print (col)
        return df, cated
            
    def process_datetime(self, df):
        for col in df.columns:
            if df[col].isnull().values.all()==False and df[col].dtypes=='<M8[ns]':
               for i in range(len(df)):
                   df[col].iloc[i] = (df[col].iloc[i]-datetime(1970,1,1)).total_seconds()
        return df
    
    def get_distribs(self, df):
#        distribs_list = ['uniform','expon']
        distribs = {}
        for col in df.columns:
            a = df[col].min()
            b = df[col].max()
            m = df[col].mean()
            std = df[col].std()
            p = stats.kstest(df[col], stats.norm(m, std).cdf)[1]
            dist = ('norm', m, std)
    
            if stats.kstest(df[col], stats.uniform(a,b).cdf)[1] > p:
                    p = stats.kstest(df[col], stats.uniform(a,b).cdf)[1]
                    dist = ('uniform', a, b)
            
            if stats.kstest(df[col], stats.expon(m).cdf)[1] > p:
                p = stats.kstest(df[col], stats.expon(m).cdf)[1]
                dist = ('exponential', m, m)
               
            if m!=0 and std!=0:
                alpha = (((1-m)/std**2)-1/m)*m**2
                beta = alpha*(1/m - 1)
                if stats.kstest(df[col], stats.beta(alpha, beta).cdf)[1] > p:
                    p = stats.kstest(df[col], stats.beta(alpha, beta).cdf)[1]
                    dist = ('beta', alpha, beta)
                
            distribs[col] = dist
        return distribs
    
    def get_covariance(self, df):
        gc = GaussianCopula()
        gc.fit(df)
        return gc.cov_matrix
    
    def stu_model(self, df, stu):
        params = {}
        for s in stu:
            params[s] = self.get_distribs(stu[s])
        return params


#stu = statsanalysis.stu_list(statsanalysis.df)
#
#        
#transformed_stu = dict.copy(stu)
#cate = {}
#params = {}
#for s in transformed_stu:
#    sdf = transformed_stu[s]
#    sdf = process_missing(sdf)  
#    sdf = process_datatype(sdf)
#    sdf, catedict = process_categorical(sdf)
#    sdf = process_datetime(sdf)
#    transformed_stu[s] = sdf
#    cate[s] = catedict
#    newsdf = sdf.dropna(axis=1,how='all')
#    newsdf = newsdf.astype(float)
#    distribs = get_distribs(newsdf)
##    cov = get_covariance(newsdf) 
#    params[s] = distribs
    
    
                
    
            