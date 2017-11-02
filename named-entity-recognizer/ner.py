# spacy 1.9
from __future__ import unicode_literals, print_function

from pathlib import Path

import random
import os
import timeit
import lxml.html

import spacy
from spacy.gold import GoldParse
from spacy.tagger import Tagger
from spacy.attrs import IS_PUNCT, LOWER

import pandas as pd
import requests
import json
import numpy as np

from elasticsearch import Elasticsearch
from elasticsearch import helpers
from helper import removeNonAscii

nlp = spacy.load('en')

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
res = requests.get('http://localhost:9200')

class entityTraining(object):
    def __init__(self, index_name, text_column):
        self.index_name = index_name
        self.text_column = text_column
        


    def termSearch(self, query, verify=True):
        res = es.search(index=self.index_name,
                        size=100, 
                        body={'query': {'match_phrase': {self.text_column: query, 
                                                    }
                                    }}
                )
        hits = res['hits']['total']
        if not verify:
            return hits
        else:
            print("Query: {}. Entries this terms shows up {} times".format(query, hits))


    def termVerify(self, terms):
        counts = []
        for term in terms:
            counts.append(self.termSearch(removeNonAscii(term), verify=False))
        verified = list(zip(terms, counts))
        return [b[0] for b in verified if b[1] >= 5]

    def textHighlights(self, query, samples = 500):
        """
        Args: search query and number of results
        Returns: clean lower cased sentences
        """
        res = es.search(index=self.index_name,
                        size=samples, 
                        body={'query': {'match_phrase': {self.text_column: query, 
                                                    }
                                    }}
                )
        res = [b['_source'][self.text_column] for b in res['hits']['hits']]
        res = [b.lstrip().lower() for b in res]
        return res

    def annotateTraining(self, sentences, term, name):
        """
        Args: clean lower cased sentences, skills, entity category
        Returns: list of annotated sentences
        """
        train = []
        for sentence in sentences:
            train.append([(int(sentence.index(term)), int(sentence.index(term) + len(term)), name)])
        return zip(sentences, train)


    def createTraining(self, sentences, terms, entity_type):
        """
        Args: sentences from create_all_corpus
        Returns: annotated sentences for use in ner training
        """
        train = []
        for b in range(len(terms)):
            print("Index: {}. {}: {}".format(b, entity_type, terms[b]))
            train.extend(self.annotateTraining(sentences[b], terms[b], entity_type))
        return train


    def createAllCorpus(self, terms, samples = 10):
        """
        Args: skills or skill_counts tuples, curated boolean
        Returns: list of sentences from search query
        """
        sentences = []
        for term in terms:
            sentences.append(self.textHighlights(term, samples=samples))
        return sentences


    def trainNer(self, nlp, train_data, model_name, iterations):
        # Add new words to vocab
        for raw_text, _ in train_data:
            doc = nlp.make_doc(raw_text)
            for word in doc:
                _ = nlp.vocab[word.orth]
        random.seed(0)
        # You may need to change the learning rate.
        nlp.entity.model.learn_rate = 0.001
        for itn in range(iterations):
            start = timeit.default_timer()
            random.shuffle(train_data)
            loss = 0.
            for raw_text, entity_offsets in train_data:
                doc = nlp.make_doc(raw_text)
                gold = GoldParse(doc, entities=entity_offsets)
                nlp.tagger(doc)
                loss += nlp.entity.update(doc, gold, drop=0.5)
            if loss == 0:
                break
            end = timeit.default_timer()-start
            print("Iteration {} complete in {} minutes".format(itn, np.round(end/60, 4)))
        nlp.end_training()
        
        if not os.path.exists('models/'+model_name):
            os.makedirs('models/'+model_name)
        nlp.save_to_directory('models/'+model_name)
        
        
    def buildNer(self, terms, samples, iterations, entity_name):
        #terms = self.termVerify(terms)
        sentences = self.createAllCorpus(terms, samples) 
        train = self.createTraining(sentences, terms, entity_name)
        start = timeit.default_timer()
        nlp.entity.add_label(entity_name)
        self.trainNer(nlp, train, self.index_name, iterations)
        end = timeit.default_timer()-start
        print("Ner training complete in {} minutes".format(end/60))
        
