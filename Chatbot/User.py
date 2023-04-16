class User:
   def __init__(self, name) -> None:
      self.username = name
      self.current_skills = {
         "Attack" : -1,
         "Defence" : -1,
         "Strength" : -1,
         "Hitpoints" : -1,
         "Ranged" : -1,
         "Prayer" : -1,
         "Magic" : -1,
         "Cooking" : -1,
         "Woodcutting" : -1,
         "Fletching" : -1,
         "Fishing" : -1,
         "Firemaking" : -1,
         "Crafting" : -1,
         "Smithing" : -1,
         "Mining" : -1,
         "Herblore" : -1,
         "Agility" : -1,
         "Thieving" : -1,
         "Slayer" : -1,
         "Farming" : -1,
         "Runecraft" : -1,
         "Hunter" : -1,
         "Construction" : -1,
      }