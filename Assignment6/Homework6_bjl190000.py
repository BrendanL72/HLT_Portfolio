from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer


import os, shutil
import re
import pickle


def is_signif_link(link_text):
   invalid_strings = ["#", "File", "action=edit", "section=", "None", "Calculator", "Skill", "Icon", "Update", "Member"]
   base_path = os.path.basename(link_text)
   if not str(base_path).isalpha():
      return False
   for i in invalid_strings:
      if i in link_text:
         return False
   return True

def get_relevant_urls(url, max_links):
   req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
   raw_html = urlopen(req).read().decode('utf-8-sig')
   soup = BeautifulSoup(raw_html, features="html.parser")

   for script in soup(['script','style']):
      script.extract()

   #find first 15 relevant links that are significant
   counter = 0
   links = set()
   for link in soup.find_all('a'):
      l = link.get('href')
      if l not in links and is_signif_link(str(l)):
         links.add(l)
         counter += 1
         if counter > max_links:
            break
   return links

def scrape_text(url, root_url):
   #websites don't like me web scraping so I have to mimic Firefox
   url_string = str(url)
   if (url_string.startswith("/")):
      req_url = root_url + url_string
   else:
      req_url = url_string
   req = Request(req_url, headers={'User-Agent': 'Mozilla/5.0'})
   html_page = urlopen(req).read().decode('utf-8')
   soup = BeautifulSoup(html_page, features="html.parser")
   for script in soup(["script", "style"]):
      script.extract()
   text = soup.get_text()

   #save text in a file   
   counter = 1
   folder_name = "text/"
   f_name = os.path.basename(url)
   while os.path.exists(folder_name + f_name + str(counter)):
      counter += 1
   with open(folder_name + f_name + str(counter), "w", encoding="utf-8") as fhandle:
      fhandle.write(text)

def extract_sentences(f_name):
   f_handle = open(f_name, encoding='utf-8')
   raw_text = f_handle.read()

   #remove most whitespace from text
   text_chunks = [chunk for chunk in raw_text.splitlines() if chunk != ""]
   #get sentences and write them to file
   sentences = sent_tokenize("\n".join(text_chunks))
   with open(f_name + "_sentences", "w", encoding = 'utf-8') as f_handle:
      for s in sentences:
         f_handle.write(s + "\n")

# gets a number of highest frequency tokens from a corpus of text using tf-idf
def extract_terms(text_files, num_terms):
   #find tf-idf of all words in text
   #These settings make SciKit's tfidf preprocess the text to remove stopwords, punctuation, and lowercase the words
   tfidf = TfidfVectorizer(input='filename',stop_words={'english'}, lowercase=True, token_pattern=r"\b[a-zA-Z]\w+[a-zA-Z]\b")
   thing = tfidf.fit_transform(text_files)

   tfidf_dict = dict(zip(tfidf.get_feature_names_out(),tfidf.idf_))
   sorted_tfidf_values = sorted(tfidf_dict.items(), key=lambda x: x[1], reverse=True)
   print(sorted_tfidf_values[:num_terms])
   return(tfidf_dict)

def find_all_sentences(text_files, term):
   sentences = []
   for tf in text_files:
      fhandle = open(tf, "r", encoding='utf-8')
      for line in fhandle:
         if term in line or term.capitalize() in line:
            sentences.append(line)
   return sentences

if __name__ == "__main__":
   url = 'https://oldschool.runescape.wiki/w/Woodcutting'
   relevant_links = get_relevant_urls(url, 50)
   print("Scraping text")

   text_folder_name = "text/"
   if os.path.exists(text_folder_name):
      shutil.rmtree(text_folder_name)
   os.mkdir(text_folder_name)

   scrape_text(url, "")
   for l in relevant_links:
      scrape_text(l, 'https://oldschool.runescape.wiki')
   
   for fname in os.listdir(text_folder_name):
      extract_sentences(text_folder_name + fname)

   file_list = []
   sentence_file_list = []
   for fname in os.listdir(text_folder_name):
      if "sentences" not in fname:
         file_list.append(text_folder_name + fname)
      else:
         sentence_file_list.append(text_folder_name + fname)

   extract_terms(file_list, 40)

   most_important_terms = ["firemaking", "fire", "axe", "log", "canoe", "farming", "fletching", "tree", "experience", "attack", "bird nest", "woodcutting"]
   #create a base of knowledge for each important term
   term_dict = dict()
   for term in most_important_terms:
      print(term)
      term_dict[term] = find_all_sentences(sentence_file_list, term)
      print(term_dict[term][0])

   pickle_file = open("woodcutting_knowledge_base", "wb")
   pickle.dump(term_dict, pickle_file)