import nltk
from nltk import word_tokenize
from nltk.util import ngrams
from collections import OrderedDict

import spacy

class entValidator(object):
    def __init__(self, entity_type, terms, nlp):
        self.entity_type = entity_type
        self.terms = terms
        self.nlp = nlp

    def getEnt(self, document):
        document = self.nlp(unicode(document))
        return [word.text for word in document if word.ent_type_ == self.entity_type]

    def create_ngrams(self, text):
        """
        Args: text
        Returns: list of bigrams and trigrams
        """
        token=nltk.word_tokenize(text)
        trigrams = [' '.join(b) for b in ngrams(token,3)]
        bigrams = [' '.join(b) for b in ngrams(token,2)]
        return trigrams + bigrams

    def termValidator(self, document):
        keywords = self.getEnt(document)
        return [b for b in keywords if b in self.terms]

    def phraseValidator(self, document):
        ngrams = [b for b in self.create_ngrams(' '.join(self.getEnt(document))) if b in self.terms]
        return ngrams

    def validate_keywords(self, document):
        """
        Args: original text data, spaCy nlp, trained ner model
        Returns: returns list of entities and ngram entities validated against skills list
        """
        validated = []
        validated.append(self.termValidator(document))
        return [list(OrderedDict.fromkeys(b)) for b in validated][0]

    def validate_phrases(self, document):
        """
        Args: original text data, spaCy nlp, trained ner model
        Returns: returns list of entities and ngram entities validated against skills list
        """
        validated = []
        validated.append(self.phraseValidator(document))
        return [list(OrderedDict.fromkeys(b)) for b in validated][0]

    def removeNonKeywords(self, keywords, phrases):
        notlist = []
        filtered = []
        last = []
        notlist.append(' '.join(set(self.create_ngrams(' '.join(keywords))).intersection(set(phrases))).split())
        filtered.append(list(set(keywords).difference(set(notlist[0]))))
        last.append(list(set(filtered[0]).union(set(phrases))))
        return last[0]

    def extractTerms(self, document):
        keywords = self.validate_keywords(document)
        phrases = self.validate_phrases(document)
        return self.removeNonKeywords(keywords, phrases)

    def termDictionary(self):
        """
        For demo purposes only
        """
        before = """\n<mark class="entity" style="background: rgba(166, 226, 45, 0.2); border-color: rgb(166, 226, 45); border: 1px solid; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em; box-decoration-break: clone; -webkit-box-decoration-break: clone">\n"""    
        after = """\n    <span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; text-transform: uppercase; vertical-align: middle; margin-left: 0.5rem">{}</span>\n</mark>\n""".format(self.entity_type)
        term_dict = {}
        for term in self.terms:
            term_dict[term] = before+term+after
        return term_dict

    def replaceAll(self, text, dic):
        header = """<div class="entities" style="line-height: 2.5">"""
        for i, j in dic.iteritems():
            text = text.replace(i, j)
        return header+text

    def displayTerms(self, text):
        extracted_terms = self.extractTerms(text)
        dictionary = self.termDictionary()
        return self.replaceAll(text.lower(), dictionary)