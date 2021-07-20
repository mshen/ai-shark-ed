import random
import numpy
import copy
import os
import time
import json
import textwrap
from sys import exit
from collections import OrderedDict

class Island():

    '''A class to represent the island. Contains most assets shared by children.
    '''

    # Dictionary of dates with corresponding event flags. Sets initial date.
    dict_dates_events = OrderedDict([("Mon 1","intro"), ("Tues 2","no"), ("Wed 3","no"), ("Thurs 4","no"),
                                    ("Fri 5","no"), ("Sat 6","no"), ("Sun 7","turnip"), ("Mon 8","no"),
                                    ("Tues 9","no"), ("Wed 10","no"), ("Thurs 11","no"), ("Fri 12","no"),
                                    ("Sat 13","no"), ("Sun 14","turnip"), ("Mon 15","no"), ("Tues 16","no"),
                                    ("Wed 17","no"), ("Thurs 18","no"), ("Fri 19","no"), ("Sat 20","no"),
                                    ("Sun 21","turnip"), ("Mon 22","no"), ("Tues 23","no"), ("Wed 24","no"),
                                    ("Thurs 25","no"), ("Fri 26","no"), ("Sat 27","no"), ("Sun 28","turnip"),
                                    ("Mon 29","no"), ("Tues 30","last")] )
    date_indices = list(dict_dates_events.keys())
    weather_dict = {"Mon 1": "sunny"}
    island_chain = OrderedDict() #dict maybe to store past reports
    date = "Mon 1"

    # Creates dictionaries for fish/bug/fossil prices
    with open('fish.txt', 'r') as file:
        fish_string = file.read().replace('\n', '')
        dict_fish = json.loads(fish_string)
    list_fish = list(dict_fish.keys())
    with open('bugs.txt', 'r') as file:
        bug_string = file.read().replace('\n', '')
        dict_bugs = json.loads(bug_string)
    list_bugs = list(dict_bugs.keys())
    with open('fossils.txt', 'r') as file:
        fossil_string = file.read().replace('\n', '')
        dict_fossils = json.loads(fossil_string)
    list_fossils = list(dict_fossils.keys())
    dict_tools = {"Fishing rod":1000, "Shovel":1500, "Net":1000, "Candy":500}
    list_all_items = list_fish + list_bugs + list_fossils
    dict_all_items = dict(dict_fish)
    dict_all_items.update(dict_bugs)
    dict_all_items.update(dict_fossils)

    # Creates dictionaries for animal personalities/species/catchphrases/dialogue
    with open('animal_personalities.txt', 'r') as file:
        personality_string = file.read().replace('\n', '')
        dict_animal_personalities = json.loads(personality_string)
    with open('animal_species.txt', 'r') as file:
        species_string = file.read().replace('\n', '')
        dict_animal_species = json.loads(species_string)
    with open('animal_catchphrases.txt', 'r') as file:
        catchphrases_string = file.read().replace('\n', '')
        dict_animal_catchphrases = json.loads(catchphrases_string)
    list_all_animals = list(dict_animal_catchphrases.keys())
    friendship = {}

    def __init__(self, island_name, player_name):
        '''Initializes the island instance.'''
        self.island_name = island_name
        self.player_name = player_name
        self.actions = 20
        self.set_date(0)

    @classmethod
    def generate_animals(cls):
        '''Generates 10 animals for the island.'''
        cls.island_animals_dict = {}
        animal_names = random.sample(cls.list_all_animals, 10)
        for i in animal_names:
            a = Animal(str(i))
            cls.island_animals_dict[i] = a
        cls.set_names(island_name, player_name, cls.island_animals_dict)
        cls.island_animals_list = list(cls.island_animals_dict.keys())

    @classmethod
    def weather(cls):
        '''Outputs random choice of several weather options.'''
        weather = ["very hot", "sunny", "breezy", "chilly", "cloudy", "rainy", "pouring"]
        if cls.date in cls.weather_dict:
            pass
        else:
            cls.weather_dict[cls.date] = random.choice(weather)
        print("It's {} today.".format(cls.weather_dict[cls.date]))

    @classmethod
    def set_date(cls, index = 0):
        '''Sets the date.'''
        cls.date = cls.date_indices[index]

    @classmethod
    def get_date(cls):
        '''Returns today's date.'''
        return cls.date

    # Only will use this in the Player child class since need to
    # reset Player actions to 30.
    @classmethod
    def advance_day(cls):
        '''Moves date forward in the order of the OrderedDict of dates.'''
        index = cls.date_indices.index(cls.date)
        if index == 29:
            ans = "Today is the last day of my probation period..."
        else:
            cls.date = cls.date_indices[index+1]
            print("Good morning! Today is {}.".format(cls.date))
            cls.weather()

    @classmethod
    def display_animals(cls):
        '''Displays all the animals on the island.'''
        print("\nANIMALS")
        print("{:^15}{:^18}{:^18}".format("Name:","Personality:","Friendship:"))
        for x in Island.friendship.items():
            print("     {:<16}{:<10} {:^18}".format(x[0],Island.dict_animal_personalities[x[0]],x[1]))

    @classmethod
    def set_names(cls, island_name, player_name, animal_dict):
        '''Sets class attributes for easy use by child classes.'''
        cls.island_name = island_name
        cls.player_name = player_name
        cls.animal_names = animal_dict.keys()
        cls.animal_dict = animal_dict

    @classmethod
    def update_friendship(cls):
        '''Updates the friendship levels of animals into a dictionary.'''
        for key in cls.animal_dict:
            cls.friendship.update({key:cls.animal_dict[key].friendship_level})

class Animal(Island):

    '''A class to represent an animal villager.'''

    def __init__(self, animal_name, friendship_level=0, inventory=[], letter_inventory=[]):
        '''Initializes an animal when created with name, personality,
        species and unique catchphrase. Some unused assets if I want to add on.
        '''
        self.animal_name = str(animal_name).title()
        self.wallet = 999999
        self.friendship_level = friendship_level
        self.inventory = inventory
        self.letter_inventory = letter_inventory
        try:
            self.personality = Island.dict_animal_personalities[self.animal_name]
            self.species = Island.dict_animal_species[self.animal_name]
            self.catchphrase = Island.dict_animal_catchphrases[self.animal_name]
        except KeyError:
            print("Failed to initialize", self.animal_name)

    def talk(self):
        '''Imports dialogue from txt files. Returns villager-specific dialogue,
        replacing player name and catchphrases.
        '''
        personality = Island.dict_animal_personalities[self.animal_name]
        personality_txt = personality.lower() + "_dialogue.txt"
        with open(personality_txt) as file:
            dialogue = file.read().splitlines()

        if self.friendship_level == 0:
            speech = "Hi, I don't think we've met before. I'm {} the {}!".format(self.animal_name, self.species.lower())
        elif (self.friendship_level > 0): #and self.friendship_level < 50):
            one_line = random.choice(dialogue)
            if one_line.find('[player]') != -1:
                speech = one_line.replace('[player]', Island.player_name)
            else:
                speech = one_line
            if one_line.find('[catchphrase]') != -1:
                speech = speech.replace('[catchphrase]', Island.dict_animal_catchphrases[self.animal_name])
        if self.friendship_level < 30:
            self.friendship_level += 2
        elif self.friendship_level >= 30 and self.friendship_level < 50:
            self.friendship_level += 3
        elif self.friendship_level >= 50 and self.friendship_level < 75:
            self.friendship_level += 4
        elif self.friendship_level >= 75:
            self.friendship_level += 5
        Island.update_friendship()
        speech = speech.strip('"')
        speech = textwrap.fill(speech, width=70)
        return speech + "\n"

    def receive_gift(self, gift):
        '''Gift received is added to animal inventory (never really used
        otherwise, but just to record it) and it increases their friendship.'''
        self.friendship_level += 5
        Island.update_friendship()
        self.inventory.extend(gift)

class Player(Island):

    '''A class to represent the player.'''

    tool_inventory = []
    pocket = {}
    turnip_dict = {}
    letter_inventory = {}

    def __init__(self, island_name, player_name, wallet = 1000):
        '''Initializes the player.'''
        super().__init__(island_name, player_name)
        self.name = player_name
        self.wallet = wallet
        self.date = Island.date # This is probably never used again
        self.loan = 1000000
        Island.generate_animals()
        Island.update_friendship()

    def display_status(self):
        '''Prints a status screen. Didn't implement turnips but left it
        since I want to do this later.
        '''
        print("...................................................................")
        print("\nName: {}\n\nSTATUS:".format(self.name))
        date_report = "Today is {}.".format(Island.get_date())
        weather_report = "It's {} today on {} Island.".format(Island.weather_dict[Island.get_date()],Island.island_name)
        wallet_loan_report = "I have {} bells in my wallet and {} bells left to pay!".format(self.wallet,self.loan)
        #animals_here = "\nANIMALS:\n{}".format("  ".join(Island.animal_names))
        print(date_report)
        print(weather_report)
        print("I have {} actions left today!".format(self.actions))
        print(wallet_loan_report)
        #print(animals_here)
        Island.display_animals()
        self.display_inventory()
        self.display_tools()
        self.display_turnips()
        print("...................................................................")

    def fish(self):
        '''Method for player fishing.'''
        if self.actions > 0:
            if "Fishing rod" not in self.tool_inventory:
                print("You can't fish without a fishing rod. Purchase one from the shop first.")
            else:
                self.actions -= 1
                fish = random.choice(self.list_fish)
                while fish == "Coelacanth":    # Coelacanth will only show up in rain
                    if Island.weather_dict[Island.date] == "rainy" or Island.weather_dict[Island.date] == "pouring":
                        break
                    else:
                        fish = random.choice(self.list_fish)
                chance = random.randint(1,11)
                if chance < 3:
                    print("\n--------------------------------------------------------------------")
                    print("You hooked the {}, but it got away...".format(fish.lower()))
                    print("--------------------------------------------------------------------\n")
                else:
                    print("\n--------------------------------------------------------------------------")
                    print("You caught a {}! It's worth {} bells! You put it in your pocket.".format(fish.lower(), self.dict_fish[fish]))
                    print("--------------------------------------------------------------------------\n")
                    if fish in self.pocket:
                        self.pocket[fish] = self.pocket[fish]+1
                    else:
                        self.pocket[fish] = 1
        else:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            print("You have no actions left for today! Sleep and try again tomorrow!\n")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def catch_bugs(self):
        '''Method for player catching bugs.'''
        if self.actions > 0:
            if "Net" not in self.tool_inventory:
                print("You can't catch bugs without a net. Purchase one from the shop first.")
            else:
                self.actions -= 1
                bug = random.choice(self.list_bugs)
                chance = random.randint(1,11)
                if chance < 4:
                    print("\n--------------------------------------------------------------------")
                    print("So close! You swung at the {} and missed! :(".format(bug.lower()))
                    print("--------------------------------------------------------------------\n")
                else:
                    print("\n--------------------------------------------------------------------------")
                    print("You caught a {}! It's worth {} bells! You put it in your pocket.".format(bug.lower(), self.dict_bugs[bug]))
                    print("--------------------------------------------------------------------------\n")
                    if bug in self.pocket:
                        self.pocket[bug] = self.pocket[bug]+1
                    else:
                        self.pocket[bug] = 1
        else:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            print("You have no actions left for today! Sleep and try again tomorrow!\n")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def dig_fossils(self):
        '''Method for player digging fossils.'''
        if self.actions > 0:
            if "Shovel" not in self.tool_inventory:
                print("You can't dig for fossils without a shovel. Purchase one from the shop first.")
            else:
                self.actions -= 1
                fossil = random.choice(self.list_fossils)
                chance = random.randint(1,11)
                if chance < 2:
                    print("\n--------------------------------------------------------------------")
                    print("You tried your best, but you couldn't find a fossil.")
                    print("--------------------------------------------------------------------\n")
                else:
                    print("\n--------------------------------------------------------------------------")
                    print("You dug up {}! It's worth {} bells! You put it in your pocket.".format(fossil.lower(), self.dict_fossils[fossil]))
                    print("--------------------------------------------------------------------------\n")
                    if fossil in self.pocket:
                        self.pocket[fossil] = self.pocket[fossil]+1
                    else:
                        self.pocket[fossil] = 1
        else:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            print("You have no actions left for today! Sleep and try again tomorrow!\n")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def pay_loan(self):
        '''Method for when the villager pays the loan.'''
        if self.actions > 0:
            print("\n.......................\nYou have {} bells. \nYou owe {} bells.\n.......................".format(self.wallet, self.loan))
            while True:
                try:
                    payment = int(input("How many bells would you like to pay off? (Enter '0' to return) "))
                    break
                except ValueError:
                    print("Please enter an integer number of bells to pay. ")
            if payment == 0:
                print("\n--------------------------------------------------------------------")
                print("You still owe {} bells.".format(self.loan))
                print("--------------------------------------------------------------------\n")
            elif payment <= self.wallet:
                self.loan = self.loan - payment
                if self.loan <= 0:
                    self.loan = 0
                self.wallet = self.wallet - payment
                self.actions -= 1
                print("\n--------------------------------------------------------------------")
                print("You made a payment of {} bells.\nYou have {} bells left in your wallet.\nYou now owe {} bells.".format(payment, self.wallet, self.loan))
                print("--------------------------------------------------------------------\n")
            elif payment > self.wallet:
                print("\n--------------------------------------------------------------------")
                print("Oops! You don't have that many bells!")
                print("--------------------------------------------------------------------\n")
        else:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            print("You have no actions left for today! Sleep and try again tomorrow!\n")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def display_inventory(self):
        '''Method to display only pocket contents.'''
        print("\nPOCKET")
        if not self.pocket:
            print("There are no items in your pocket.")
        else:
            print("{:<20}{:^20}".format("Item Name:","Quantity:"))
            for item in self.pocket.items():
                print("    {:<20}{:^20}".format(item[0],item[1]))
        print("")

    def display_tools(self):
        '''Method to display only tool inventory.'''
        print("TOOLS")
        if not self.tool_inventory:
            print("You don't have any tools.")
        else:
            for item in self.tool_inventory:
                print("{:<20}".format(item))
        print("")

    def display_turnips(self):
        '''Method to display only turnip inventory.'''
        print("TURNIPS")
        if not self.turnip_dict:
            print("You don't have any turnips.")
        else:
            for item in self.tool_inventory.items():
                print("{:<20}{:^20}".format(item[0],item[1]))
        print("")

    def receive_gift(self):
        '''When player receives a gift, adds the gift to the pocket.'''
        gift = random.choice(Island.list_all_items)
        if gift in self.pocket:
            self.pocket[gift] = self.pocket[gift]+1
        else:
            self.pocket[gift] = 1
        print("Congratulations! Received {} from {}!\n".format(gift.lower(), random.choice(Island.island_animals_list)))
        print("---------------------------------------")
        self.display_inventory()
        print("---------------------------------------\n")

    def receive_friendship_gift(self, animal_name):
        '''When player talks to animal with high friendship, chance of gift.'''
        gift = random.choice(Island.list_all_items)
        if gift in self.pocket:
            self.pocket[gift] = self.pocket[gift]+1
        else:
            self.pocket[gift] = 1
        print("{} enjoyed your chat and gave you a {}!\n".format(animal_name, gift.lower()))
        print("---------------------------------------")
        self.display_inventory()
        print("---------------------------------------\n")

    def give_gift(self, giftee):
        '''Takes villager name as an argument. Subtracts the selected
        gift from player's pocket inventory.
        '''
        if self.actions > 0:
            self.display_inventory()
            while True:
                if not self.pocket:
                    print("\n-----------------------------------------------")
                    print("You don't have anything to gift...")
                    print("-----------------------------------------------\n")
                    break
                else:
                    try:
                        gift = input("What would you like to gift? (Cancel with '0') ")
                        if gift == "0":
                            break
                        else:
                            self.display_inventory()
                            if self.pocket[gift.capitalize()] > 1:
                                self.pocket[gift.capitalize()] -= 1
                            else:
                                del self.pocket[gift.capitalize()]
                            self.actions -= 1
                            print("\n-------------------------------------------------------")
                            print("Gave {} to {}!".format(gift.lower(), giftee))
                            print("{}'s friendship level increased by 5 points!".format(giftee))
                            print("-------------------------------------------------------\n")
                            Island.animal_dict[giftee].receive_gift(gift)
                            break
                    except KeyError:
                        print("\n-----------------------------------------------")
                        print("You don't have any {}!".format(gift))
                        print("-----------------------------------------------\n")
        else:
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
            print("You have no actions left for today! Sleep and try again tomorrow!\n")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def get_date(self):
        '''Overwrites parent method to keep self.date consistent'''
        self.date = Island.date
        return Island.date

    def advance_day(self):
        '''Moves date forward. Overrides parent method. This one is the only
        one that is called, but I left the parent one since originally I wasn't
        sure which class I wanted to call it.
        '''
        index = Island.date_indices.index(Island.date)
        if Island.date == "Tues 30":
            print("\n....................................................................\n")
            print("Today is the last day of my probation period.")
            self.end_sequence()
        else:
            Island.date = Island.date_indices[index+1]
            self.date = Island.date
            self.actions = 20
            self.loan_check()
            print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nGood morning! Today is {}.\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~".format(Island.date))
            Island.weather()
            self.gift_event()

    def gift_event(self):
        '''Chance of a random gift every day~'''
        a = random.randint(1,10)
        if self.wallet <= 500:
            if a < 4:
                self.receive_gift()
        else:
            if a == 1:
                self.receive_gift()

    def end_sequence(self):
        '''Begins game end sequence.'''
        print("I worked hard this past month and paid off {} bells of my loan.".format(1000000-self.loan))
        if self.loan == 0:
            print("\nTom Nooky: Congratulations! You managed to pay off your home loan!")
            time.sleep(3.05)
            print("Tom Nooky: I'd like to officially welcome you to {} Island!".format(Island.island_name))
            time.sleep(3.05)
            print("Tom Nooky: We're happy to invite you as a permanent, productive resident of {} Island!".format(Island.island_name))
            time.sleep(3.05)
        elif self.loan > 0:
            Island.update_friendship()
            if all(value >= 100 for value in Island.friendship.values()):
                print("\nCongratulations! You have fulfilled the hidden condition.")
                time.sleep(3.05)
                print("Although you weren't able to pay off your home loan, your friendship\nwith the villagers makes you an invaluable part of our {} island community.".format(Island.island_name))
                time.sleep(3.05)
            else:
                print("\nUnfortunately, it wasn't enough to pay off the loan.\nTom Nooky told me to say my goodbyes to the villagers.")
                time.sleep(3.05)
                print("He said we're going fishing for sharks soon. I wonder what he meant...\n...\n...\n...")
                time.sleep(3.05)
        print("\n##########  Thanks for playing!  ##########\n")
        exit(1)

    def loan_check(self):
        '''Executes every time self.advance_day() is called in case player
        won and wants to end early.
        '''
        if self.loan == 0:
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("Congratulations! You paid off your whole home loan!")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nContinue playing? ")

            while True:
                try:
                    m = int(input("\n[1] Yes\n[0] No\n"))
                    if m == 1:
                        break
                    elif m == 0:
                        print("\nTom Nooky: Congratulations! You managed to pay off your home loan!")
                        print("Tom Nooky: I'd like to officially welcome to {} Island! We're \nhappy to invite you as a permanent, productive resident!".format(Island.island_name))
                        print("\n##########  Thanks for playing!  ##########\n")
                        exit(1)
                    else:
                        print("Please enter a valid number for your selection.")
                        continue
                except ValueError:
                    print("Please enter the number for your selection.")

class Turnip(Island):

    '''Unused Turnip class.'''

    def __init__(self, price, quantity_purchased):
        '''Initializes a turnip.'''
        self.purchase_date = Island.date
        self.quantity = quantity_purchased
        self.price = price

    def is_fresh(self):
        '''Checks if the turnip is fresh or not. Not fully implemented.'''
        return Island.date

class Shop(Island):

    '''A class to establish a shop, its inventory and prices.'''

    def __init__(self):
        '''Initializes the shop.'''
        self.set_turnip_price()

    @classmethod
    def check_Sunday(cls):
        '''Checks if it's Sunday.'''
        if Island.date[0:3] == 'Sun':
            return True
        else:
            return False

    @classmethod
    def set_turnip_price(cls):
        '''Sets the turnip price depending on the day.'''
        if cls.check_Sunday() == True:
            cls.turnip_price = random.randint(10,120)
        else:
            cls.turnip_price = random.randint(10,700)
        cls.shop_inventory = {"Fishing rod":1500, "Shovel":4500, "Net":1000, "Candy":500, "Turnip":cls.turnip_price}

class Engine():

    '''A class to execute game loops.'''

    def __init__(self, island, player):
        '''Takes island and player arguments and initializes them.'''
        self.island = island
        self.villager = player

    def main_menu_loop(self, villager, island):
        '''Takes island and villager (player) arguments. Creates the main
        game loop.
        '''
        while True:
            try:
                self.print_main()
                action = int(input(("""What would you like to do? """)))
                if action == 0:
                    print("\nNow exiting the game...\n\n~~~Thanks for playing!~~~\n")
                    exit(1)
                elif action == 1:
                    self.villager.display_status()
                elif action == 2:
                    if self.villager.actions > 0:
                        self.talk_loop(villager, island, island.island_animals_list)
                    else:
                        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
                        print("You have no actions left for today! Sleep and try again tomorrow!\n")
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                elif action == 3:
                    if self.villager.actions > 0:
                        self.shop_loop(villager, island)
                    else:
                        print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
                        print("You have no actions left for today! Sleep and try again tomorrow!\n")
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                elif action == 4:
                    self.villager.pay_loan()        # actions check is in method
                elif action == 5:
                    while True:
                        island.display_animals()
                        print("")
                        try:
                            giftee = input("Who would you like to gift? (Press '0' to quit) ")
                            if giftee == '0':
                                break
                            else:
                                if giftee.title() not in Island.island_animals_list:
                                    print("{} is not on this island!".format(giftee.title()))
                                    continue
                                else:
                                    giftee = giftee.title()
                                    self.villager.give_gift(giftee)
                        except TypeError:   # I don't think this ever executes since everything is a string
                            print("Please enter the name of a villager to talk to or '0' to quit. ")
                elif action == 6:
                    self.villager.dig_fossils()
                elif action == 7:
                    self.villager.catch_bugs()
                elif action == 8:
                    self.villager.fish()
                elif action == 9:
                    self.villager.advance_day()
            except ValueError:
                print("\nSorry, your input is invalid. Please enter a number corresponding\nto your selection or enter '0' to quit.")

    def print_main(self):
        '''Prints the main menu options.'''
        print(
            """\n       [1] Status           [4] Pay loan              [7] Catch bugs
       [2] Talk             [5] Give gift             [8] Fish
       [3] Shop             [6] Dig for fossils       [9] Sleep
       [0] Quit\n""")

    def talk_loop(self, villager, island, animal_dict):
        '''Takes villager, island and dictionary containing keys of animal names
        and values that correspond to their Animal class objects. This loop
        executes when the talk option in the main menu is selected.
        '''
        while True and self.villager.actions > 0:
            island.display_animals()
            print("")
            try:
                animal = input("Who would you like to talk to? Enter the name of a villager or '0' to quit. ")
                if animal == '0':
                    break
                else:
                    if animal.title() not in animal_dict:
                        print("{} is not on this island!".format(animal.title()))
                        continue
                    else:
                        print("\n-------------------------------------------------------")
                        print("{}: {}".format(animal.title(), island.island_animals_dict[animal.title()].talk()))
                        print("{}'s friendship increased to {}.".format(animal.title(), island.island_animals_dict[animal.title()].friendship_level))
                        print("-------------------------------------------------------\n")
                        if island.island_animals_dict[animal.title()].friendship_level > 50:
                            a = random.randint(1,10)    # stole this from Player's gift_event() method
                            if a == 1 or a == 5:        # but wanted to add more conditions for that when
                                villager.receive_friendship_gift(animal.title()) # it's called after sleeping
                        self.villager.actions -= 1
            except TypeError:
                print("Please enter the name of a villager to talk to or '0' to quit. ")

    def shop_loop(self, villager, island):
        '''Takes villager and island arguments. This loop executes when the
        shop option is selected from the main menu.
        '''
        shop = Shop()
        print("Welcome to the shop! What would you like to do? ")
        try:
            shopchoice = int(input("""
            [1] Buy
            [2] Sell
            [0] Never mind!\n\n"""))
            if shopchoice == 1:
                print("\nYou have {} bells in your wallet.\nWhat would you like to buy? ".format(self.villager.wallet))
                while True and self.villager.actions > 0:
                    try:
                        buyitem = int(input("""
                        [1] Shovel        4500 bells
                        [2] Fishing rod   1500 bells
                        [3] Net           1000 bells
                        [4] Candy          500 bells
                        [0] Quit\n\n"""))
                        if buyitem == 1:
                            item = "Shovel"
                        elif buyitem == 2:
                            item = "Fishing rod"
                        elif buyitem == 3:
                            item = "Net"
                        elif buyitem == 4:
                            item = "Candy"
                        elif buyitem == 0:
                            break
                        else:
                            print("Oops! Please select one of the options or enter '0' to quit. ")
                            continue
                        payment = Shop.shop_inventory[item]
                        if payment <= self.villager.wallet:
                            if item not in self.villager.tool_inventory:
                                self.villager.tool_inventory.extend([item])
                                self.villager.wallet -= payment
                                print("\n--------------------------------------------------------------------")
                                print("You bought a {} for {} bells! Added it to your inventory.".format(item.lower(),payment))
                                print("You have {} bells remaining in your wallet!".format(self.villager.wallet))
                                print("--------------------------------------------------------------------\n")
                                self.villager.actions -= 1
                                break
                            else:
                                print("\n--------------------------------------------------------------------")
                                print("You already have that item!")
                                print("--------------------------------------------------------------------\n")
                                break
                        else:
                            print("\n--------------------------------------------------------------------")
                            print("Oops! You don't have that many bells! ")
                            print("--------------------------------------------------------------------\n")
                    except ValueError:
                        print("Please enter a number selection or enter '0' to quit.\nYou have {} bells in your wallet.\nWhat would you like to buy? ".format(self.villager.wallet))

            # added the option to sell everything in inventory (I caved since
            # it was so tedious) and to sell > one of duplicate items at a time
            elif shopchoice == 2:

                while True and self.villager.actions > 0:
                        try:
                            villager.display_inventory()
                            sell = input("What would you like to sell?\nType an item's name to sell the item, cancel with '0',\nor enter 'all' to sell everything in your pocket (costs 6 actions) ")
                            sell_item = sell.capitalize()
                            if sell_item == "0":
                                break

                            # sell everything in pocket at once; costs 6 actions
                            elif sell_item.lower() == 'all':
                                if not self.villager.pocket:
                                    print("\n--------------------------------------------------------------------")
                                    print("\nYou don't have anything in your pocket to sell! Returning to menu. ")
                                    print("--------------------------------------------------------------------\n")
                                    break
                                else:
                                    self.villager.actions -= 6
                                    if self.villager.actions < 0:
                                        self.villager.actions = 0
                                    sold_log = []
                                    total_sum = 0
                                    for pocket_key in self.villager.pocket:
                                        sell_quantity = self.villager.pocket[pocket_key]
                                        self.villager.wallet += island.dict_all_items[pocket_key] * sell_quantity
                                        total_sum += island.dict_all_items[pocket_key] * sell_quantity
                                        receipt = "Sold {} {}(s) at {} bells each and received {} bells!".format(sell_quantity, pocket_key.lower(), island.dict_all_items[pocket_key], island.dict_all_items[pocket_key] * sell_quantity)
                                        sold_log.extend([receipt])
                                    self.villager.pocket.clear()
                                    # prints a log of everything sold.
                                    print("\n--------------------------------------------------------------------")
                                    print("\n".join(sold_log))
                                    print("\nTotal earnings: {} bells".format(total_sum))
                                    print("--------------------------------------------------------------------\n")
                                    continue

                            # error checks that item requested is even in pocket before continuing
                            elif sell_item not in self.villager.pocket:
                                print("\n--------------------------------------------------------------------")
                                print("\nYou don't have any {}!\n".format(sell_item.lower()))
                                print("--------------------------------------------------------------------\n")
                                continue

                            # just wanting to sell some but not all items in pocket
                            else:
                                # error checks quantity for type and to see if dictionary contains it
                                while True:
                                    try:
                                        sell_quantity = input("\nHow many {}(s) would you like to sell?\n(Enter '0' to exit and 'a' to sell all) ".format(sell_item.lower()))
                                        if sell_quantity == "0":
                                            break
                                        elif sell_quantity == "a":
                                            sell_quantity = self.villager.pocket[sell_item.capitalize()]
                                        else:
                                            try:
                                                sell_quantity = int(sell_quantity)
                                            except ValueError:
                                                print("\n-----------------------------------------------------------------------")
                                                print("Please enter a valid integer number, 'a' for all, or '0' to exit.")
                                                print("-----------------------------------------------------------------------\n")
                                                continue
                                        if sell_quantity > self.villager.pocket[sell_item.capitalize()]:
                                            print("\n--------------------------------------------------------------------")
                                            print("You don't have that many {}(s)!\n".format(sell_item.lower()))
                                            print("--------------------------------------------------------------------\n")
                                            continue
                                        else:
                                            break
                                    except KeyError:
                                        print("\n--------------------------------------------------------------------")
                                        print("You don't have any {}!\n".format(sell_item.lower()))
                                        print("--------------------------------------------------------------------\n")

                                # if '0' continues in second loop
                                if sell_quantity == "0":
                                    continue
                                else:
                                    # all checks cleared! does the actual subtraction
                                    if self.villager.pocket[sell_item.capitalize()] > sell_quantity:
                                        self.villager.pocket[sell_item.capitalize()] -= sell_quantity
                                    else:
                                        del self.villager.pocket[sell_item.capitalize()]

                                    self.villager.actions -= 1
                                    self.villager.wallet += island.dict_all_items[sell_item] * sell_quantity
                                    print("\n--------------------------------------------------------------------")
                                    print("\nSold {} {}(s) at {} bells each and received {} bells!\n".format(sell_quantity, sell_item.lower(), island.dict_all_items[sell_item], island.dict_all_items[sell_item] * sell_quantity))
                                    print("--------------------------------------------------------------------\n")
                                    continue
                        except KeyError:
                            print("\n--------------------------------------------------------------------")
                            print("You don't have any {}!\n".format(sell_item.lower()))
                            print("--------------------------------------------------------------------\n")
            elif shopchoice == 0:
                print("\nSee you next time!\n")
            else:
                print("Exiting the shop... Please shop again with a valid input!")
        except ValueError:
            print("Exiting the shop... Please shop again with a valid input!")

    def start(self, island, villager):
        '''Takes island and villager as arguments and prints the intro text.
        Also sets the weather for the first time and begins main menu loop.
        '''
        # wraps text to display in 70 chars
        nook1 = textwrap.fill("Tom Nooky: Hello, hello, {}!".format(villager.name.upper()), width=70)
        nook2 = textwrap.fill("Tom Nooky: How did I know your name? I stole a peek at your passport when you tumbled out of your plane... Where are we, you ask?", width=70)
        nook3 = textwrap.fill("Tom Nooky: It looks like your flight had to have an emergency landing... but not to worry!")
        nook4 = textwrap.fill("Tom Nooky: You've landed on {} Island!".format(island.island_name.upper()))
        nook5 = textwrap.fill("Tom Nooky: Unfortunately, due to recent spikes in tourism and everyone wanting to move here, we barely have enough accomodations for our own town residents...")
        nook6 = textwrap.fill("Tom Nooky: Luckily for you, I happen to have one housing unit left. What to do... You seem to have nowhere to go...")
        nook7 = textwrap.fill("Tom Nooky: Ah! I know! Since I'm generous, I'll give you an interest-free loan! The mortgage is a measly 1,000,000 bells.")
        nook8 = textwrap.fill("Tom Nooky: I'll need you to work extra hard in the next month to pay off your mortgage...")
        nook9 = textwrap.fill("Tom Nooky: If you can't come up with the bells in time...so sorry, but I'll have to toss you to the sharks!")

        # prints wrapped text
        print("\n" + nook1 + "\n")
        time.sleep(1.00)
        print(nook2 + "\n")
        time.sleep(1.00)
        print(nook3 + "\n")
        time.sleep(1.00)
        print(nook4 + "\n")
        time.sleep(1.00)
        print(nook5 + "\n")
        time.sleep(1.00)
        print(nook6 + "\n")
        time.sleep(1.00)
        print(nook7 + "\n")
        time.sleep(1.00)
        print(nook8 + "\n")
        time.sleep(1.00)
        print(nook9 + "\n")
        time.sleep(1.00)

        ready = input("Tom Nooky: Are you ready? ")
        if ready.lower() == "no" or ready == "0":
            print("Tom Nooky: Yes, yes. Well that's too bad.")
        elif ready.lower() == "yes" or ready == "1":
            yes = textwrap.fill("Tom Nooky: Yes, yes! I can't wait to see what a productive member of society you'll be...")
            print(yes)
        else:
            pass
        enter = input("Press 'Enter' to continue.")
        print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nGood morning! Today is {}.\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~".format(Island.date))
        Island.weather()
        self.main_menu_loop(villager, island)

# Creates an Engine class object and calls its method to start the game.
print("""
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  ^^^                                                   ^^^
  ^^^        ~~~~            /|     ~~~~~~              ^^^
  ^^^                 ~~~~~~/ |~~~~~                    ^^^
  ^^^             ~~~~~~~~~~~~~~~~~~~~~                 ^^^
  ^^^                                                   ^^^
  ^^^  ~Welcome to Animal Intersection: Shark Edition!~ ^^^
  ^^^                                                   ^^^
  ^^^                                                   ^^^
  ^^^                     ~~~~~~~~~~~                   ^^^
  ^^^                                                   ^^^
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
""")
island_name = input("Please enter the name of the island you will be visiting: ")
if len(island_name) < 1:
    island_name = "Shark"
player_name = input("Please enter your name: ")
if len(player_name) < 1:
    player_name = "Rando"
villager = Player(island_name, player_name)
island = Island(island_name, player_name)
eng = Engine(island, villager)
eng.start(island, villager)
