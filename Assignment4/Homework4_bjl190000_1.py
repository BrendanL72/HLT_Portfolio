from nltk import ngrams
from nltk import word_tokenize
from collections import Counter
import pickle

def create_ngram_dict(fname):
   #read in text and turn into tokens
   fhandle = open(fname, 'r', encoding="utf-8")
   raw_text = fhandle.read()
   tokens = word_tokenize(raw_text)

   unigrams = list(ngrams(tokens, 1))
   bigrams = list(ngrams(tokens, 2))
   
   #WINDOWS GAMING
   unigram_freqs = dict(Counter(set(unigrams)))
   bigram_freqs = dict(Counter(set(bigrams)))

   return (unigram_freqs, bigram_freqs)

if __name__ == "__main__":
   test_files = ["data/LangId.train.English", "data/LangId.train.French", "data/LangId.train.Italian"]
   for fname in test_files:
      print(fname)
      unigram_counts, bigram_counts = create_ngram_dict(fname)

      pickle.dump(unigram_counts, open(fname + ".unigrams", 'wb'))
      pickle.dump(bigram_counts, open(fname + ".bigrams", 'wb'))