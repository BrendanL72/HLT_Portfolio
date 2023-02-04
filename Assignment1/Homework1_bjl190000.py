import sys
import os
import pickle
import csv
import re


#  Person stores important employee information and 
class Person:
   def __init__(self, first_name, last_name, middle_name, id, phone_num):
      self.first_name = first_name
      self.last_name = last_name
      self.middle_name = middle_name
      self.id = id
      self.phone_num = phone_num
   
   #  Prints employee information in the following format:
   #  Employee id: <id>
   #     <first_name> <mid> <last>
   #     <phone_num>
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

#functions to standardize employee information fields into their correct format

#  Last names should be Capital Case
def stan_last_name(last_name):
   return last_name.capitalize()

#  First names should be Capital Case
def stan_first_name(first_name):
   return first_name.capitalize()

#  Middle initials should be capitalized. If they do not exist, then just put X
def stan_mid_init(mid_init):
   default_mid_init = "X"
   if len(mid_init):
      return mid_init[0].capitalize()
   else:
      return default_mid_init

# IDs should be two capital letters followed by 4 digits: AB1234
def stan_id(id):
   id_regex = "[A-Z]{2}\d{4}"
   if re.fullmatch(id_regex, id):
      pass
   else:
      new_id = ""
      while not re.fullmatch(id_regex, new_id):
         new_id = input("ID Error for Previous ID {}, please enter an ID with 2 capital letters followed by 4 numbers\n".format(id))
      id = new_id
   return id

# Phone number uses the following format: XXX-XXX-XXXX
def stan_phone_num(phone_num):
   phone_num_format = "\d{3}[-]\d{3}[-]\d{4}"
   if re.fullmatch(phone_num_format, phone_num):
      pass
   else:
      raw_phone_num = re.sub("[^0-9]", "", phone_num)
      new_phone_num = raw_phone_num[0:3] + "-" + raw_phone_num[3:6] + "-" + raw_phone_num[6:10]
      phone_num = new_phone_num
   return phone_num


def standardize_info(last_name, first_name, mid_init, id, phone_num):
   last_name = stan_last_name(last_name)
   first_name = stan_first_name(first_name)
   mid_init = stan_mid_init(mid_init)
   id = stan_id(id)
   phone_num = stan_phone_num(phone_num)
   
   return (last_name, first_name, mid_init, id, phone_num)


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
         last_name, first_name, mid_init, id, phone_num = standardize_info(last_name, first_name, mid_init, id, phone_num)
         #add stuff
         if id not in persons.keys():
            persons[id] = Person(last_name, first_name, mid_init, id, phone_num)
         else:
            print("Error, duplicate id found")
   return persons



if __name__ == "__main__":
   #get the file path from command line arguments
   #command should look like python3 <this_file_name>.py data.csv
   args_list = sys.argv
   if len(args_list) <= 1:
      print("Error, no input file specified")
      sys.exit(1)
   input_file_name = args_list[1]
   input_file_path = os.path.relpath(input_file_name)
   
   #process and write the data from the csv into a disctionary and save it
   persons = process_input_file(input_file_path)
   pickle.dump(persons, open("persons.p", "wb"))

   #reopen the pickle and reread it
   pickle_persons = pickle.load(open("persons.p", "rb"))
   for id in pickle_persons.keys():
      pickle_persons[id].display()