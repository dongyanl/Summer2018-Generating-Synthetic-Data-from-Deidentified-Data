#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 18 14:08:49 2018

@author: dongyanglu
"""


import pandas as pd
import difflib
from datetime import datetime
from datetime import timedelta
import random
import collections
from collections import OrderedDict
import numpy as np
from scipy import stats
from copulas.multivariate.GaussianCopula import GaussianCopula
from statsanalysis import stats_analysis
from sdv import modeler
import argparse
import json
from DAFM.main import KCModel



class sampler:
    def __init__ (self):
        parser = argparse.ArgumentParser(description='Process inputs.')
        parser.add_argument('--dataset_path', nargs=1, type=str, default=["./Example/example.txt"])
        parser.add_argument('--num_of_stu', nargs=1, type=int, default=[2])

        args = parser.parse_args()
        data_path = args.dataset_path[0]
        
        sa_obj = stats_analysis()
        self.df = sa_obj.import_data(data_path)
        self.df = sa_obj.process_datatype(self.df)
        
        meta = sa_obj.create_meta(self.df)
        with open('report.json', 'w') as f:
            json.dump(meta, f, sort_keys=True, indent=4)
            
        sdv_obj = modeler()
        self.stu = sa_obj.stu_list(self.df)
        self.transformed_stu = dict.copy(self.stu)
        
        self.cate = {}
        self.params = {}
        for s in self.transformed_stu:
            sdf = self.transformed_stu[s]
            sdf = sdv_obj.process_missing(sdf)  
            sdf = sdv_obj.process_datatype(sdf)
            sdf, catedict = sdv_obj.process_categorical(sdf)
            sdf = sdv_obj.process_datetime(sdf)
            self.transformed_stu[s] = sdf
            self.cate[s] = catedict
            newsdf = sdf.dropna(axis=1,how='all')
            newsdf = newsdf.astype(float)
            distribs = sdv_obj.get_distribs(newsdf)
        #    cov = get_covariance(newsdf) 
            self.params[s] = distribs
        
        self.n = args.num_of_stu[0]
            
    
    def create_stu(self, newdf):
        s = random.choice(list(self.transformed_stu.keys()))
        originaldf = self.stu[s]
        
        distrib = self.params[s]
        dist, a, b = distrib['Problem Name']
        if dist == 'norm':
            problemnum = np.random.normal(a,b,1)[0]
        elif dist == 'uniform':
            problemnum = np.random.uniform(a,b,1)[0]
        elif dist == 'exponential':
            problemnum = np.random.exponential(a,1)[0]
        elif dist == 'beta':
            problemnum = np.random.beta(a,b,1)[0]
        problemcate = self.cate[s]['Problem Name']
        for key, value in problemcate.items():
            if value[0] <= problemnum <=value[1]:
                problem = key
                break
        newdf = originaldf[(originaldf['Problem Name']==problem) & (originaldf['Attempt At Step']==1)
            &(originaldf['Problem View']==1)]
        try:
            newstu = s[:5]+str(int(s[5])+1)+s[6:]
        except:
            newstu = s.replace(s[5],'1')
        
        newdf['Anon Student Id'] = newstu
        sessionid = newdf['Session Id'].iloc[0]
        try:
            newdf['Session Id'] = sessionid[:-1] + str(int(sessionid[-1])+1)
        except:
            newdf['Session Id'] = sessionid.replace(sessionid[-1], '1')
        return newdf, newstu, distrib, s
    
    def create_time(self, newdf, stuid, distrib, oristu):
        dist, a, b = distrib['Time']
        if dist == 'norm':
            starttime = np.random.normal(a,b,1)[0]
        elif dist == 'uniform':
            starttime = np.random.uniform(a,b,1)[0]
        elif dist == 'exponential':
            starttime = np.random.exponential(a,1)[0]
        elif dist == 'beta':
            starttime = np.random.beta(a,b,1)[0]
        starttime = datetime.fromtimestamp(starttime)
        newdf['Time'].iloc[0] = starttime
        newdf['Problem Start Time'] = starttime
        for i in range(len(newdf)):
            dist, a, b = distrib['Duration (sec)']
            duration = np.random.uniform(a,b)
            newdf['Duration (sec)'].iloc[i] = duration
            if i != len(newdf)-1:
                newdf['Time'].iloc[i+1] = newdf['Time'].iloc[i] + timedelta(seconds=duration)
            tid = newdf['Transaction Id'].iloc[i] 
            try:
                newdf['Transaction Id'].iloc[i] = tid[:-1] + str(int(tid[-1])+1)
            except:
                newdf['Transaction Id'].iloc[i] = tid.replace(tid[-1], '1')
        
        return newdf
    
    def create_outcome(self, newdf, stuid, distrib, oristu):
        i = 0
        while i < len(newdf):
            try:
                kcobj = KCModel()
                prob = kcobj.main()
                outcomenum = np.random.choice(2, 1, p=[1-prob, prob])[0]
            except:
                dist, a, b = distrib['Outcome']
                if dist == 'norm':
                    outcomenum = np.random.normal(a,b,1)[0]
                elif dist == 'uniform':
                    outcomenum = np.random.uniform(a,b,1)[0]
                elif dist == 'exponential':
                    outcomenum = np.random.exponential(a,1)[0]
                elif dist == 'beta':
                    outcomenum = np.random.beta(a,b,1)[0]
            outcomecate = self.cate[oristu]['Outcome']
            for key, value in outcomecate.items():
                if value[0] <= outcomenum <=value[1]:
                    outcome = key
                    break
            newdf['Outcome'].iloc[i] = outcome
            if outcome == 'CORRECT':
                newdf['Is Last Attempt'].iloc[i] = 1
            else:
                newdf['Is Last Attempt'].iloc[i] = 0
                
                row = newdf.iloc[i].copy()
                row['Attempt At Step'] = newdf['Attempt At Step'].iloc[i]+1
                newdf = newdf.append(row)
                newdf = newdf.sort_index()
            i+=1
                
        return newdf
    
    def create_synthetic(self):
        newdf = pd.DataFrame(columns=self.df.columns)  
        newdf, stuid, distrib, oristu = self.create_stu(newdf)
        newdf = self.create_outcome(newdf, stuid, distrib, oristu) 
        newdf = self.create_time(newdf, stuid, distrib, oristu)
        with open('synthetic.csv', 'a') as f:
            newdf.to_csv(f, header=False)
            
    def main(self):
        header_df = pd.DataFrame(columns=self.df.columns) 
        with open('synthetic.csv', 'w') as f:
            header_df.to_csv(f, header=True)
        for i in range(self.n):
            self.create_synthetic()

obj = sampler()
obj.main()





        