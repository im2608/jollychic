'''
Created on Sep 13, 2018

@author: Heng.Zhang
'''

from global_param import *
import pandas as pd
import numpy as np


def withday_week_sale(goodssale, submit_sku, week_start, week_end):
    week_sale = goodssale[(goodssale.data_date >= week_start)&(goodssale.data_date < week_end)].groupby('sku_id')['goods_num'].sum()
    week_sale = week_sale.reset_index()
    week_sale = pd.merge(submit_sku, week_sale, how='left', on=['sku_id'])
    return week_sale

def sametime_lastyear():
    goodssale = pd.read_csv(r'%s/goodsale_corrected.csv' % inputPath)
    submit_sku = pd.read_csv(r'%s/submit_example.csv' % inputPath)
    
    submit_sku = pd.DataFrame(submit_sku.sku_id)
    
    week_sale = withday_week_sale(goodssale, submit_sku, 20170501, 20170508)
    submit_sku['week1'] = week_sale.goods_num
    
    week_sale = withday_week_sale(goodssale, submit_sku, 20170508, 20170515)
    submit_sku['week2'] = week_sale.goods_num

    week_sale = withday_week_sale(goodssale, submit_sku, 20170515, 20170522)
    submit_sku['week3'] = week_sale.goods_num

    week_sale = withday_week_sale(goodssale, submit_sku, 20170522, 20170529)
    submit_sku['week4'] = week_sale.goods_num
    
    week_sale = withday_week_sale(goodssale, submit_sku, 20170529, 20170605)
    submit_sku['week5'] = week_sale.goods_num
    
    submit_sku.fillna(0, inplace=True)
    submit_sku.to_csv(r'%s/submit.csv' % outputPath, index=False)
    return


def smooth_avg():
    goodssale = pd.read_csv(r'%s/in_submiting/goodsale_corrected.csv' % inputPath)


if (__name__ == '__main__'):
    sametime_lastyear()