# MAGIC PASSWORD MANAGER

**Video Demo:**  <https://youtu.be/wjlhNX3-SVA>

## Project Files

The file `project.py` contains all functions required to execute the program. This program is described in detail in the below sections.

The test file `test_project.py` contains test functions for all functions in `project.py` with the exception of `parse_program_args()`, for which I felt a test is not necessary since it only instantiates an `argparse` parser.

## Overview

My final project for **CS50P** is titled **Magic Password Manger**. It is a command line program that allows a user to store password information in csv files, which are refered to as *databases* in the program. The first row of a csv file contains the names of the columns and the other rows contain the corresponding password information, i.e. one password entry per row. Each "cell" is encrypted / decrpyted with a *master password*, which the user must provide.

## Subcommands

The program is controlled by providing subcommands, which allow the user to only perform one action at a time. If, for example, a user wanted to open a database, the user could first execute `project.py list-db` to view the available databases and then `project.py open-db --database DB_NAME` to open and display the chosen database file.

### list-db

`project.py list-db`

The `list-db` subcommand displays the names of all files in the current working directory that match the pattern `*.mpmdb`, which is an acronym for `m`agic `p`assword `m`anager `db`. The file extension is omitted in that list.

### open-db

`project.py open-db --database DB_NAME`

The `open-db` subcommand reads an existing csv file, decrypts each cell with the provided master password and displays the information in a table. After decryption, the validity of the master password is verfified by evaluating if the first cell of the header contains the string `index`, which would not be the case if the cells where decrypted with a wrong master password.

### create-db

`project.py create-db --database DB_NAME`

The `create-db` subcommand creates an "empty" csv file, which only contains the header row (`index`, `title`, `username`, `password`). The header cells are encrypted with the master password provided by the user.

### delete-db

`project.py delete-db --database DB_NAME`

The `delete-db` subcommand deletes a csv file.

### add

`project.py add --database DB_NAME --title TITLE --username USERNAME --password-length LENGTH`

The `add` subcommand allows the user to add a password entry (i.e. row) to an existing csv file. A random password is created automatically with the length provided as a command line argument. The `title` and `username` also need to be provided as arguments, whereas the `index` is simply the next index number.

The random password always contains characters of the four groups "lower case letters", "upper case letters", "digits" and "punctuation". The count of characters of each of these groups is calculated as follows:

```python
# Upper case, Digits, Punctuation:
password_length // 4

# Lower case:
password_length // 4 + password_length % 4
```

### remove

`project.py remove --database DB_NAME --index INDEX`

The `remove` subcommand allows the user to remove a password entry at a specific index.

## Design Choices

### Menu vs Command Line

My first idea was to display a main menu and a "page" for each of the subcommands, allowing the user to navigate between the subcommands or to exit the program by entering the appropriate option number. After several coding sessions the program had a basic functionality that would allow a user to navigate between the *main* menu and the *list* menu and also display the appropriate information for the current "page". However, storing the *state* of the program (current page / subcommand, options for that subcommand, data) and displaying the appropriate data and options got more and more complicated. Progress slowed down significantly and that's where I decided to simplify my project by allowing the user to control the program via command line arguments instead.
