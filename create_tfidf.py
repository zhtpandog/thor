import math
import numpy as np
import jsonlines
import json

class tfidf2:
  def __init__(self):
    self.documents = {} # {doc:{word:tfidf}} after call prep(), contains each doc name and its doc dict, the doc dict is {word:tfidf}
    self.corpus_dict = {} # {word:df}, contains all the words, and document frequency (df)
    self.idf = {} # idf
    self.num_docs = 0 # number of documents
    self.prepStatus = False

  def addDocument(self, doc_name, list_of_words):
    '''
    Add document one by one
    :param doc_name: document name, or uuid
    :param list_of_words: word list correspond to the doc name
    :return: void
    '''
    ## compute tf (doc dict is the dict of the single doc)
    doc_dict = {}
    for w in list_of_words:
      doc_dict[w] = doc_dict.get(w, 0.0) + 1.0 # if the word w exists, plus 1 to its value; if not exists, make its value 1

    # normalizing the doc dict (creating tf score)
    length = float(len(list_of_words))
    for k in doc_dict:
      doc_dict[k] = doc_dict[k] / length

    # add the normalized document and its tf score to the corpus
    self.documents[doc_name] = doc_dict
    ## finish the work on tf

    # make change to the global df
    for w in set(list_of_words):
      self.corpus_dict[w] = self.corpus_dict.get(w, 0.0) + 1.0 # count each word's to the whole corpus contribution only once

  def prep(self):
    '''
    Prepare the tfidf value for each doc in corpus.
    :return: void
    '''
    # creating idf dict
    self.num_docs = len(self.documents)
    for i, j in self.corpus_dict.items():
      self.idf[i] = math.log(self.num_docs / self.corpus_dict[i])

    # computing tfidf for each document
    for doc in self.documents:
      for i in self.documents[doc]: # i is word
        self.documents[doc][i] *= self.idf[i]
    self.prepStatus = True

  def similarities_by_name(self, queryName):
    '''
    Calculates cosine tfidf similarities w.r.t each doc in the corpus. Query by name existed. Returns a dict {docname:similarity_score} pairs.
    :param queryName: query uuid
    :return: sims: query word list's tfidf similarity to all documents in the corpus
    '''

    if self.prepStatus == False:
      print "Not Prepared, pls call prep() first"
      return

    query_dict = self.documents[queryName]

    # computing similarities
    sims = {}
    for doc in self.documents:
      score = 0.0
      doc_dict = self.documents[doc]

      for k in query_dict: # k is each word in query dict
        if k in doc_dict:
          score += query_dict[k] * doc_dict[k]
      score /= np.linalg.norm(np.array(query_dict.values())) * np.linalg.norm(np.array(doc_dict.values()))

      sims[doc] = score

    return sims

  def similarities_by_wordlist(self, list_of_words):
    '''
    Calculates cosine tfidf similarities w.r.t each doc in the corpus. Query by new list of words. Returns a dict {docname:similarity_score} pairs.
    :param list_of_words: a list of words
    :return: sims: query word list's tfidf similarity to all documents in the corpus
    '''

    if self.prepStatus == False:
      print "Not Prepared, pls call prep() first"
      return

    query_dict = {}
    for w in list_of_words:
      query_dict[w] = query_dict.get(w, 0.0) + 1.0  # if the word w exists, plus 1 to its value; if not exists, make its value 1

    # calculate tfidf
    # assume all the query words exist in idf !!!IMPORTANT!!!
    length = float(len(list_of_words))
    for k in query_dict:
      query_dict[k] = (query_dict[k] / length) * self.idf[k]

    # computing similarities
    sims = {}
    for doc in self.documents:
      score = 0.0
      doc_dict = self.documents[doc]

      for k in query_dict:  # k is each word in query dict
        if k in doc_dict:
          score += query_dict[k] * doc_dict[k]
      score /= np.linalg.norm(np.array(query_dict.values())) * np.linalg.norm(np.array(doc_dict.values()))

      sims[doc] = score

    return sims

from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
class MTokenizer(object):

    @staticmethod
    def tokenize_string(string):
       """
       I designed this method to be used independently of an obj/field. If this is the case, call _tokenize_field.
       It's more robust.
       :param string: e.g. 'salt lake city'
       :return: list of tokens
       """
       list_of_sentences = list()
       tmp = list()
       tmp.append(string)
       k = list()
       k.append(tmp)
       # print k
       list_of_sentences += k  # we are assuming this is a unicode/string

       word_tokens = list()
       for sentences in list_of_sentences:
           # print sentences
           for sentence in sentences:
               for s in sent_tokenize(sentence):
                   word_tokens += word_tokenize(s)

       return word_tokens

table = tfidf2()
with jsonlines.open("reliefweb_corpus_raw_20160331_eng_duprm.jsonl") as reader:
    for obj in reader:
        table.addDocument(obj["id"], MTokenizer.tokenize_string(obj["text"]))

table.prep()

with open("tfidf_all.json", "w") as f:
    f.write(json.dumps(table.documents))