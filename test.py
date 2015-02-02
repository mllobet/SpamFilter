#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re
import json
import tldextract
import random

import regex
from scipy.sparse import csr_matrix

import stemmer
from sklearn import naive_bayes

FNAME = "posts.json"

s = stemmer.SpanishStemmer()

commonWords = [
    'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'se', 'del', 'las', 'un',
    'por', 'con', 'no', 'una', 'su', 'para', 'es', 'al', 'lo', 'como', 'mas',
    'o', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya',
    'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'tambien', 'fue',
    'habia', 'era', 'muy', 'anos', 'hasta', 'desde', 'esta', 'mi', 'porque',
    'que', 'solo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'asi', 'nos',
    'ni', 'parte', 'tiene', 'el', 'uno', 'donde', 'bien', 'tiempo', 'mismo',
    'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'despues', 'te', 'otros',
    'aunque', 'esa', 'eso', 'hace', 'otra', 'gobierno', 'tan', 'durante',
    'siempre', 'dia', 'tanto', 'ella', 'tres', 'si', 'dijo', 'sido', 'gran',
    'pais', 'segun', 'de', 'la', 'i', 'el', 'a', 'l', 'en', 'va', 'de', 'que',
    'del', 'un', 'les', 'amb', 'per', 'una', 'els', 'es', 'al', 'es', 'dels',
    'ser', 'van', 'o', 'com', 'mes', 'no', 's', 'seva', 'fou', 'entre', 'pero',
    'seu', 'com', 'per', 'tambe', 'son', 'als', 'on', 'aquest', 'anys',
    'ciutat', 'era', 'pel', 'despres', 'va', 'aquesta', 'part', 'gran', 'ha',
    'durant', 'sobre', 'any', 'nom', 'estat', 'altres', 'havia', 'dos', 'rei',
    'molt', 'primer', 'quan', 'fer', 'li', 'contra', 'pels', 'cap', 'els seus',
    'seves', 'pot', 'temps', 'mateix', 'hi', 'tres', 'forma', 'esta',
    'guerra', 'te', 'despres', 'fins', 'fill',

    'http', 'facebook', 'google', 'com', 'org', 'net', 'cat', 'es', 'www',

    'k', 'xd', 'q', 'xq'
];

ACCENTS = ((u'à', u'a'), (u'á', u'a'), (u'è', u'e'), (u'é', u'e'), (u'ì', u'i'),
           (u'í', u'i'), (u'ò', u'o'), (u'ó', u'o'),
           (u'ù', u'u'), (u'ú', u'u'), (u'ñ', 'n'),
           (u'ä', 'a'), (u'ë', 'e'), (u'ï', 'i'), (u'ö', 'o'), (u'ü', 'u'), )

PREFIXES = [
    "m'",
    "s'",
    "t'",
    "l'",
    "d'",
    "'"
]
SUFFIXES = [
    "'s",
    "'"
]

def cleanWord(word):
    if word[:6] == u"__url_":
        return word

    # Lowercase
    word = word .lower()

    # Remove accents
    for c_old, c_new in ACCENTS:
        word = word.replace(c_old,c_new)

    # Remove common prefixes
    for p in PREFIXES:
        if word[:len(p)] == p:
            word = word[len(p):]

    # Remove common suffixes
    for p in SUFFIXES:
        if word[-len(p):] == p:
            word = word[:-len(p)]

    if word in commonWords:
        return None
    if len(word) <= 3:
        return None

    word = s.stem(word)
    return word


def repl(m):
    url = m.group(0)
    domain = tldextract.extract(url).domain
    return u"__url_" + domain

def tokenize(message):
    message = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', repl, message)

    tokens = re.findall(r"[\w']+", message)
    for t in tokens:
        t = cleanWord(t)
        if t is None:
            continue
        yield t

def run():
    with open(FNAME) as f:
        posts = json.load(f)

    for post in posts:
        data = post['text'][1:].decode('hex')
        data = data.decode('utf-8')
        print list(tokenize(data))

num_features = 0
features = {}

def generate_map(posts):
    global num_features
    global features

    data = []
    row_ind = []
    col_ind = []

    postid = 0
    labels = []
    for post in posts:
        labels.append(int(post['state']))
        text = post["text"]

        postfeatures = {}
        for token in tokenize(text):
            if token not in features:
                features[token] = num_features
                num_features += 1
            featureid = features[token]
            if featureid not in postfeatures:
                postfeatures[featureid] = 1
            else:
                postfeatures[featureid] += 1

        for (id, count) in postfeatures.items():
            data.append(count)
            row_ind.append(postid)
            col_ind.append(id)

        postid += 1

    return (csr_matrix((data, (row_ind, col_ind)), shape=(postid, num_features)), labels)

def get_feature_vector(text):
    global features
    global num_features

    vector = [0]*num_features
    for token in tokenize(text):
        if token not in features:
            continue
        vector[features[token]] += 1

    return vector

if __name__=="__main__":
    with open(FNAME) as f:
        #Load crap
        print "Loading crap..."
        posts = json.load(f)
        for post in posts:
            post["text"] = post['text'][1:].decode('hex').decode('utf-8')

        print "Shuffling crap..."
        random.shuffle(posts)

        print "Processing crap..."
        (X, y) = generate_map(posts[:16000])

        for f in features:
            print f

        print "num_features = ", num_features

        print "Training using crap..."
        clf = naive_bayes.MultinomialNB()
        clf.fit(X, y)

        print "Predicting crap..."
        correct = 0
        v11 = 0
        v12 = 0
        v21 = 0
        v22 = 0
        for post in posts[16000:]:
            pred = clf.predict(get_feature_vector(post['text']))[0]
            v = int(post['state'])
#            print "---"
#            print pred
#            print v
            if pred == 1 and v == 1:
                v11 += 1
            if pred == 1 and v == 2:
                v12 += 1
            if pred == 2 and v == 1:
                v21 += 1
            if pred == 2 and v == 2:
                v22 += 1

            if pred == v:
                correct += 1

        print "OPness: "
        print correct
        print float(correct)/(len(posts) - 16000)

        print "1,1: ", v11
        print "1,2: ", v12
        print "2,1: ", v21
        print "2,2: ", v22
