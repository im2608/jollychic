'''
Created on Sep 17, 2018

@author: Heng.Zhang
'''
import datetime
import math

from global_param import *
from sku_features import *
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler, Normalizer



def get_sku_sale_num_in_week(week_end, goodssale_df, sku_df):
    end_date = datetime.datetime.strptime(week_end, "%Y%m%d").date()
    start_date = end_date + datetime.timedelta(days =-7)
    goodsale_window_df = goodssale_df[(goodssale_df.data_date >= int(start_date.strftime("%Y%m%d")))&\
                                      (goodssale_df.data_date < int(end_date.strftime("%Y%m%d")))][['sku_id', 'goods_num']]
    goodsale_window_df = goodsale_window_df.groupby('sku_id')['goods_num'].sum().reset_index()

    goodsale_window_df = pd.merge(sku_df, goodsale_window_df, how='left', on='sku_id')     
    goodsale_window_df.fillna(0, inplace=True)                         

    return goodsale_window_df[['sku_id', 'goods_num']]

def get_sku_sale_mean_std(goodssale_df):
    sku_mean_std = pd.DataFrame()
    sku_gp = goodssale_df.groupby('sku_id')
    sku_mean_std['sku_mean'] = sku_gp['goods_num'].mean()    
    sku_mean_std['sku_std'] = sku_gp['goods_num'].std()
    
    sku_mean_std = sku_mean_std.reset_index()
    sku_mean_std.fillna(0, inplace=True)
    
    return sku_mean_std
    
def goodssale_sku_sale_week_mean_std(goodssale_df, submit_sku):    
    sku_mean_std = submit_sku[['sku_id']]

    goods_num_mean_dict = {}
    week_start_date = datetime.datetime.strptime('20170301', "%Y%m%d").date()
    while week_start_date <= datetime.datetime.strptime('20180316', "%Y%m%d").date():
        
        week_end_dat = week_start_date + datetime.timedelta(days=7)        
        week_start = int(week_start_date.strftime("%Y%m%d"))
        week_end = int (week_end_dat.strftime("%Y%m%d"))        
        week_start_date = week_end_dat
        
        sku_week_mean_std = pd.DataFrame()
        
        goodssale_week_df = goodssale_df[(goodssale_df.data_date >= week_start) &(goodssale_df.data_date < week_end)]
        sku_gp = goodssale_week_df.groupby('sku_id')
        sku_week_mean_std['sku_mean_%d_%d' % (week_start, week_end)] = sku_gp['goods_num'].mean()    
        sku_week_mean_std['sku_std_%d_%d' % (week_start, week_end)] = sku_gp['goods_num'].std()
        sku_week_mean_std = sku_week_mean_std.reset_index()
        
        sku_mean_std = pd.merge(sku_mean_std, sku_week_mean_std, how='left', on='sku_id')
        
    sku_mean_std.fillna(0, inplace=True)
    sku_id = sku_mean_std['sku_id']
    del sku_mean_std['sku_id']
    
    tmp_mean = sku_mean_std.mean(axis=1)
    tmp_std = sku_mean_std.std(axis=1)

    sku_mean_std['sku_id'] = sku_id
    sku_mean_std['sku_week_mean'] = tmp_mean
    sku_mean_std['sku_week_std'] = tmp_std
    
    return sku_mean_std
        
    

        
# def sku_features(submit_sku, goods_sku_map_df, goodssale_window_df, goodsdaily_window_df, goods_promote_window_df, goodsinfo_df):
    
def generate_slide_window_feature(fcst_date, goodsdaily_df, goodssale_df, goods_promote_df, goodsinfo_df, submit_sku, goods_sku_map_df):    
#     feature_end_date = datetime.datetime.strptime(fcst_date, "%Y%m%d") - datetime.timedelta(days=7)
    feature_end_date = datetime.datetime.strptime(fcst_date, "%Y%m%d")
    feature_end = int(feature_end_date.strftime("%Y%m%d"))
    sku_features = None
    for feature_windows_size in [5,6,7,8]:
        feature_start_date = feature_end_date - datetime.timedelta(days= feature_windows_size * 7) 
        feature_start = int(feature_start_date.strftime("%Y%m%d")) 
        goodsdaily_window_df = goodsdaily_df[(goodsdaily_df.data_date >= feature_start) &(goodsdaily_df.data_date < feature_end)]
        goodssale_window_df =  goodssale_df[(goodssale_df.data_date >= feature_start) &(goodssale_df.data_date < feature_end)]
        goodspromote_window_df = goods_promote_df[(goods_promote_df.promote_start_time >= feature_start) &
                                                  (goods_promote_df.promote_end_time < feature_end)]

        sku_window_features = create_sku_features(submit_sku, goods_sku_map_df, 
                                                  goodssale_window_df, goodsdaily_window_df, 
                                                  goodspromote_window_df, goodsinfo_df, 'window_size_%d' % feature_windows_size)
        if (sku_features is None):
            sku_features = sku_window_features
        else:
            sku_features = pd.concat([sku_features, sku_window_features], axis=1)

    return sku_features
    

def main():    
    algo_start_date = '20180101'
    days_after_training = 45
    
    verify_week = '20180223'
    predict_week = '20180216'
    
    training_week_date = datetime.datetime.strptime(algo_start_date, "%Y%m%d")
    verify_week_date = datetime.datetime.strptime(verify_week, "%Y%m%d")
    predict_week_date = datetime.datetime.strptime(predict_week, "%Y%m%d")
    
    fcsting_weeks_cnt = 5
    
    train_weeks_dict = {}
    verify_weeks_dict = {}
    predict_weeks_dict = {}
    submiting_week_dict = {}
    
    
    for i in range(1, fcsting_weeks_cnt + 1):        
        label_week_date = training_week_date + datetime.timedelta(days=days_after_training) 
        train_weeks_dict[training_week_date.strftime("%Y%m%d")] = label_week_date.strftime("%Y%m%d")
        
        verify_label_week_date = verify_week_date + datetime.timedelta(days=days_after_training)
        verify_weeks_dict[verify_week_date.strftime("%Y%m%d")] = verify_label_week_date.strftime("%Y%m%d")
        
        predict_weeks_dict[training_week_date.strftime("%Y%m%d")] = predict_week_date.strftime("%Y%m%d")
        submiting_week_dict[predict_week_date.strftime("%Y%m%d")] = 'week%d' % i

        training_week_date += datetime.timedelta(days=7)
        verify_week_date += datetime.timedelta(days=7)
        predict_week_date += datetime.timedelta(days=7) 
    

    print(getCurrentTime(), 'loading submit_example..')
    submit_sku = pd.read_csv(r'%s/submit_example.csv' % inputPath)
    submit_sku = submit_sku[['sku_id']]
    
    print(getCurrentTime(), 'loading goods_sku_relation..') 
    goods_sku_map_df = pd.read_csv(r'%s/goods_sku_relation.csv' % inputPath)
    
    print(getCurrentTime(), 'loading goodsale..') 
    goodssale_df = pd.read_csv(r'%s/goodsale.csv' % inputPath)
    
    print(getCurrentTime(), 'loading goodsdaily..')
    goodsdaily_df = pd.read_csv(r'%s/goodsdaily.csv' % inputPath)
    
    print(getCurrentTime(), 'loading goods_promote..')
    goods_promote_df = pd.read_csv(r'%s/goods_promote.csv' % inputPath)
    
    print(getCurrentTime(), 'loading goodsinfo..')
    goodsinfo_df = pd.read_csv(r'%s/goodsinfo.csv' % inputPath)

    # 训练模型
    week_models_dict = {}
    for training_week, label_week in train_weeks_dict.items():
        print(getCurrentTime(), 'traing with week %s, label week %s' % (training_week, label_week))
        training_features = generate_slide_window_feature(training_week, goodsdaily_df, goodssale_df, goods_promote_df, 
                                                          goodsinfo_df, submit_sku, goods_sku_map_df)
        normalizer = Normalizer()
        training_features = normalizer.fit_transform(training_features)

        sku_sale_num = get_sku_sale_num_in_week(training_week, goodssale_df, submit_sku)

        LR = LinearRegression()
        LR.fit(training_features, sku_sale_num['goods_num'])

        week_models_dict[training_week] = (LR, normalizer)

    verify_mse = 0   
    # 校验
    for verify_week, verify_label_week in verify_weeks_dict.items():
        print(getCurrentTime(), 'verify week %s, verify label week %s' % (verify_week, verify_label_week))
        sku_verify_window_features = generate_slide_window_feature(verify_week, goodsdaily_df, goodssale_df, goods_promote_df, 
                                                                   goodsinfo_df, submit_sku, goods_sku_map_df)
        LR = week_models_dict[training_week][0]
        normalizer = week_models_dict[training_week][1]
        sku_verify_window_features =normalizer.transform(sku_verify_window_features)

        verify_sale_num = get_sku_sale_num_in_week(verify_week, goodssale_df, submit_sku)

        predicted_verify_week =  pd.DataFrame(LR.predict(sku_verify_window_features), columns=['fcst_num'])
        predicted_verify_week.loc[predicted_verify_week['fcst_num'] < 0, 'fcst_num'] = 0

        verify_mse += mean_squared_error(verify_sale_num['goods_num'], predicted_verify_week['fcst_num'])
        
    print(getCurrentTime(), 'verify_mse %f' % verify_mse)
    
    submition = pd.DataFrame(submit_sku['sku_id'])
    predict_weeks_dict = {'20180216':'week1', 
                          '20180223':'week2',
                          '20180302':'week3',
                          '20180309':'week4',
                          '20180316':'week5',}
    # 预测
    for training_week, predict_feature_week in predict_weeks_dict.items():
        submiting_week_num = submiting_week_dict[predict_feature_week]
        print(getCurrentTime(), 'predicting %s with %s using model trained with %s' % 
              (submiting_week_num, predict_feature_week, training_week))
        sku_fcst_window_features = generate_slide_window_feature(predict_feature_week, goodsdaily_df, goodssale_df, goods_promote_df, 
                                                                 goodsinfo_df, submit_sku, goods_sku_map_df)
        LR = week_models_dict[training_week][0]
        normalizer = week_models_dict[training_week][1]
        sku_fcst_window_features = normalizer.transform(sku_fcst_window_features)

        submition[submiting_week_num] = LR.predict(LR.predict(sku_verify_window_features))
        submition.loc[submition[submiting_week_num] < 0, submiting_week_num] = 0
        
    # 对输出 week 排序
    submition = submition[['sku_id', 'week1', 'week2', 'week3', 'week4', 'week5']]

    output_filename = 'submit_%s.csv' % (datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    print(getCurrentTime(), 'output file to %s' % output_filename)
    submition.to_csv('%s/%s' % (outputPath, output_filename), index=False)
    
    veriy_submition_file(output_filename)
    
    return

def verify_submition_df(submition_df):
    pass

def veriy_submition_file(subfie_filename):
    print(getCurrentTime(), 'verifying %s' % (subfie_filename))    
    training_week_date = datetime.datetime.strptime(algo_start_date, "%Y%m%d")
    fcsting_weeks_cnt = 5
    
    fcsting_weeks = []
    week_submit_colname_dict = {}
    
    for i in range(1, fcsting_weeks_cnt + 1):        
        fcsting_week_date = training_week_date + datetime.timedelta(days=days_after_training) 
        fcsting_weeks.append(fcsting_week_date.strftime("%Y%m%d"))
        week_submit_colname_dict[fcsting_week_date.strftime("%Y%m%d")] = 'week%d' % i
         
        training_week_date += datetime.timedelta(days=7)

    print(getCurrentTime(), 'veriy_submit() loading goodsale..') 
    goodssale_df = pd.read_csv(r'%s/goodsale.csv' % inputPath)

    print(getCurrentTime(), 'veriy_submit() loading submit_example..')
    submit_sku = pd.read_csv(r'%s/submit_example.csv' % inputPath)
    submit_sku = submit_sku[['sku_id']]

    sku_sale_mean_std = goodssale_sku_sale_week_mean_std(goodssale_df, submit_sku)

    submition = pd.read_csv(r'%s/%s' % (outputPath, subfie_filename))

    submition = pd.merge(submition, sku_sale_mean_std, how='left', on='sku_id')

    week_mse_no_mean = 0
    weeks = ['week1', 'week2', 'week3', 'week4', 'week5']
    
    for fcsting_week in fcsting_weeks:
        sku_sale_num = get_sku_sale_num_in_week(fcsting_week, goodssale_df, submit_sku)
        mse = mean_squared_error(sku_sale_num['goods_num'], submition[week_submit_colname_dict[fcsting_week]])
        week_mse_no_mean += mse

    week_mse_mean = 0
    for week in weeks: 
        submition.loc[submition[week] > submition['sku_week_mean'] + 2 * submition['sku_week_std'], week] = submition['sku_week_mean'] + 2 * submition['sku_week_std']
        mse = mean_squared_error(sku_sale_num['goods_num'], submition[week])
        week_mse_mean += mse

#     week_mse_mean /= submition.shape[0]

#     print(getCurrentTime(), 'without range to mean %f, with range to mean %f' % (math.sqrt(week_mse_no_mean), math.sqrt(week_mse_mean)))
    print(getCurrentTime(), 'without range to mean %f, with range to mean %f' % (week_mse_no_mean, week_mse_mean))
    
    colnames = ['sku_id']
    colnames.extend(weeks)    
    submition[colnames].to_csv('%s/submit_%s.csv' % (outputPath, datetime.datetime.now().strftime('%Y%m%d_%H%M%S')), index=False)
    
       

    
if __name__ == '__main__':
    main()
#     veriy_submit('submit_20180921_161430.csv')
