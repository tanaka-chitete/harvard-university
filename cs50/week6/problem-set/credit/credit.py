# FILE: Credit
# CREATOR: Tanaka Chitete
# PURPOSE: Validate a credit card implementing Luhn's algorithm
# CREATION: 28/04/2020
# LATEST MODIFICATION: 28/04/2020

from cs50 import get_string

def main():
    cardNum = get_string("Payment card number: ")
    
    cardNum_len = len(cardNum)
    
    # Executes if user input (i.e. 'credit card') is between 13 and 16 digits
    if (13 <= cardNum_len) and (cardNum_len <= 16):
        # Obtains reverse of cardNum
        cardNumRev = cardNum[::-1]

        # Obtains sum of multiplying every other digit from second-to-last by 2
        multDigs_sum = multDigs(cardNumRev, cardNum_len)
        
        # Obtains sum of adding every other digit from last
        addDigs_sum = addDigs(cardNumRev, cardNum_len)
        
        sumTotal = multDigs_sum + addDigs_sum
        
        # Obtains last digit of sumTotal
        sumTotal_digLast = sumTotal % 10
        
        # Executes if last digit of sumTotal is 0
        if sumTotal_digLast == 0:
            # Obtains first and second digits of cardNum
            cardNum_digOne = int(cardNum[0])
            cardNum_digTwo = int(cardNum[1])
            
            # Outputs card type
            outCardType(cardNum_len, cardNum_digOne, cardNum_digTwo)
        # Executes if last digit of sumTotal is not 0
        else:
            print("INVALID")
    # Executes if user input is less than 13 or greater than 16 digits
    else:
        print("INVALID")

# NAME: multDigs
# IMPORT: cardNumRev (str), cardNum_len (int)
# EXPORT: multDigs_sum (int)
# PURPOSE: Return sum of multiplying every other digit from second to-last by 2
# CREATION: 28/04/2020
# LATEST MODIFICATION: 28/04/2020
def multDigs(cardNumRev, cardNum_len):
    multDigs_sum = 0
    for i in range(1, cardNum_len, +2):
        prod = int(cardNumRev[i]) * 2
        
        # Executes if prod is greater than 9
        if prod > 9:
            prodDigOne = prod // 10
            prodDigTwo = prod % 10
            
            multDigs_sum += prodDigOne + prodDigTwo
        # Executes if prod is less than 9
        else:
            multDigs_sum += prod
            
    return multDigs_sum
    
# NAME: addDigs
# IMPORT: cardNumRev (str), cardNum_len (int)
# EXPORT: addDigs_sum (int)
# PURPOSE: Return sum of adding every other digit from last
# CREATION: 28/04/2020
# LATEST MODIFICATION: 28/04/2020
def addDigs(cardNumRev, cardNum_len):
    addDigs_sum = 0
    for i in range(0, cardNum_len, +2):
        addDigs_sum += int(cardNumRev[i])
        
    return addDigs_sum
    
# NAME: outCardType
# IMPORT: cardNum_len (int), cardNum_digOne (int), cardNum_digTwo(int)
# EXPORT: none
# PURPOSE: Output type of card
# CREATION: 28/04/2020
# LATEST MODIFICATION: 28/04/2020
def outCardType(cardNum_len, cardNum_digOne, cardNum_digTwo):
    # Executes if type is American Express
    if cardNum_digOne == 3 and \
       (cardNum_digTwo == 4 or cardNum_digTwo == 7) and \
       cardNum_len == 15:
        print("AMEX")
    # Executes if type is Mastercard
    elif cardNum_digOne == 5 and \
         (1 <= cardNum_digTwo and cardNum_digTwo <= 5) and \
         cardNum_len == 16:
        print("MASTERCARD")
    # Executes if type is Visa
    elif cardNum_digOne == 4 and \
         (cardNum_len == 13 or cardNum_len == 16):
        print("VISA")
    # Executes if type is invalid
    else:
        print("INVALID")
        
        
        
if __name__ == "__main__":
    main()