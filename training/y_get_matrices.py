import json
from math import exp
import numpy as np
import pandas as pd



def get_reviews(datafile):
    user_dict = {}
    item_dict = {}
    feature_dict ={}
    aspect_index = 0

    for tupel in datafile.iterrows():
        line = tupel[0]
        user_id = datafile["user_id"][line]
        item_id = datafile["business_id"][line]
        list_len = len(datafile['absa'][line])
        if user_id not in user_dict:
            user_dict[user_id] = []
        if item_id not in item_dict:
            item_dict[item_id] = []
        for i in range(0, list_len):
            feature = datafile['absa'][line][i]['aspect']
            polarity = datafile['absa'][line][i]['polarity']
            if feature not in feature_dict:
                feature_dict[feature] = aspect_index
                aspect_index = aspect_index+1
            user_dict[user_id].append([feature, polarity])
            item_dict[item_id].append([feature, polarity])
    return [feature_dict, user_dict, item_dict]


def get_index(user_dict, product_dict):
    user_index = {}
    product_index = {}
    index = 0
    for user in user_dict.keys():
        user_index[user] = index
        index += 1
    index = 0
    for product in product_dict.keys():
        product_index[product] = index
        index += 1
    return [user_index, product_index]


def get_user_item_matrix(datafile, user_index, product_index):
    num_users = len(user_index)
    num_items = len(product_index)
    result = np.zeros((num_users, num_items))
    num_reviews = len(datafile)
    result_dense = np.zeros((num_reviews, 3))
    for line in datafile.iterrows():
        i = line[0]
        user_id = datafile['user_id'][i]
        product_id = datafile['business_id'][i]
        user = user_index[user_id]
        product = product_index[product_id]
        rating = datafile['stars'][i]
        result[user, product] = rating
        result_dense[i, 0] = user
        result_dense[i, 1] = product
        result_dense[i, 2] = rating
    return result, result_dense

def split_by_time(datafile, portion):

    datafile = datafile.sort_values(['user_id', 'date'], ascending=[True, True])
    datafile = datafile.reset_index(drop=True)
    test = datafile[datafile['user_id']=='-1']
    cnt = 0
    for i in range(1, len(datafile)):
        cnt += 1
        if datafile['user_id'][i] != datafile['user_id'][i-1] or i == (len(datafile) - 1):
            j = round(cnt*portion)
            test = test.append(datafile.iloc[(i - int(j)):i])
            cnt = 0
    datafile = datafile.drop(datafile.index[test.index])
    datafile = datafile.reset_index(drop=True)
    test = test.reset_index(drop=True)
    return test, datafile

def get_user_feature_matrix(user_dict, user_index, aspect_index, N):
    result = np.zeros((len(user_index), len(aspect_index)))
    for key in user_dict.keys():
        index_user = user_index[key]
        user_reviews = user_dict[key]
        count_dict = {}
        for review in user_reviews:
            feature = review[0]
            if feature not in aspect_index:
                continue
            aspect = aspect_index[feature]
            if aspect not in count_dict:
                count_dict[aspect] = 0;
            count_dict[aspect] += 1
        for aspect in count_dict.keys():
            count = count_dict[aspect]
            result[index_user, aspect] = 1 + (N - 1) * (2 / (1 + exp(-count)) - 1)
    return result


def get_product_feature_matrix(product_dict, product_index, aspect_index, N):
    result = np.zeros((len(product_index), len(aspect_index)))
    for key in product_dict.keys():
        index_product = product_index[key]
        product_reviews = product_dict[key]
        count_dict = {}
        for review in product_reviews:
            feature = review[0]
            polarity = review[1]
            if polarity == 'negative':
                s = -1
            elif polarity == 'positive':
                s = 1
            elif polarity == 'neutral':
                s = 0.5
            aspect = aspect_index[feature]
            if aspect not in count_dict:
                count_dict[aspect] = [];
            count_dict[aspect].append(s)
        for aspect in count_dict.keys():
            count = sum(count_dict[aspect])
            result[index_product, aspect] = 1 + (N - 1) / (1 + exp(-count))
    return result

def get_X_validation(X):
    X_valid = np.copy(X)
    mask = np.random.choice([0, 1], size=X.shape, p=[0.8, 0.2] ).astype(np.bool)
    X[mask] = -1
    X_valid[~mask] = -1
    return X, X_valid
