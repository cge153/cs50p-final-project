import csv
import os
import random
import string

import cryptocode
import pytest

from mpm import get_database_names
from mpm import create_random_password
from mpm import create_empty_database
from mpm import save_database
from mpm import open_database
from mpm import delete_database


@pytest.fixture
def random_string() -> str:
    return "".join(random.sample(string.ascii_lowercase, 10))


@pytest.fixture
def db_extension() -> str:
    return ".mpmdb"


@pytest.fixture
def password_row() -> list[str]:
    return ["1", "Hogwarts Students Online", "ron.weasley@magic.wiz", "iLuvCakes123!"]


@pytest.fixture
def min_pwd_length() -> int:
    return 5


@pytest.fixture
def default_pwd_length() -> int:
    return 10


@pytest.fixture
def pwd_length() -> int:
    return 9


@pytest.fixture
def count_lower_case() -> int:
    return 3


@pytest.fixture
def count_other() -> int:
    return 2


def test_get_database_names_contains_name(random_string, db_extension) -> None:
    # Create an empty test file. This should be in the returned list.
    random_db_file_name: str = random_string + db_extension
    with open(random_db_file_name, "w") as file:
        file.write("")

    # Test the function
    db_names: list[str] = get_database_names()
    assert random_string in db_names

    # Delete test file
    if os.path.exists(random_db_file_name):
        os.remove(random_db_file_name)


def test_get_database_names_empty_list(random_string) -> None:
    # A random extension name ensures that no such files are found
    random_file_extension: str = "." + random_string

    # Test the function
    db_names: list[str] = get_database_names(random_file_extension)
    assert len(db_names) == 0


def test_create_random_password_length(pwd_length) -> None:
    assert len(create_random_password(pwd_length)) == pwd_length


def test_create_random_password_minimum_length(min_pwd_length) -> None:
    assert len(create_random_password(1)) == min_pwd_length


def test_create_random_password_default_length(default_pwd_length) -> None:
    assert len(create_random_password()) == default_pwd_length


def test_create_random_password_contains_lower_case(pwd_length, count_lower_case) -> None:
    pwd: str = create_random_password(pwd_length)
    lower_case_characters: list[str] = [
        char for char in pwd if char in string.ascii_lowercase]

    assert len(lower_case_characters) == count_lower_case


def test_create_random_password_contains_upper_case(pwd_length, count_other) -> None:
    pwd: str = create_random_password(pwd_length)
    upper_case_characters: list[str] = [
        char for char in pwd if char in string.ascii_uppercase]

    assert len(upper_case_characters) == count_other


def test_create_random_password_contains_digits(pwd_length, count_other) -> None:
    pwd: str = create_random_password(pwd_length)
    digit_characters: list[str] = [
        char for char in pwd if char in string.digits]

    assert len(digit_characters) == count_other


def test_create_random_password_contains_punctuation(pwd_length, count_other) -> None:
    pwd: str = create_random_password(pwd_length)
    punctuation_characters: list[str] = [
        char for char in pwd if char in string.punctuation]

    assert len(punctuation_characters) == count_other


def test_create_empty_database_file_created(random_string, db_extension):
    db_file: str = random_string + db_extension
    create_empty_database(random_string, random_string)
    
    with open(db_file) as file:
        file_reader = csv.reader(file)
        password_rows: list[list[str]] = [row for row in file_reader]
    
    assert cryptocode.decrypt(password_rows[0][0], random_string) == "index"
    
    if os.path.exists(db_file):
        os.remove(db_file)
    
    
def test_create_empty_database_raises_file_exists_error(random_string, db_extension):
    db_file: str = random_string + db_extension
    with open(db_file, "w") as file:
        file.write("")
    
    with pytest.raises(FileExistsError):
        create_empty_database(random_string, random_string)
    
    if os.path.exists(db_file):
        os.remove(db_file)


def test_save_database_contains_row_data(random_string, db_extension, password_row):
    db_file: str = random_string + db_extension
    save_database(random_string, random_string, [password_row])
    
    with open(db_file, "r") as file:
        file_reader = csv.reader(file)
        password_rows_encrypted: list[list[str]] = [row for row in file_reader]
    
    assert cryptocode.decrypt(password_rows_encrypted[0][0], random_string) == password_row[0]
    assert cryptocode.decrypt(password_rows_encrypted[0][1], random_string) == password_row[1]
    assert cryptocode.decrypt(password_rows_encrypted[0][2], random_string) == password_row[2]
    
    if os.path.exists(db_file):
        os.remove(db_file)


def test_open_database_returns_correct_data(random_string, db_extension, password_row):
    db_file: str = random_string + db_extension
    test_data_rows = [["index", "title", "username", "password"], password_row]
    with open(db_file, "w") as file:
        file_writer = csv.writer(file)
        for row in test_data_rows:
            file_writer.writerow([cryptocode.encrypt(column, random_string) for column in row])
    password_rows: list[list[str]] = open_database(random_string, random_string)
    
    assert password_rows[0][0] == "index"
    assert password_rows[0][1] == "title"
    assert password_rows[0][2] == "username"
    assert password_rows[0][3] == "password"
    assert password_rows[1][0] == password_row[0]
    assert password_rows[1][1] == password_row[1]
    assert password_rows[1][2] == password_row[2]
    assert password_rows[1][3] == password_row[3]
    
    if os.path.exists(db_file):
        os.remove(db_file)
    
    
def test_open_database_raises_file_not_found_error(random_string, db_extension):
    with pytest.raises(FileNotFoundError):
        open_database(random_string, random_string)
    
    
def test_open_database_raises_value_error(random_string, db_extension):
    db_file: str = random_string + db_extension
    with open(db_file, "w") as file:
        file_writer = csv.writer(file)
        file_writer.writerow(["index", "title", "username", "password"])
    
    with pytest.raises(ValueError):
        open_database(random_string, random_string)
    
    if os.path.exists(db_file):
        os.remove(db_file)


def test_delete_database_file_deleted(random_string, db_extension):
    db_file: str = random_string + db_extension
    with open(db_file, "w") as file:
        file.write("")
    
    delete_database(random_string)
    
    assert not os.path.exists(random_string + db_extension)    


def test_delete_database_file_not_found_error(random_string):
    with pytest.raises(FileNotFoundError):
        delete_database(random_string)
