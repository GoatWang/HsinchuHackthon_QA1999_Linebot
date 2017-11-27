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
        with open(os.path.join(ModelsDir, 'vectorterms'), 'r' , encoding='utf8') as f:
            self.vectorterms = json.load(f)
        with open(os.path.join(ModelsDir, 'contactinfo.json'), 'r', encoding='utf8') as f:
            self.cat_contact_mapping = json.load(f)
        with open(os.path.join(ModelsDir, 'questions.json'), 'r', encoding='utf8') as f:
            self.data = json.load(f)
            self.df = pd.DataFrame(self.data)

        self.test_sentence = test_sentence
        self.test_vec = self.to_vec(test_sentence)

        self.bst = xgb.Booster({'nthread': 4})  # init model
        self.bst.load_model(os.path.join(ModelsDir, '20171125 232430246178.model'))  # load data


    def getcat_mapping(self):
        return self.cat_mapping

    def getvectorterms(self):
        return self.vectorterms

    def to_vec(self, test_sentence):
        # print(test_sentence)
        words = list(jieba.cut(test_sentence, cut_all=False))
        # print(", ".join(words))
        
        allrelated = []
        for keyword in words:
            url = 'http://140.120.13.244:10000/kem/?keyword='+ keyword +'&lang=cht'
            res = requests.get(url)
            related = [term[0] for term in eval(res.text) if term[1] > 0.65]
            allrelated.extend(related)
        words.extend(allrelated)
        # print(", ".join(words))
            
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
        # print(cat_num)

        cat = None
        for key, value in self.cat_mapping.items():
            if str(int(cat_num)) == str(value):
                cat = key
        # print(cat)
        return cat

    def findsimilar(self):
        df = self.df
        test_vector = self.to_vec(self.test_sentence)

        similar_scores = []
        for num, vector in enumerate(df['vector']):
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
        for n, row in relatedrows.iterrows():
            feedbackstring += str(n + 1) + '. ' + row['question'] + "\n"
            feedbackstring += row['ans'] + "\n"
        
        feedbackstring += "若沒有回答道您的問題，請參考以下聯絡方式: \n"
        feedbackstring += contactInfo

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
