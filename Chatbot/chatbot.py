from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
import nltk
import pickle
from pathlib import Path
import random
import re
import yaml
from User import User


#web scraping imports
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def preprocess_text(input_string):
   tokens = input_string.lower().split()
   filtered_tokens = [t for t in tokens if t not in stopwords.words('english')]
   return filtered_tokens


def get_message_similarity(user_tokens, related_tokens, required_tokens):
   msg_prob = 0 
   has_required_token = False
   if required_tokens:
      for t in user_tokens:
         if t in required_tokens:
            has_required_token = True
            break

   num_common_tokens = 0
   if has_required_token:
      for t in user_tokens:
         for rt in related_tokens:
            if t in rt:
               num_common_tokens += 1

      #print(num_common_tokens)
      msg_prob = float(num_common_tokens)/len(user_tokens)
   else:
      msg_prob = 0

   return msg_prob


#determine which response to use given tokens
def choose_response(responses, user_tokens):
   has_likely_response = False
   probs = {}
   for r in responses.keys():
      req_tokens = responses[r]["required_words"]
      if isinstance(req_tokens, str):
         req_tokens = req_tokens.lower()
      examples = responses[r]["examples"]
      if isinstance(examples, str):
         examples = examples.lower()
      probs[r] = get_message_similarity(user_tokens, related_tokens=examples, required_tokens=req_tokens)
      if probs[r] > 0.1:
         has_likely_response = True

   if has_likely_response:
      return max(probs.items(), key=lambda e: e[1])[0]
   else:
      return "unsure"
      

def respond(responses, response_type, inputs):
   if response_type in responses.keys():
      possible_responses = responses[response_type]["response"]
      if len(possible_responses) > 0:
         r = random.choice(possible_responses)
      else:
         r = "ERROR: NO RESPONSES UNDER THIS TYPE"

      print(r.format(*inputs))
   else:
      print("ERROR: INVALID RESPONSE TYPE")

#lookup tokens on the OSRS wiki
def wiki_lookup(lookup_string):
   osrs_link = "https://oldschool.runescape.wiki/w/"
   try:
      req = Request(osrs_link + lookup_string, headers= {'User-Agent': 'Mozilla/5.0'})
      raw_html = urlopen(req).read().decode('utf-8-sig')
      soup = BeautifulSoup(raw_html, features="html.parser")
      
      for script in soup(['script','style']):
         script.extract()

      text = soup.get_text()
      return text
   except:
      return "ERROR"

def extract_sentences(wiki_text):
   #remove most whitespace from text
   text_chunks = [chunk for chunk in wiki_text.splitlines() if chunk != ""]
   #get sentences and write them to file
   sentences = sent_tokenize(" ".join(text_chunks))
   return sentences

def filter_sentences(sentences):
   for s in sentences:
      if "[edit | edit source]" in s or "(edit)" in s:
         sentences.remove(s)
      elif not s.endswith("."):
         sentences.remove(s)
      elif "\n" in s:
         sentences.remove(s)
      elif s.split()[0].isdigit():
         sentences.remove(s)
      elif "•" in s or "[" in s:
         sentences.remove(s)

   return sentences 

#gets the highest of postive ('pos'), negative ('neg'), or neutral ('neu') statements
def getMostSentScores(sentences, type):
   sent_analyzer = SentimentIntensityAnalyzer()
   all_sent_scores = {}
   for s in sentences:
      sent_scores = sent_analyzer.polarity_scores(s)
      all_sent_scores[s] = sent_scores[type]
   return all_sent_scores

if __name__ == "__main__":
   user_input = ""

   #responses
   responses_file = "./data/responses.yaml"
   responses_fhandle = open(responses_file, "r")
   responses = yaml.safe_load(responses_fhandle)

   for r in responses:
      examples = responses[r]["examples"]
      if examples:
         for i,e in enumerate(examples):
            examples[i] = preprocess_text(e)


   #users 
   users_path = Path("./data/users")
   if users_path.is_file():
      with open(users_path, "rb") as users_fhandle:
         users = pickle.load(users_fhandle)
   else:
      users = {}

   current_user = User("default")
   skills = current_user.current_skills.keys()

   current_state = "hello"
   bot_response = "hello"

   current_topic = ""
   current_verb = ""
   response_inputs = []

   next_response_type = ""
   
   while (user_input != "end"):
      respond(responses, bot_response, response_inputs)
      user_input = input()
      response_inputs = []

      if user_input == "":
         continue
      if (current_state == "hello"):
         if user_input in users.keys():
            bot_response = "welcome_back"
         else:
            users[user_input] = User(user_input)
            bot_response = "new_user"
         current_user = users[user_input]
         response_inputs.append(current_user.username)
         
         current_state = ""
      else:
         input_tokens = preprocess_text(user_input)
         next_response_type = choose_response(responses,input_tokens)

         input_tags = nltk.pos_tag(user_input.split())

         if next_response_type == "unsure":
            response_inputs = [user_input]
         elif next_response_type == "opinion":
            #get the first verb and topic
            for t in input_tags:
               #current things found
               if current_topic != "" and current_verb != "":
                  break
               #first noun
               if t[1].startswith("NN") or t[1] == "VBD" or t[1] == "VBG" and current_topic == "":
                  current_topic = t[0]
               #first verb
               elif t[1].startswith("V"):
                  current_verb = t[0]

            response_inputs = [current_topic]

         elif next_response_type == "elab_opinion":
            #look up OSRS wiki for information
            
            wiki_text = wiki_lookup(current_topic)
            sentences = extract_sentences(wiki_text)
            real_sentences = filter_sentences(sentences)

            wiki_response = ""
            #check if wiki page is valid
            if current_topic != "":
               if wiki_text != "ERROR":
                  #find a positive sentence
                  sent_scores = getMostSentScores(sentences, "pos")
                  rand_sentence = sorted(sent_scores, key=lambda s: s[1], reverse=True)[:10]
                  wiki_response = random.choice(rand_sentence)
               else:
                  #invalid, say something else
                  wiki_response = "No, I can't :("
            else:
               wiki_response = "Elaborate on what? We haven't talked about anything yet!"
            response_inputs = [wiki_response]
         elif next_response_type == "tip":
            #look up OSRS wiki for information
            for t in reversed(input_tags):
               if t[1].startswith("NN") or t[1] == "VBD" or t[1] == "VBG" and current_topic == "":
                  current_topic = t[0]
                  break

            wiki_text = wiki_lookup(current_topic)
            sentences = extract_sentences(wiki_text)
            real_sentences = filter_sentences(sentences)
            wiki_response = random.choice(real_sentences)
            response_inputs = [wiki_response]
            pass
         elif next_response_type == "change_topic":
            #clear the current topic to discuss something else
            if current_topic != "":
               if current_verb != "":
                  last_verb = current_verb + " "
               else:
                  last_verb = current_verb
               last_topic = current_topic
               response_inputs = [last_verb, last_topic]
               current_topic = ""
               current_verb = ""
            else:
               next_response_type = "no_prev_topic"
         elif next_response_type == "hello_there":
            response_inputs = [current_user.username]
         elif next_response_type == "skill_issue":
            #get skill needed
            input_tags = nltk.pos_tag(user_input.split())
            after_to = False
            to_tokens = []
            current_skill = ""
            cannot = ""

            for t in input_tags:
               if t[1] == "TO":
                  after_to = True
               if after_to:
                  to_tokens.append(t[0])
                  if t[1].startswith("V") and t[1] not in skills:
                     current_verb = t[0]
               if t[0] in skills:
                  current_skill = t[0]
            #look up the item on OSRS
            wiki_text = wiki_lookup(" ".join(to_tokens))
            #item not found, ask them to ask again
            if wiki_text == "ERROR":
               next_response_type = "unsure"
            #item found, find the level requirements
            else:
               current_skill_level = -1
               skill_reqs = -1
               
               #has the user previously mentioned their level?
               if current_user.current_skills[current_skill] == -1:
                  #no, ask them for their info
                  while (current_skill_level > 0):
                     skill_input = input("Well that depends, what is your current {} level?".format(current_skill))
                     if skill_input.isdigit():
                        current_skill_level = int(skill_input)
                  #update user's skill level
                  current_user.current_skills[current_skill] = current_skill_level
               else:
                  current_skill_level = current_user.current_skills[current_skill]
               if current_skill_level < skill_reqs:
                  cannot = "not"
            response_inputs = [current_skill, cannot, current_verb, current_topic]

         bot_response = next_response_type

   with open(users_path, "wb") as users_fhandle:
      pickle.dump(users, users_fhandle)