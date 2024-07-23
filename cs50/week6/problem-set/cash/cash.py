from cs50 import get_float

QUARTER = 25
DIME = 10
NICKEL = 5
PENNY = 1

quartersUsed = 0
dimesUsed = 0
nickelsUsed = 0
penniesUsed = 0

while True:
    changeInDollars = get_float("Please enter the required amount of change: ")
    if (changeInDollars > 0.0):
        break

changeInCents = changeInDollars * 100

while QUARTER <= changeInCents:
    changeInCents -= QUARTER
    quartersUsed += 1

while DIME <= changeInCents:
    changeInCents -= DIME
    dimesUsed += 1
    
while NICKEL <= changeInCents:
    changeInCents -= NICKEL
    nickelsUsed += 1

while PENNY <= changeInCents:
    changeInCents -= PENNY
    penniesUsed += 1
    
totalCoinsUsed = quartersUsed + dimesUsed + nickelsUsed + penniesUsed

print(f"{totalCoinsUsed}")