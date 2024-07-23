import csv
import sys
from cs50 import SQL

# Executes if incorrect number of command line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python import.py [csv file]")
# Executes if correct number of arguments is provided
else:
    # Connects to students.db database
    db = SQL("sqlite:///students.db")
    
    # Opens csv file given by second command line argument
    csv_reader = csv.DictReader(open(sys.argv[1]))

    # Copies row from source csv file into student buffer
    for row in csv_reader:
        student = row

        # Splits the student's full name;
        # into their first, middle (where applicable) and last names
        student["name"] = student["name"].split()

        # Inserts None into middle name entry;
        # if the student doesn't have a middle name
        if len(student["name"]) == 2:
            student["name"].insert(1, None)

        # Query for inserting values into first, middle, last, house and birth;
        # columns of the students database
        query = "INSERT INTO students (first, middle, last, house, birth) " + \
                "VALUES (%s, %s, %s, %s, %s)"

        # Values to be substituted into query;
        # representing the student's first, (middle) and last names;
        # house and date of birth, respectively
        values = student["name"][0], student["name"][1], student["name"][2], \
            student["house"], student["birth"]

        # Adds student into students database
        db.execute(query, values)