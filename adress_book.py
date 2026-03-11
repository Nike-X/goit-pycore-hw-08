# Homework 12: define classes for address book, which stores some contacts (name and associated phone numbers):
# Field - parent class for all fields (name and phone).
#
# Name - class for contact name, validates that name is not empty; inherits Field class.
#
# Phone - class for contact's phone number, validates that number consists of 10 digits; 
# inherits Field class.
#
# Birthday - class for contact's birth date, validates that date is provided as 'dd.mm.yyyy';
# inherits Field class.
#
# Record - class for contact itself; stores a name and a list of phone numbers. Can add, find, 
# edit(replace), and remove phone number.
#
# AddressBook - class for the whole address book; inherits UserDict class. 
# As a dictionary, stores Records as values with Record.name as a key. Can add, find and delete Record by its name.
# Also contains get_upcoming_birthdays function, which returns a list of users, 
# whose birthday will be in the next 7 days.

from collections import UserDict
from datetime import date, datetime, timedelta

# Define class Field to store some values (name or phone)
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Define class Name to store Record name
class Name(Field):
    def __init__(self, value):
         # Assign value via setter
         self.name = value

    # Define getter
    @property
    def name(self):
         return self.value

    # Also define setter
    @name.setter
    def name(self, value):
         # Strip unnecessary characters and explicitly convert to string
         value = str(value).strip()
         # Check if name is empty
         if not value:
              # Raise error if name is empty
              raise ValueError("Name cannot be empty.")
         self.value = value  

# Define class Phone to store phone number. Phone inherits Field class
# Add a validation for Phone creation
class Phone(Field):
    # We get some phone value (probably string), that we should assign to Phone
    def __init__(self, value):
          # Assign value via setter
          self.phone = value

    # Define getter
    @property
    def phone(self):
      return self.value
          
    # Also define setter
    @phone.setter
    def phone(self, value):
      # Explicitly convert to string and strip unnecessary chars
      value = str(value).strip()
      # Check that it is valid phone (10 digits). If not, raise a ValueError
      if not(len(value) == 10 and value.isdigit()):
            raise ValueError(f'Invalid phone number: {value}. Phone number must contain exactly 10 digits.')
      self.value = value

class Birthday(Field):
    def __init__(self, value):
        # Assign value via setter
        self.birthday = value
    
    # Define getter
    @property
    def birthday(self):
        return self.value
    
    # Also define setter
    @birthday.setter
    def birthday(self, value):
        try:
            # Explicitly convert to string and strip unnecessary chars
            value = str(value).strip()
            # Convert string to date (DD.MM.YYYY format)
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        # If provided string does not match the format DD.MM.YYYY, raise ValueError
        except ValueError:
            raise ValueError(f'Invalid date format: {value}. Use DD.MM.YYYY')
    # Define __str__ method to represent birthday as a string
    def __str__(self):
         return self.value.strftime('%d.%m.%Y')

# Define Record class, to store record in address book (name and associated phone numbers)
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    # Define method to add phone number
    def add_phone(self, phone):
          # Create Phone object and append it to phones list
          self.phones.append(Phone(phone))

    # Define method to find phone number in Record
    def find_phone(self, phone):
          # Convert to string explicitly and strip unnecessary chars
          phone = str(phone).strip()
          # Loop through phones to find required values, and return appropriate Phone object (or None)
          for p in self.phones:
                if p.phone == phone:
                      return p
          return None
          
    # Define method to edit (replace) existing phone number in Record
    def edit_phone(self, old_phone, new_phone):
          # Find required phone number using find_phone method
          p = self.find_phone(old_phone)
          # If number does not exist, just return False
          if p is None:
                return False
          # If number exists, assign new value to corresponding Phone object via setter and return True
          p.phone = new_phone
          return True
    
    # Define method to remove phone number from Record
    def remove_phone(self, phone):
          # Find required phone number using find_phone method
          p = self.find_phone(phone)
          # If number does not exist, just return False
          if p is None:
                return False
          # If number exists, remove it from phones list and return True
          self.phones.remove(p)
          return True

    def add_birthday(self, birthday):
         # Create Birthday object and assign it to Record.birthday field
         self.birthday = Birthday(birthday)

    # Define string representation for the Record object
    def __str__(self):
        # Convert phones list to string, phone numbers separated by semicolon,
        # or explicitly show that birthday is not specified
        phones = '; '.join(p.value for p in self.phones) if self.phones else 'not set'
        # Convert birthday date object to string, or explicitly show that birthday is not specified
        birthday = self.birthday.value.strftime('%d.%m.%Y') if self.birthday else 'not set'
        # Return formatted string
        return f'Contact name: {self.name.name}, phones: {phones}, birthday: {birthday}'

# Define class for the whole address book (inherited from UserDict).
# It stores Records as dict items, Name is a key, and record is a value
class AddressBook(UserDict):
    # Define method to add new record to address book (add type hint for record)
    def add_record(self, record: Record):
            # Assign provided record as a value for Record's name as a key
            self.data[record.name.value] = record
    
    # Define method to find required Record by its name
    def find(self, name):
         # Convert to string explicitly and strip unnecessary chars
         name = str(name).strip()
         # Return apropriate dict item
         return self.data.get(name)
    
    # Define method to delete Record by its name
    def delete(self, name):
         # Convert to string explicitly and strip unnecessary chars
         name = str(name).strip()
         # Return True if successfully deleted (self.data.pop found required item and returned its value)
         # Return False if not found (because pop provide None in that case, and is not None return False)
         return self.data.pop(name, None) is not None
    
    # Returns a list of contacts whose birthday will be in the next 7 days
    def get_upcoming_birthdays(self):
         # Obtain current date
         current_date = date.today()
         # Create empty list for birthdays
         upcoming_birthdays = []

         for record in self.data.values():
              if record.birthday is None:
                   continue
              # Get contact birthday date from Record object
              birthday_date = record.birthday.value

              # Find next birthday and construct it as date object ...
              next_birthday_date = date(current_date.year, birthday_date.month, birthday_date.day)

              # ... and we make an amendment if the nearest birthday is in the next calendar year
              if next_birthday_date < current_date:
                  next_birthday_date = date(current_date.year + 1, birthday_date.month, birthday_date.day)
              # Check that the next birthday will be in the next 7 days (including today)
              if current_date <= next_birthday_date < current_date + timedelta(days=7):
                  # If the next birthday is on Saturday, set congratulation date on next Monday
                  if next_birthday_date.weekday() == 5:
                        congratulation_date = next_birthday_date + timedelta(days=2)
                  # If the next birthday is on Sunday, also set congratulation date on next Monday
                  elif next_birthday_date.weekday() == 6:
                        congratulation_date = next_birthday_date + timedelta(days=1)
                  # If the next birthday is a working day, do not transfer it
                  else:
                        congratulation_date = next_birthday_date
                  # 1. Format congratulation_date to string
                  # 2. Construct dictionary with Record name and congratulation date for each Record
                  # 3. Append dictionaries to the birthdays list
                  upcoming_birthdays.append({'name': record.name.value,
                                              'congratulation_date': congratulation_date.strftime('%d.%m.%Y')})
         return upcoming_birthdays