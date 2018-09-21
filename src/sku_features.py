'''
Created on Sep 14, 2018

@author: Heng.Zhang
'''

from global_param import *
from sklearn.preprocessing import OneHotEncoder
    
def create_sku_features(submit_sku, goods_sku_map_df, goodssale_window_df, 
                        goodsdaily_window_df, goods_promote_window_df, goodsinfo_df, 
                        feature_name_postfix):

    sku_gp = goodssale_window_df.groupby('sku_id')
    
    # sku 销量， 价格， 标签价格的均值
    sku_mean = sku_gp[['goods_num', 'goods_price', 'orginal_shop_price']].mean().reset_index()
    sku_mean.rename(columns=lambda colname: '%s_mean' % colname if colname != 'sku_id' else colname, inplace=True)
    # sku 销售价格的折扣
    sku_mean['sku_discount'] = sku_mean['goods_price_mean'] / (sku_mean['orginal_shop_price_mean'] + 0.001)
    
    # sku 销量， 价格， 标签价格的均值，  sku 销售价格的折扣
    submit_sku = pd.merge(submit_sku, sku_mean, how='left', on='sku_id')

    # goods 促销的平均价， 促销的平均折扣
    promote_gp = goods_promote_window_df.groupby('goods_id')
    goods_promote_mean = promote_gp[['promote_price', 'shop_price']].mean().reset_index()
    goods_promote_mean.rename(columns={'promote_price':'promote_price_mean'}, inplace=True)
    goods_promote_mean['promote_discount_mean'] = goods_promote_mean['promote_price_mean'] / (goods_promote_mean['shop_price'] + 0.001)
    del goods_promote_mean['shop_price']

    # sku, goods 的销量, sku 销量 占 goods 销量的比例
    sku_sale_num = goodssale_window_df.groupby(['goods_id', 'sku_id'])['goods_num'].sum().reset_index()
    sku_sale_num.rename(columns={'goods_num':'sku_num'}, inplace=True)    
    goods_sale_num = sku_sale_num.groupby('goods_id')['sku_num'].sum().reset_index()
    goods_sale_num.rename(columns={'sku_num':'goods_num'}, inplace=True)        
    sku_sale_num = pd.merge(sku_sale_num, goods_sale_num, how='left', on=['goods_id'])
    sku_sale_num['sku_sale_percent_in_goods'] = sku_sale_num['sku_num'] / sku_sale_num['goods_num']
    
    sku_sale_num = pd.merge(sku_sale_num, goods_promote_mean, how='left', on=['goods_id'])
    sku_sale_num.fillna(0, inplace=True)
    
    del goodsdaily_window_df['data_date']
    click_gp = goodsdaily_window_df.groupby('goods_id')
    click_total = click_gp[['goods_click', 'cart_click', 'favorites_click', 'sales_uv']].sum().reset_index()    
    click_total['total_click']              = click_total['goods_click'] + click_total['cart_click'] + click_total['favorites_click']
    click_total['goods_click_percent']      = click_total['goods_click'] / click_total['total_click']
    click_total['goods_cart_click_percent'] = click_total['cart_click'] / click_total['total_click']
    click_total['goods_fav_click_percent']  = click_total['favorites_click'] / click_total['total_click']

#     # 每人购买 goods 后的平均点击次数
    click_total['goods_click_per_uv']      = click_total['goods_click'] / click_total['sales_uv']
    click_total['goods_cart_click_per_uv'] = click_total['cart_click'] / click_total['sales_uv']
    click_total['goods_fav_click_per_uv']  = click_total['favorites_click'] / click_total['sales_uv']
    
    # 平均每人的购买数量
    sku_sale_num = pd.merge(sku_sale_num, click_total, how='left', on='goods_id')
    sku_sale_num['goods_num_per_uv'] = sku_sale_num['goods_num'] / sku_sale_num['sales_uv']
    sku_sale_num.fillna(0, inplace=True)
    
    submit_sku = pd.merge(submit_sku, sku_sale_num, how='left', on='sku_id')

    oht = OneHotEncoder()
    oht.fit(np.array([0,1,2,3,4]).reshape(-1, 1))
    season_oht = pd.DataFrame(oht.transform(goodsinfo_df['goods_season'].values.reshape(-1, 1)).toarray())
    season_oht.rename(columns={0:'season_0', 1:'season_1', 2:'season_2', 3:'season_3', 4:'season_4'}, inplace=True)
    tmp = pd.concat([goodsinfo_df['goods_id'], season_oht], axis=1)
    submit_sku = pd.merge(submit_sku, tmp, how='left', on='goods_id')
    submit_sku.fillna(0, inplace=True)

    del submit_sku['goods_id']
    del submit_sku['sku_id']
    submit_sku.rename(columns=lambda colname: '%s_%s' % (colname, feature_name_postfix), inplace=True)
    
    for colname in submit_sku.columns:
        tmp_inf = np.isinf(submit_sku[colname])
        submit_sku.loc[tmp_inf, colname] = 0
        
    return submit_sku
