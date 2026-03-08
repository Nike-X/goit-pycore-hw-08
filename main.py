# Homework 12:
#
# This script implements an assistant bot that manages phone contacts. 
# Bot uses AddressBook class to store contacts (Records in AddressBook), 
# and decorators for error handling. Each Record has name, phone number(s),
# and (optionally) birthday.
#
# When the bot starts, the address book is loaded from a file 
# (or created if loading fails). Upon exit, the address book is automatically 
# saved to a binary file.
# 
# The bot is launched and prompted via the command line interface.
#
# List of commands:
# 
# hello - returns a greeting message
# add <name> <phone> - adds a new contact (or adds a phone if the contact already exists)
# change <name> <old_phone> <new_phone> - replaces the specified phone number
# phone <name> - shows all phone numbers of a contact
# all - shows all contacts from the address book (including birthdays)
# add-birthday <name> <dd.mm.YYYY> - adds a birthday to a contact
# show-birthday <name> - shows contact's birthday date
# birthdays - returns a list of contacts whose birthday will be in the next 7 days
# close | exit - exit bot

## Import section
import pickle
from functools import wraps
from adress_book import AddressBook, Record

## Service functions:
## - error handler
## - user's input parser

# This function serializes the address book with pickle and saves it to a binary file
def save_data(book: AddressBook, filename: str = "addressbook.pkl"):
    # Create and open file with context manager
    with open(filename, "wb") as file:
        # Serialize the address book and write it to the file
        pickle.dump(book, file)

# Loads the address book from a binary file
def load_data(filename: str = "addressbook.pkl"):
    # Try load book from file
    try:
        with open(filename, "rb") as file:
            # If book loaded successfully, return it
            return pickle.load(file)
    # If we get an error, create and return empty address book
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        return AddressBook()

# Add a decorator function to handle ValueError, KeyError, and IndexError
def input_error(function):
    # Wrap received function to preserve its metadata
    @wraps(function)
    def inner(*args, **kwargs):
        # Call received function
        try:
            return function(*args, **kwargs)
        # Handle ValueError
        except ValueError as error:
            return f"Invalid arguments: {error}"
        # Handle KeyError
        except KeyError:
            return "Requested contact does not exist."
        # Handle IndexError
        except IndexError:
            return "Not enough arguments for this command."
        # Handle any other error
        except Exception as error:
            return f"An unexpected error occured: {type(error).__name__} {error}"
    # Return inner function
    return inner

# This function parses user input from CLI
# We do not use decorator, instead we check for empty input in the function itself 
# to avoid ambiguity in error handling
def parse_input(user_input: str):
    # Split the user's input into command and arguments
    chunks = user_input.split()

    # Check that input is not empty, return empty command and args if empty input
    if not chunks:
        return "", []

    # Assign command and args from chunks
    cmd, *args = chunks
    # For command, strip unnecessary characters and convert to lowercase to compare 
    # command with predefined
    return cmd.strip().lower(), args

## Applied functions

# Simple greeting handler
# Note: args and book are included to keep the handler signature consistent
# Note: Decorator was added to unify code structure. This function 
# does not generate any errors for now
@input_error
def hello(_args, _book):
    return "How can I help you?"

# This function adds a new contact to the address book, or adds a phone number 
# to an existing contact. It uses decorator for error handling
@input_error
def add_contact(args: list, book: AddressBook):
    # Assign provided args to variables
    name, phone = args

    # Search for existing contact record with provided name
    record = book.find(name)
    # If contact does not exist, create new record in address book
    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return f"Contact {name} added with phone number {phone}."
    
    # If contact exists, add provided phone number to this contact 
    # (previous phone numbers remain unchanged)
    record.add_phone(phone)
    return f"Phone number {phone} added to contact {name}."

# This function changes phone number for existing contact. It uses decorator for error handling
@input_error
def change_contact(args: list, book: AddressBook):
    # Assign provided args to variables 
    name, old_phone, new_phone = args

    # Search for existing contact record with provided name
    record = book.find(name)
    # If contact does not exist, return an error (we cannot change non-existent contact)
    if record is None:
        raise KeyError
    
    # If contact exists, replace provided old phone number 
    # with provided new number
    changed = record.edit_phone(old_phone, new_phone)

    # If the old phone number was not found, record.edit_phone() returns False
    # In this case, we should return a corresponding message
    if not changed:
        return f"Phone number {old_phone} was not found for contact {name}."

    # Show the user which number was replaced
    return f"Contact {name} successfully changed. Phone number {old_phone} has been successfully replaced with {new_phone}."

# This function returns the phone number(s) of the selected contact. It uses decorator for error handling
@input_error
def show_phone(args: list, book: AddressBook):
    # Assign name from args
    name, = args

    # Search for existing contact record with provided name
    record = book.find(name)

    # If contact does not exist, return an error (we cannot change non-existent contact)
    if record is None:
        raise KeyError
    
    # If contact exists, return all its phone numbers as a string
    phones = ", ".join(phone.value for phone in record.phones)
    return f"{record.name.value}: {phones}." if phones else f"No phones found for contact {name}."

# This function sets birthday date for existing contact
# It uses decorator for error handling
@input_error
def add_birthday(args: list, book: AddressBook):
    # Assign name from args
    name, birthday = args

    # Search for existing contact record with provided name
    record = book.find(name)

    # If contact does not exist, return an error (we cannot change non-existent contact)
    if record is None:
        raise KeyError
    
    # If the contact exists, assign the birthday
    record.add_birthday(birthday)
    return f"Birthday for contact {name} set to {str(record.birthday)}."

# This function shows birthday date of existing contact
# It uses decorator for error handling
@input_error
def show_birthday(args: list, book: AddressBook):
    # Assign name from args
    name, = args

    # Search for existing contact record with provided name
    record = book.find(name)

    # If contact does not exist, return an error (we cannot change non-existent contact)
    if record is None:
        raise KeyError
    
    # If contact exists, return its birthday (or warn user that it is not set)
    if record.birthday is None:
        return f"Birthday is not set for contact {name}."
    
    return f"{record.name.value} birthday is {str(record.birthday)}"

# This function returns a list of contacts whose birthday will be in the next 7 days
# Does not require any additional input arguments. It uses decorator for error handling
# Note: args are included to keep the handler signature consistent
@input_error
def birthdays(_args: list, book: AddressBook):
    # All logic is implemented inside the AddressBook.get_upcoming_birthdays() method,
    # so we just need to call it. Get list of dicts with upcoming birthday dates
    upcoming_birthdays = book.get_upcoming_birthdays()

    # Warn user if there are no upcoming birthdays
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next 7 days."
    
    # Convert the resulting dictionaries into formatted strings
    lines = []
    for item in upcoming_birthdays:
        lines.append(f"{item['name']}: {item['congratulation_date']}")
    
    # Return formatted output with a brief explanation
    return "Upcoming birthdays in the next 7 days:\n" + "\n".join(lines)

# This function returns all contacts in address book, line by line. It uses decorator for error handling
# Note: args are included to keep the handler signature consistent
@input_error
def all_contacts(_args: list, book: AddressBook):
    # Warn user if address book is empty
    if not book.data:
        return "No contacts saved."
    
    # Create an empty list for formatted contact descriptions
    lines = []

    # Generate string description for each contact. Description includes name, all phone numbers,
    #  and birthday (if it exists).
    for record in book.data.values():
        name = record.name.value
        phones = ", ".join(phone.value for phone in record.phones) if record.phones else "N/A"
        birthday = str(record.birthday) if record.birthday else "N/A"
        lines.append(f"{name}: {phones}; birthday: {birthday}.")

    # Join all lines into a single string and return it
    # Printing is done only in main()
    return "\n".join(lines)

# Define handlers for all available commands (except control commands like close/exit)
# This will allow us to abandon the long if...elif...else statement in main()
# It also simplifies adding new commands in the future

COMMAND_HANDLERS = {
    "hello": hello,
    "add": add_contact,
    "change": change_contact,
    "phone": show_phone,
    "all": all_contacts,
    "add-birthday": add_birthday,
    "show-birthday": show_birthday,
    "birthdays": birthdays,
}

# Main function, processes user's input, defines commands and prints responses to console
def main():
    # Try to load address book from file
    # Note: if loading fails, load_data() automatically creates a new address book
    book = load_data()

    # Print greetings
    print("Welcome to the assistant bot!")

    # Wait for user's input
    while True:
        user_input = input("Enter a command: ")

        # Parse user's input to separate command and arguments
        command, args = parse_input(user_input)

        # Define commands to exit from bot
        if command in ["close", "exit"]:
            # Save current book to a file, then exit
            save_data(book)
            print("Good bye!")
            break
        
        # Ignore empty input
        if command == "":
            continue
        
        # Look up the user command in the command handlers dictionary
        handler = COMMAND_HANDLERS.get(command)

        # If command is found, execute it
        # Note: to unify command handling, we always provide args
        # when calling the function (even if args are not used)
        if handler is not None:
            print(handler(args, book))
        # Warn about invalid command
        else:
            print("Invalid command.")

# This code executes main() function if script is launched from command line
if __name__ == "__main__":
    main()
