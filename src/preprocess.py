'''
Created on Sep 13, 2018

@author: Heng.Zhang
'''

import csv
from global_param import *
import pandas as pd
import numpy as np
import datetime

def correct_goodssale():
    goodssale_csv = csv.reader(open(r'%s/goodsale.csv' % (inputPath), 'r'))
    
    goodssale_corrected_file = open(r'%s/goodsale_corrected.csv' % (inputPath), 'w')    
    goodssale_corrected_file.write("data_date,goods_id,sku_id,goods_num,goods_price,orginal_shop_price\n")
    
    index = 0
    for each_goods in goodssale_csv:
        if (index == 0):
            index += 1
            continue

        if (',' in each_goods[4]):
            each_goods[4] = each_goods[4].replace(',', '')
            
        if (',' in each_goods[5]):
            each_goods[5] = each_goods[5].replace(',', '')
            
        goodssale_corrected_file.write("%s,%s,%s,%s,%.2f,%.2f\n" % 
                                       (each_goods[0], each_goods[1], each_goods[2], each_goods[3], float(each_goods[4]), float(each_goods[5])))
    
    

def withdraw_sku(submit_sku, filename):
    print(getCurrentTime(), "handling %s" % filename)
    file_df = pd.read_csv(r'%s/%s' % (inputPath, filename))  
    sku_in_submiting = np.in1d(file_df.sku_id, submit_sku.sku_id)
    file_df[sku_in_submiting].to_csv('%s/in_submiting/%s' % (inputPath, filename), index=False)
    
def withdraw_goods(submit_goods, filename):
    print(getCurrentTime(), "handling %s" % filename)
    file_df = pd.read_csv(r'%s/%s' % (inputPath, filename))  
    goods_in_submiting = np.in1d(file_df.goods_id, submit_goods.goods_id)
    file_df[goods_in_submiting].to_csv('%s/in_submiting/%s' % (inputPath, filename), index=False)


def withdraw_submiting():
    submit_sku = pd.read_csv(r'%s/submit_example.csv' % inputPath)
    
    print(getCurrentTime(), "handling goods_sku_relation")
    goods_sku_relation = pd.read_csv(r'%s/goods_sku_relation.csv' % inputPath)    
    goods_in_submiting = np.in1d(goods_sku_relation.sku_id, submit_sku.sku_id)
    goods_in_submiting = goods_sku_relation[goods_in_submiting]
    goods_in_submiting.to_csv('%s/in_submiting/goods_sku_relation.csv' % inputPath, index=False)
    
    withdraw_goods(goods_in_submiting, 'goodsdaily.csv')
    withdraw_goods(goods_in_submiting, 'goodsinfo.csv')    
    withdraw_sku(submit_sku, 'goodsale_corrected.csv') 
    withdraw_goods(goods_in_submiting, 'goods_promote_with_price.csv')
    
def goodssale_month_var_mean():    
    print(getCurrentTime(), 'loading goodsale..') 
    goodssale_df = pd.read_csv(r'%s/goodsale.csv' % inputPath)
    start_date = datetime.datetime.strptime('20170301', "%Y%m%d").date()
    
    month_start_end = [(20170301, 20170331), (20170401, 20170430), (20170501, 20170531), (20170601, 20170630), (20170701, 20170731), 
                       (20170801, 20170831), (20170901, 20170930), (20171001, 20171031), (20171101, 20171130), (20171201, 20171231), 
                       (20180101, 20180131), (20180201, 20180228),  (20180301, 20180331)]
    for i in month_start_end:
        goodssal_mean = np.mean(goodssale_df[(goodssale_df.data_date >= i[0]) & (goodssale_df.data_date <= i[1])].goods_num)        
        goodssal_var  = np.var(goodssale_df[(goodssale_df.data_date >= i[0]) & (goodssale_df.data_date <= i[1])].goods_num)
        
        print('goods sale %d - %d, var %.2f, mean %.2f ' % (i[0], i[1], goodssal_var, goodssal_mean))
        
def goodssale_sku_week_mean():    
    print(getCurrentTime(), 'loading goodsale..') 
    goodssale_df = pd.read_csv(r'%s/goodsale.csv' % inputPath)
    goods_num_mean_dict = {}
    week_start_date = datetime.datetime.strptime('20170301', "%Y%m%d").date()
    while week_start_date <= datetime.datetime.strptime('20180316', "%Y%m%d").date():
        
        week_end_dat = week_start_date + datetime.timedelta(days=7)        
        week_start = int(week_start_date.strftime("%Y%m%d"))
        week_end = int (week_end_dat.strftime("%Y%m%d"))        
        week_start_date = week_end_dat

        goods_num_mean_dict[(week_start, week_end)] = goodssale_df[(goodssale_df.data_date >= week_start) &(goodssale_df.data_date < week_end)]['goods_num'].mean()
        
    
    week_mean = 0
    for week, each_week_mean in goods_num_mean_dict.items():
        print(week, each_week_mean)
        week_mean += each_week_mean
        
    print('week mean', week_mean / len(goods_num_mean_dict))

    

def remove_promote_time():
    def get_date(each_date, colname):
#         tmp = each_date[colname].split(' ')[0]
        return each_date[colname].replace('-', '')
    
    promote = pd.read_csv(r'%s/%s' % (inputPath, 'goods_promote_with_price.csv'))
    start_date = promote.apply(get_date, axis=1, args=('promote_start_time', ))
    end_date = promote.apply(get_date, axis=1, args=('promote_end_time', ))      
    
    promote['promote_start_time'] = start_date
    promote['promote_end_time'] = end_date
    
        
if __name__ == '__main__':
    goodssale_week_mean()
    
    
    
    