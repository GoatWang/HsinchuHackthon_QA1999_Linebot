from django.conf import settings

import jieba
import os

from pymongo import MongoClient
import pandas as pd
import requests
import xgboost
import xgboost as xgb
import json
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity



class Classifier():

    def __init__(self, test_sentence):
        if __name__ == "__main__":
            ModelsDir = 'models'
        else:
            ModelsDir = os.path.join('society', 'models')


        jieba.set_dictionary(os.path.join(ModelsDir, 'dict.txt.big'))
        with open(os.path.join(ModelsDir, 'cat_mapping'), 'r' , encoding='utf8') as f:
            self.cat_mapping = json.load(f)
        # with open(os.path.join(ModelsDir, 'vectorterms'), 'r' , encoding='utf8') as f:
        with open(os.path.join(ModelsDir, 'vectorterms_nonword2vec'), 'r' , encoding='utf8') as f: ##api can't be connected
            self.vectorterms = json.load(f)
        with open(os.path.join(ModelsDir, 'contactinfo.json'), 'r', encoding='utf8') as f:
            self.cat_contact_mapping = json.load(f)
        with open(os.path.join(ModelsDir, 'ProcessedData.json'), 'r', encoding='utf8') as f:
            self.data = json.load(f)
            self.df = pd.DataFrame(self.data)

        self.test_sentence = test_sentence
        self.test_vec = self.to_vec(test_sentence)

        self.bst = xgb.Booster({'nthread': 4})  # init model
        # self.bst.load_model(os.path.join(ModelsDir, '20171125 232430246178.model'))  # load data ##api can't be connected
        self.bst.load_model(os.path.join(ModelsDir, '20171127 125648530042.model'))  # load data


    def getcat_mapping(self):
        return self.cat_mapping

    def getvectorterms(self):
        return self.vectorterms

    def to_vec(self, test_sentence):
        words = list(jieba.cut(test_sentence, cut_all=False))
        
        self_main_list = [0] * len(self.vectorterms)
        for term in words:
            if term in self.vectorterms:
                idx = self.vectorterms.index(term)
                self_main_list[idx] += 1
        return self_main_list

    def predict_cat(self):
        self_main_list = self.to_vec(self.test_sentence)
        vector = self_main_list
        cat_num = self.bst.predict(xgboost.DMatrix(np.array([vector,])))[0]

        cat = None
        for key, value in self.cat_mapping.items():
            if str(int(cat_num)) == str(value):
                cat = key
        return cat

    def findsimilar(self):
        df = self.df
        test_vector = self.to_vec(self.test_sentence)

        similar_scores = []
        for num, question in enumerate(df['question']):
            vector = self.to_vec(question)
            score = cosine_similarity([np.array(vector), np.array(test_vector)])[0][1]
            similar_scores.append((num, score))

        sorted_scores = sorted(similar_scores, key=lambda x: x[1], reverse=True)
        relatedquery_idxs =  [idx[0] for idx in sorted_scores][:3]

        return df.loc[relatedquery_idxs]

    def getcontactinfo(self, cat):
        contactInfo = self.cat_contact_mapping.get(cat)
        return contactInfo

    def getfeedbackinfo(self, cat, relatedrows):
        contactInfo = self.getcontactinfo(cat)

        feedbackstring = "您是否要請教以下問題?\n"
        # feedbackstring = ""
        count = 0
        for n, row in relatedrows.iterrows():
            feedbackstring += str(count) + ". " + row['question'].replace('\n', '') + "\n"
            # feedbackstring += row['ans'] + "\n"
            count += 1
        # feedbackstring += "若沒有回答道您的問題，請參考以下聯絡方式: \n"
        # feedbackstring += contactInfo

        return feedbackstring























if __name__ == "__main__":
    clf = Classifier("兒童")
    cat = clf.predict_cat()
    print(cat)
    # def getall(col_name):
    #     conn = MongoClient()
    #     db = conn.QA1999
    #     collection = db[col_name]
    #     cursor = collection.find({})
    #     rows = [row for row in cursor]
    #     df = pd.DataFrame(rows)
    #     return df

    # df_test= getall('taipei')[:100]
    # idxs = np.random.choice(df_test.index, size=5)
    # test_sentences = df_test.loc[idxs, 'question']

    # for sen in test_sentences:
    #     cat = clf.predict_cat(sen)
    #     print(sen)
    #     print(cat)
    #     print("======")
