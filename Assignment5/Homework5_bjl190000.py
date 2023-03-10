from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import os, shutil
import re


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
         print(l)
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
   text_chunks = [chunk for chunk in raw_text.splitlines() if not re.match(r'^\s*$', chunk)]
   #get sentences and write them to file
   sentences = sent_tokenize(" ".join(text_chunks))
   with open(f_name + "_sentences", "w", encoding = 'utf-8') as f_handle:
      for s in sentences:
         f_handle.write(s + "\n")

# combine_corpus gets a list of files and combiens their text into a 
def combine_corpus(file_name_list, path):
   text = ""
   for fname in file_name_list:
      f_handle = open(path + fname, encoding='utf-8')
      text = text + "\n" + f_handle.read()

   return text


# gets a number of highest frequency tokens from a corpus of text using tf-idf
def extract_terms(text, num_terms):
   tokens = [token.lower() for token in text.split()]
   reduced_tokens = [t for t in tokens 
                     if (t.isalpha() and t not in stopwords.words('english'))]

   #find word frequency
   wnl = WordNetLemmatizer()
   lemmas = [wnl.lemmatize(t) for t in reduced_tokens]
   lemma_set = set(lemmas)
   lemma_count  = {n:lemmas.count(n) for n in lemma_set}
   most_common_nouns = sorted(lemma_count.items(), key=lambda x: x[1], reverse=True)
   print(most_common_nouns[:num_terms])

if __name__ == "__main__":
   url = 'https://oldschool.runescape.wiki/w/Woodcutting'
   relevant_links = get_relevant_urls(url, 15)
   print("Scraping text")

   folder_name = "text/"
   if os.path.exists(folder_name):
      shutil.rmtree(folder_name)
   os.mkdir(folder_name)

   scrape_text(url, "")
   for l in relevant_links:
      print(str(l))
      scrape_text(l, 'https://oldschool.runescape.wiki')
   
   for fname in os.listdir(folder_name):
      extract_sentences(folder_name + fname)

   file_list = []
   for fname in os.listdir(folder_name):
      if "sentences" not in fname:
         file_list.append(fname)

   text = combine_corpus(file_list, folder_name)
   extract_terms(text, 25)