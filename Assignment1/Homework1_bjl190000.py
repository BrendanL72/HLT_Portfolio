import sys
import os
import pickle
import csv

class Person:
   def __init__(self, first_name, last_name, middle_name, id, phone_num):
      self.first_name = first_name
      self.last_name = last_name
      self.middle_name = middle_name
      self.id = id
      self.phone_num = phone_num
   
   def display(self):
      format_vars = {"first_name" : self.first_name, 
                     "middle_name" : self.middle_name, 
                     "last_name" : self.last_name, 
                     "id" : self.id,
                     "phone_num" : self.phone_num}

      display_format = """Employee id: {id} 
            {first_name} {middle_name} {last_name} 
            {phone_num} 
            """ 
      print(display_format.format(**format_vars))

#  process_input_file gets a formatted fully populated input file path which contains information about people
#  It returns a dictionary of Person objects where the person's ID is the key
#  It also standardizes any data to be in the proper format (ex. change first letter of first name to be capitalized)
def process_input_file(input_file_path):
   persons = {}
   with open(input_file_path, 'r') as csv_file:
      input_file_reader = csv.reader(csv_file)
      #ignore the first line
      next(input_file_reader)
      for row in input_file_reader:
         last_name, first_name, mid_init, id, phone_num = row
         #standardize and check id 
         standardize_info()
         #add stuff
         persons[id] = Person(last_name, first_name, mid_init, id, phone_num)
   return persons

def standardize_info():
   pass

if __name__ == "__main__":
   args_list = sys.argv
   if len(args_list) <= 1:
      print("Error, no input file specified")
      sys.exit(1)
   input_file_name = args_list[1]
   input_file_path = os.path.relpath(input_file_name)
   persons = process_input_file(input_file_path)
   pickle.dump(persons, open("persons.p", "wb"))

   #reopen the pickle and reread it
   pickle_persons = pickle.load(open("persons.p", "rb"))
   for id in pickle_persons.keys():
      pickle_persons[id].display()