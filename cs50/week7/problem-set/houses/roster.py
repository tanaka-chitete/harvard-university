import sys
from cs50 import SQL

# Executes if incorrect number of command line arguments is provided
if len(sys.argv) != 2:
    print("Usage: python roster.py [house]")
# Executes if correct number of arguments is provided
else:
    # Connects to students.db database
    db = SQL("sqlite:///students.db")
    
    house = sys.argv[1]
    
    # Query to retreive details of all students in given house
    query = "SELECT first, middle, last, birth FROM students WHERE house = " + \
            "'" + house + "'" + "ORDER BY last, first"
    
    # Executes query to retreive student details
    students = db.execute(query)
    
    # Prints each student's details formatted as first, (middle) and last name
    # and birth year, respectively
    for row in range(len(students)):
        # Prints student's first name
        print(f"{students[row]['first']}", end=" ")
        
        # Prints student's middle name (where applicable)
        if students[row]['middle'] != None:
            print(f"{students[row]['middle']}", end=" ")
            
        # Prints student's last name
        print(f"{students[row]['last']}", end=", ")
        
        # Prints student's birth year
        print(f"born {students[row]['birth']}")