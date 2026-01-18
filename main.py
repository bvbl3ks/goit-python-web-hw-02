from collections import UserDict
from datetime import datetime, timedelta
import pickle



# Помилки

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as err:
            return str(err)
        except IndexError:
            return "Enter the argument for the command."
        except KeyError:
            return "Contact not found."
    return inner


# Класси

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, number):
        if not number.isdigit() or len(number) != 10:
            raise ValueError("Phone number must contain 10 digits.")
        super().__init__(number)


class Birthday(Field):
    def __init__(self, date_str):
        try:
            date = datetime.strptime(date_str, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date)


# Record

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, new_phone):
        self.phones.append(Phone(new_phone))

    def remove_phone(self, trash_phone):
        for p in self.phones:
            if p.value == trash_phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Old phone number not found.")

    def find_phone(self, target_phone):
        for p in self.phones:
            if p.value == target_phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        bday = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "—"
        return f"Name: {self.name.value}, Phones: {phones}, Birthday: {bday}"
    
#Pickle
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

#AdressBook

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for man in self.data.values():
            if not man.birthday:
                continue

            birthday = man.birthday.value.replace(year=today.year)

            if birthday < today:
                birthday = birthday.replace(year=today.year + 1)

            delta = (birthday - today).days

            if 0 <= delta <= 7:
                congratulate_date = birthday
                if congratulate_date.weekday() >= 5:  # weekend
                    congratulate_date += timedelta(days=(7 - congratulate_date.weekday()))

                upcoming.append({
                    "name": man.name.value,
                    "birthday": congratulate_date.strftime("%d.%m.%Y")
                })

        return upcoming

    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())


#Handler

@input_error
def add_contact(args, book):
    name, phone = args
    person = book.find(name)

    if person is None:
        person = Record(name)
        book.add_record(person)
        message = "Contact added."
    else:
        message = "Contact updated."

    if phone not in [p.value for p in person.phones]:
        person.add_phone(phone)

    return message



@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.phones:
        return "No phone numbers."
    return "; ".join(p.value for p in record.phones)




@input_error
def show_all(args, book):
    return str(book)


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return "Birthday not set."
    return record.birthday.value.strftime("%d.%m.%Y")


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return "\n".join(f"{u['name']}: {u['birthday']}" for u in upcoming)


#parse, main

def parse_input(user_input):
    parts = user_input.split()
    return parts[0].lower(), parts[1:]


def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()
        if not user_input:
            continue

        command, args = parse_input(user_input)

        if command in ("exit", "close"):
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()