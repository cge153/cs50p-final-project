"""Magic Password Manager: A Password management program.

This program allows a user to create passwords and store them in a csv file.
The content of the csv file is encrypted / decrypted with a master password.
New passwords are created using characters from lower case and upper case
letters, numbers and punctuation characters.

    Typical usage examples:
    
    project.py list-db
    project.py create-db --database magicpwds
    project.py open-db -d magicpwds
    project.py delete-db -d magicpwds
    project.py add -d magicpwds -t "Hogwarts Students Magic Web" -u ron1980ash -l 10
    project.py remove -d magicpwds -i 7
"""


import argparse
import csv
import getpass
import glob
import os
import random
import string
import sys

import cryptocode
import tabulate


def main():
    PROMPT_MASTER_PWD = "Please enter master password: "
    PROMPT_MASTER_PWD_NEW = "Please enter a master password for the new database: "
    PROMPT_MASTER_PWD_REPEAT = "Please repeat the master password: "
    
    args: argparse.Namespace = parse_program_args()
 
    if args.command == "list-db":
        db_names: list[str] = get_database_names()
        
        if len(db_names) == 0:
            sys.exit("No database files found. You can use the 'create-db' subcommand to create a database.\n")

        print("\n".join(db_names), "\n")

    elif args.command == "create-db":
        while True:
            master_pwd: str = getpass.getpass(prompt=PROMPT_MASTER_PWD_NEW)
            master_pwd_repeat: str = getpass.getpass(prompt=PROMPT_MASTER_PWD_REPEAT)
            if master_pwd == master_pwd_repeat:
                break
            else:
                print("The passwords did not match, please try again!\n")

        try:
            create_empty_database(args.database, master_pwd)
            print("Database created successfully.")
        except FileExistsError as err:
            sys.exit(f"Error: {err}")
        except Exception as err:
            sys.exit(f"Unexpected Error: {err}")
        
    elif args.command == "open-db":
        master_pwd: str = getpass.getpass(PROMPT_MASTER_PWD)
        
        try:
            rows: list[list[str]] = open_database(args.database, master_pwd)
        except FileNotFoundError as err:
            sys.exit(f"Error: {err}")
        except ValueError as err:
            sys.exit(f"Error: {err}")
        except Exception as err:
            sys.exit(f"Unexpected Error: {err}")
        
        print(tabulate.tabulate(rows, headers="firstrow", tablefmt="rounded_outline"))
    
    elif args.command == "delete-db":
        try:
            delete_database(args.database)
            print("Database deleted successfully.")
        except FileNotFoundError:
            print(f"Error: {err}")
        except Exception as err:
            sys.exit(f"Unexpected Error: {err}")
    
    elif args.command == "add":
        master_pwd: str = getpass.getpass(PROMPT_MASTER_PWD)
        
        try:
            rows: list[list[str]] = open_database(args.database, master_pwd)
        except FileNotFoundError as err:
            sys.exit(f"Error: {err}")
        except ValueError as err:
            sys.exit(f"Error: {err}")
        except Exception as err:
            sys.exit(f"Unexpected Error: {err}")
        
        index: str = str(len(rows))
        password: str = create_random_password(args.password_length)
        rows.append([index, args.title, args.username, password])
        save_database(args.database, master_pwd, rows)
        
        print(tabulate.tabulate(rows, headers="firstrow", tablefmt="rounded_outline"))

    elif args.command == "remove":
        master_pwd: str = getpass.getpass(prompt=PROMPT_MASTER_PWD)
        
        try:
            rows: list[list[str]] = open_database(args.database, master_pwd)
        except FileNotFoundError as err:
            sys.exit(f"Error: {err}")
        except ValueError as err:
            sys.exit(f"Error: {err}")
        except Exception as err:
            sys.exit(f"Unexpected Error: {err}")
        
        if args.index not in range(1, len(rows)):
            sys.exit("Could not remove item: Invalid index\n")
        else:
            rows.pop(args.index)
            
            # Re-index rows
            for index, row in enumerate(rows):
                if index > 0:
                    row[0] = str(index)
            
            save_database(args.database, master_pwd, rows)
            print(tabulate.tabulate(rows, headers="firstrow", tablefmt="rounded_outline"))


def get_database_names(search_pattern: str = "*.mpmdb") -> list[str]:
    """Searches for files that match a pattern.

    Args:
        search_pattern (str, optional): The file search pattern. Defaults to "*.mpmdb".

    Returns:
        list[str]: A list of file names that match the pattern, without the file extension.
    """
    
    db_files: list[str] = glob.glob(search_pattern)
    db_names: list[str] = [db_file.split(".")[0] for db_file in db_files]
    return db_names


def create_empty_database(database: str, master_pwd: str) -> None:
    """Creates a csv file which only contains the header row.

    Args:
        database (str): The name of the database to be created.
        master_pwd (str): Password used for encrypting each cell item.

    Raises:
        FileExistsError: The database file already exists.
    """
    
    db_file: str = database + ".mpmdb"
    if os.path.exists(db_file):
        raise FileExistsError("A database with that name already exists")

    row_header = ["index", "title", "username", "password"]
    with open(db_file, "w") as file:
        file_writer = csv.writer(file)
        file_writer.writerow([cryptocode.encrypt(column, master_pwd) for column in row_header])


def open_database(database: str, master_pwd: str) -> list[list[str]]:
    """Opens an existing csv file.

    Args:
        database (str): The name of the database to open.
        master_pwd (str): Password used for decrypting each cell item.

    Raises:
        FileNotFoundError: The database file does not exist.
        ValueError: The password used for decrypting is incorrect.

    Returns:
        list[list[str]]: A list of rows containing the header row and rows with password information.
    """
    
    db_file: str = database + ".mpmdb"
    if not os.path.exists(db_file):
        raise FileNotFoundError("Database file not found")

    with open(db_file, "r") as file:
        file_reader = csv.reader(file)
        password_rows: list[list[str]] = [row for row in file_reader]

    password_rows_decrypted: list[list[str]] = []
    for row in password_rows:
        row_decrypted = [cryptocode.decrypt(column, master_pwd) for column in row]
        password_rows_decrypted.append(row_decrypted)
    
    if password_rows_decrypted[0][0] != "index":
        raise ValueError("Master password incorrect")
    
    return password_rows_decrypted
    
    
def save_database(database: str, master_pwd: str, rows: list[list[str]]) -> None:
    """Saves a list of rows to a csv file.

    Args:
        database (str): The name of the database to save to.
        master_pwd (str): Password used for encrypting each cell item.
        rows (list[list[str]]): A list of rows containing the header row and rows with password information.
    """
    
    db_file: str = database + ".mpmdb"
    with open(db_file, "w") as file:
        file_writer = csv.writer(file)
        for row in rows:
            file_writer.writerow([cryptocode.encrypt(column, master_pwd) for column in row])


def delete_database(database: str) -> None:
    """Deletes a csv file.

    Args:
        database (str): The name of the database to be deleted.

    Raises:
        FileNotFoundError: The database file does not exist.
    """
    
    db_file: str = database + ".mpmdb"
    if not os.path.exists(db_file):
        raise FileNotFoundError("Database file not found")
    os.remove(db_file)


def create_random_password(password_length: int = 10) -> str:
    """Creates a random password.
    
    The random password is created by using lower case and upper case letters,
    numbers and punctuation characters.

    Args:
        password_length (int, optional): The length of the password. Defaults to 10. Minimum is 5.

    Returns:
        str: The random pasword.
    """
    
    MINIMUM_LENGTH: int = 5
    
    if password_length < MINIMUM_LENGTH:
        password_length = MINIMUM_LENGTH
    
    # Determine how many characters to be used per group. The rest is added to the lower case group.
    count_characters_per_group: int = password_length // 4
    count_rest: int = password_length % 4

    # Add characters of each group to a single list and make that list random
    password_characters: list[str] = []
    password_characters += random.sample(string.ascii_lowercase, count_characters_per_group + count_rest)
    password_characters += random.sample(string.ascii_uppercase, count_characters_per_group)
    password_characters += random.sample(string.digits, count_characters_per_group)
    password_characters += random.sample(string.punctuation, count_characters_per_group)
    random.shuffle(password_characters)
    
    return "".join(password_characters)


def parse_program_args() -> argparse.Namespace:
    # Top-level parser
    parser = argparse.ArgumentParser(description="Magic Password Manager: Create and store passwords")
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand parsers
    subparsers.add_parser("list-db", help="list available databases")
    
    parser_create_db = subparsers.add_parser("create-db", help="create an empty database")
    parser_create_db.add_argument("-d", "--database", metavar="DB_NAME", type=str, help="database name (without file extenstion)", required=True)
    
    parser_open_db = subparsers.add_parser('open-db', help="open and display a database")
    parser_open_db.add_argument("-d", "--database", metavar="DB_NAME", type=str, help="database name (without file extenstion)", required=True)
    
    parser_delete_db = subparsers.add_parser("delete-db", help="delete a database")
    parser_delete_db.add_argument("-d", "--database", metavar="DB_NAME", type=str, help="database name (without file extenstion)", required=True)
    
    parser_add = subparsers.add_parser("add", help="add entry to an existing database")
    parser_add.add_argument("-d", "--database", metavar="DB_NAME", type=str, help="database name (without file extenstion)", required=True)
    parser_add.add_argument("-t", "--title", metavar="TITLE", type=str, help="title for password", required=True)
    parser_add.add_argument("-u", "--username", metavar="USERNAME", type=str, help="username used with password", required=True)
    parser_add.add_argument("-l", "--password-length", metavar="LENGTH", type=int, help="length of the random password")

    parser_remove = subparsers.add_parser("remove", help="remove entry from an existing database")
    parser_remove.add_argument("-d", "--database", metavar="DB_NAME", type=str, help="database name (without file extenstion)", required=True)
    parser_remove.add_argument("-i", "--index", metavar="INDEX", type=int, help="index of entry to be removed", required=True)

    return parser.parse_args()
    
    
if __name__ == "__main__":
    main()
