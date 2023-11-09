"""This script manage phonebook
-----------------------------
you can use commands below:
add <name> <phone number> [birthday] - add new record to the phonebook
change <name> <phone number>         - change record into phonebook
phone <name> <phone number>          - show phone number for name
find <part_of_name>|<part_of_phone>  - search for part of name or phone in phonebook
delete <name>                        - delete user <name> from phonebook
birthday <name> [birthday]           - show how many days to birthday for <name> and can set birthday
show all                             - show all records from phonebook
show N                               - show records fo N record in one time
hello                                - it is just hello :)
exit | close | good bye              - finish the program
help                                 - this information
"""

import pickle
from pathlib import Path
from collections import UserDict
from datetime import date, datetime, timedelta


class Field:
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    ...


class Phone(Field):
    def __init__(self, value: str):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        if len(value) < 10 or not value.isdigit():
            raise ValueError
        self.__value = value


class ExceptionWrongBirthday(Exception):
    pass


class Birthday(Field):
    def __init__(self, birthday: str = None):
        self.__birthday = None
        self.birthday = birthday

    @property
    def birthday(self):
        return self.__birthday

    @birthday.setter
    def birthday(self, birthday: str):
        if birthday:
            try:
                bday = datetime.strptime(birthday, "%Y-%m-%d").date()
            except:
                raise ExceptionWrongBirthday
            self.__birthday = bday

    def __str__(self):
        if self.birthday != None:
            bday = self.birthday.strftime("%Y-%m-%d")
        else:
            bday = "No Birthday "
        return f"{bday:<12}"


class Record:
    def __init__(self, name: str, phone: str = None, birthday: Birthday = None):
        self.name = Name(name)
        self.phones = [Phone(phone)] if phone else []
        self.birthday = birthday

    def remove_phone(self, phone: Phone):
        value = None
        for val in self.phones:
            if val.value == phone:
                value = val
        self.phones.remove(value)

    def edit_phone(self, old_phone: Phone, new_phone: Phone):
        found = None
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                found = True
        if not found:
            raise ValueError

    def find_phone(self, phone: Phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph
        return f"not found"

    def add_phone(self, phone: str):
        ll = list(map(lambda x: x.value, self.phones))
        if phone not in ll:
            self.phones.append(Phone(phone))

    def days_to_birthday(self) -> int | None:
        if not self.birthday:
            return None
        current_year = datetime.today().year
        today = datetime.today().date()
        new_bd = self.birthday.birthday
        new_bd = new_bd.replace(year=current_year)
        # new_bd = datetime(current_year, self.birthday.value.month, self.birthday.value.day).date()
        delta = (new_bd - today).days
        if delta >= 0:
            return delta
        else:
            new_bd = new_bd.replace(year=current_year + 1)
            delta = (new_bd - today).days
            return delta

    def __str__(self):
        return f"Contact name: {self.name.value:<20}, birthday: {self.birthday}, phones: {'; '.join(p.value for p in self.phones)}"


class AddressBook(UserDict):
    def delete(self, name: str) -> None:
        if name in self.data:
            del self.data[name]

    def iterator(self, n: int) -> str:
        nn = 0
        result = ""
        for item in self.data:
            result += f"{self.data.get(item)}\n"
            nn += 1
            if nn == n or (nn < n and not self.data.get(item)):
                yield result
                result = ""
                nn = 0
        if result:
            yield result

    def find(self, name: str) -> Record:
        for record in self.data:
            if record == name:
                return self.data[record]

    def find_name(self, part_of_name: str):
        result = ""
        for record in self.data:
            if part_of_name in record:
                result += f"{self.data[record]}\n"
        return result

    def find_phone(self, part_of_phone: str):
        result = ""
        for record in self.data:
            for phone in self.data[record].phones:
                if part_of_phone in phone.value:
                    result += f"{record} has {phone}\n"
        return result

    def add_record(self, new_record: Record) -> str:
        self.data[new_record.name.value] = new_record
        return f"Contact {new_record.name.value} add succefully!"

    def __getitem__(self, key: str) -> Record:
        return self.data[key]

    def finish(self):
        with open(Path("phonebook1.txt"), "wb") as pb:
            data = pickle.dumps(self.data)
            pb.write(data)

    def start(self):
        with open(Path("phonebook1.txt"), "rb") as pb:
            data = pb.read()
            self.data = pickle.loads(data)
            

book = AddressBook()


def find_name(*args) -> str:
    name = ""
    idx = 0
    for item in args:
        if item.isalpha():
            name += f"{item} "
            idx += 1
        else:
            name = name.strip()
            break
    return name.strip(), idx


data_pb = Path("phonebook.txt")


def input_error(func):
    def inner(*args) -> str:
        try:
            return func(*args)
        except KeyError:
            retcode = "Unkwown person, try again"
        except ValueError:
            retcode = "The phone number must consist of 10 or more digits!"
        except IndexError:
            retcode = "Insufficient parameters for the command!"
        except ExceptionWrongBirthday:
            retcode = "Birthday date must be in yyyy-mm-dd pattern, where d(1-31) m(1-12) y(1-9999) is digits"
        except AttributeError as e:
            retcode = e

        return retcode

    return inner


def normalize(number: str) -> str:
    for i in "+-() ":
        number = number.replace(i, "")
    if int(number):
        return number
    else:
        raise ValueError


@input_error
def add_number(*args) -> str:
    name, idx = find_name(*args)
    args = list(args[idx:])
    birthday = None
    phone = args.pop(0)
    if args and "-" in args[-1]:
        birthday = args.pop(-1)
    if name in book:
        record = book[name]
        if phone:
            record.add_phone(phone)
        if birthday:
            record.birthday = Birthday(birthday)
    else:
        rec = Record(name, phone, Birthday(birthday))
        book.add_record(rec)
    if args:
        for rec in args:
            book[name].add_phone(rec)
    return f"Abonent added|updated succefully!"


@input_error
def change_number(*args) -> str:
    name, idx = find_name(*args)
    record = book.find(name)
    record.edit_phone(args[-2], args[-1])
    return f"Phone number for <{name}> changed succefully!"


@input_error
def find_phone(*args) -> str:
    name, idx = find_name(*args)
    record = book.find(name)
    found_phone = record.find_phone(args[-1])
    return f"Phone number {found_phone} in phonebook for {name}"


@input_error
def delete(*args) -> str:
    name, idx = find_name(*args)
    book.delete(name)
    return f"Abonent <{name}> was succefully deleted!"


@input_error
def birthday(*args) -> str:
    name, idx = find_name(*args)
    args = list(args[idx:])
    record = book.find(name)
    if args and "-" in args[-1]:
        birthday = args.pop(-1)
        record.birthday = Birthday(birthday)
    days = record.days_to_birthday()
    if days == 0:
        return "Birthday is today!"
    elif days == None:
        return "Birthday is not defined!"
    else:
        return f"{name}'s birthday is in {days} days"


@input_error
def show(args=None, *_):
    if not args:
        return show_all()
    else:
        for items in book.iterator(int(args)):
            print(items)
            _ = input("Press enter for next part")


@input_error
def show_all() -> str:
    return_string = ""
    for record in book.values():
        return_string += f"{record}\n"
    return return_string


@input_error
def help(*_) -> str:
    return __doc__


@input_error
def hello(*_) -> str:
    return "Hi! How can I help you?"


@input_error
def find(*args):
    if args[0].isalpha():
        return book.find_name(args[0])
    if args[0].isdigit():
        return book.find_phone(args[0])


COMMANDS = {
    "add": add_number,
    "change": change_number,
    "show all": show_all,
    "phone": find_phone,
    "delete": delete,
    "hello": hello,
    "help": help,
    "show": show,
    "find": find,
    "birthday": birthday,
}


def parser(command: str) -> str:
    if command.lower().startswith("show all"):
        return show_all()

    if command.lower().startswith(("good bye", "close", "exit")):
        book.finish()
        return "Good bye!"

    command = command.split()
    command[0] = command[0].lower()
    if command[0] in COMMANDS:
        return COMMANDS[command[0]](*command[1:])

    return "Command not recognized, try again"


def main():
    book.start()
    print(help())
    while True:
        command = input("Enter your command > ")
        if not command:
            continue
        ret_code = parser(command)
        if ret_code == "Good bye!":
            print("Good bye, and have a nice day!")
            break
        elif ret_code:
            print(ret_code)


if __name__ == "__main__":
    main()
