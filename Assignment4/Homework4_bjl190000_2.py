from nltk import ngrams
from nltk import word_tokenize
import pickle

# compute_prob() determines the likelihood of a line of text to be within a given set of bigrams using LaPlace smoothing   
def compute_prob(text, bigram_counts, vocab_size):
   unigrams_test = word_tokenize(text)
   bigrams_test = list(ngrams(unigrams_test, 2))

   prob = 1

   for b in bigrams_test:
      bigram_count = bigram_counts[b] if b in bigram_counts else 0
      first_token_count = unigram_dict[b[0]] if b[0] in unigram_dict else 0

      prob = prob * (bigram_count + 1)/(first_token_count + vocab_size)

   return prob

# get_pred_acc() receives two files, one with predictions and another with the actual answers
# it compares each prediction to their corresponding true values and determines the prediction accuracy
def get_pred_acc(preds_fname, true_fname):
   preds_fhandle = open(preds_fname, "r")
   true_fhandle = open(true_fname, "r")

   preds_line = preds_fhandle.readline()
   true_line = true_fhandle.readline()

   num_correct = 0
   num_lines = 0

   while (preds_line != "" and true_fhandle != ""):
      if preds_line == true_line:
         num_correct += 1
      num_lines += 1
      preds_line = preds_fhandle.readline()
      true_line = true_fhandle.readline()

   return num_correct/num_lines

if __name__ == "__main__":
   fnames = ["data/LangId.train.English", "data/LangId.train.French", "data/LangId.train.Italian"]
   unigrams = []
   bigrams = []
   
   vocab_size = 0
   num_tokens = 0

   #read in each pickle dictionary
   for fname in fnames:
      unigram_fname = fname + ".unigrams"
      bigram_fname = fname + ".bigrams"

      unigram_dict = pickle.load(open(unigram_fname, "rb"))
      bigram_dict = pickle.load(open(bigram_fname, "rb"))

      #get total training vocab and token size 
      vocab_size += len(unigram_dict.keys())

      unigrams.append(unigram_dict)
      bigrams.append(bigram_dict)

   # read in the test data and determine which 
   test_fname = "data/LangId.test"
   test_preds_fname = test_fname + ".preds"
   test_fhandle = open(test_fname, "r" , encoding="utf-8")
   test_preds_fhandle = open(test_preds_fname, "w")

   line_number = 1
   for line in test_fhandle:
      #test for each language model
      probs = []
      for i in range(len(fnames)):
         probs.append(compute_prob(line, bigrams[i], vocab_size))
      #determine which has highest likelihood
      best_lang = probs.index(max(probs))

      #write predictions to a file
      # 0 - english
      # 1 - french
      # 2 - italian
      language_prediction = ""
      if best_lang == 0:
         language_prediction = "English"
      elif best_lang == 1:
         language_prediction = "French"
      elif best_lang == 2:
         language_prediction = "Italian"
      else:
         language_prediction = "Error"

      test_preds_fhandle.write(str(line_number) + " " + language_prediction + "\n")
      
      line_number += 1

   test_preds_fhandle.close()

   #determine accuracy
   print("Prediction Accuracy:", get_pred_acc(test_preds_fname, "data/LangId.sol"))
   