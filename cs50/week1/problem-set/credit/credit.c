// FILE: Credit
// CREATOR: Tanaka Chitete
// PURPOSE: Validate a credit card using Luhn's algorithm
// CREATION DATE: 24/04/2020
// LATEST MODIFICATION DATE: 25/04/2020

#include <cs50.h>
#include <stdio.h>

int separateDigits(long cardNum, int cardDigs[19]);
int multiplyDigits(int cardDigs[19], int numOfDigs);
int addDigits(int cardDigs[19], int numOfDigs);
int identifyCard(int digOne, int digTwo, int numOfDigs, 
                 int sumLastDig);
void outputCardType(int cardID);

int main(void)
{
    // main variables
    long cardNum;
    int sumTotal, cardDigOne, cardDigTwo, cardID, 
        sumTotalLastDig;

    // Return value assignment variables
    int numOfDigs, sumFromMultiplyDigits, sumFromAddDigits;
    
    cardNum = get_long("Payment card number: ");

    int cardDigs[19];

    // Separates card number into its digits (in reverse order)
    numOfDigs = separateDigits(cardNum, cardDigs);

    if((13 <= numOfDigs) && (numOfDigs <= 16))
    {
        // Sum of multiplying each digit from second-to-last by 2
        sumFromMultiplyDigits = multiplyDigits(cardDigs, numOfDigs);

        // Sum of adding each digit from last
        sumFromAddDigits = addDigits(cardDigs, numOfDigs);

        sumTotal = sumFromMultiplyDigits + sumFromAddDigits;

        // Obtains first and second digits of the credit card for 
        // verification purposes
        cardDigOne = cardDigs[numOfDigs - 1];
        cardDigTwo = cardDigs[numOfDigs - 2];

        // Obtains last digit of sumTotal for verification purposes
        sumTotalLastDig = sumTotal % 10;

        // Obtains ID of card for verification purposes        
        cardID = identifyCard(cardDigOne, cardDigTwo, numOfDigs, 
                              sumTotalLastDig);

        outputCardType(cardID);
    }
    else
    {
        printf("INVALID\n");
    }   
}

// NAME: separateDigits
// IMPORT: cardNum (int), cardDigs (int),  
// EXPORT: numOfDigs (int)
// PURPOSE: Separate digits and store them in array in reverse
// CREATION DATE: 24/04/2020
// LATEST MODIFICATION DATE: 24/04/2020

int separateDigits(long cardNum, int cardDigs[19])
{
    long cardDig;
    int i, numOfDigs;

    i = 0;
    // Loops through each digit of credit card number
    while(cardNum != 0)
    {
        // Obtains current last digit
        cardDig = cardNum % 10;

        cardDigs[i] = cardDig;

        numOfDigs = i + 1;

        // Removes current last digit
        cardNum = cardNum / 10;
        i = i + 1;
    }
    return numOfDigs;
}

// NAME: multiplyDigits
// IMPORT: cardDigs (int), numOfDigs (int)
// EXPORT: sum (int)
// PURPOSE: Calculate sum of every other digit from second-to-last
//          multiplied by two
// CREATION DATE: 24/04/2020
// LATEST MODIFICATION DATE: 25/04/2020

int multiplyDigits(int cardDigs[19], int numOfDigs)
{
    int sum, product, productDigOne, productDigTwo;

    sum = 0;
    for(int i = 1; i < numOfDigs; i += 2)
    {
        product = cardDigs[i] * 2;

        // Splits product into first and second digits if it is too
        // large
        if(product > 9)
        {
            productDigOne = product / 10;
            productDigTwo = product % 10;

            sum = sum + productDigOne + productDigTwo;
        }
        else
        {
            sum = sum + product;
        }
    }
    return sum;
}

// NAME: addDigits
// IMPORT: cardDigs (int), numOfDigs (int)
// EXPORT: sum (int)
// PURPOSE: Calculate sum of every other digit from last
// CREATION DATE: 24/04/2020
// LATEST MODIFICATION DATE: 25/04/2020

int addDigits(int cardDigs[19], int numOfDigs)
{
    int sum;

    sum = 0;
    for(int i = 0; i < numOfDigs; i += 2)
    {
        sum = sum + cardDigs[i];
    }
    return sum;
}

// NAME: identifyCard
// IMPORT: digOne (int), digTwo, numOfDigs (int), sumLastDig (int)
// EXPORT: cardID (int)
// PURPOSE: Card will be identified as either an AMEX, Mastercard
//          or Visa card, otherwise invalid
// CREATION DATE: 25/04/2020
// LATEST MODIFICATION DATE: 25/04/2020

int identifyCard(int digOne, int digTwo, int numOfDigs, 
                 int sumLastDig)
{
    int cardID;

    cardID = 0;
    // Identifies if card is an AMEX card
    if((digOne == 3) &&     
       ((digTwo == 4) || (digTwo == 7)) &&   
       (numOfDigs == 15) &&     
       (sumLastDig == 0))
    {
        cardID = 1;
    }
    // Identifies if card is a Mastercard card
    else if((digOne == 5) && 
            ((1 <= digTwo) && (digTwo <= 5)) && 
            (numOfDigs == 16) && 
            (sumLastDig == 0))
    {
        cardID = 2;
    }
    // Identifies if card is a Visa card
    else if((digOne == 4) && 
            ((numOfDigs == 13) || (numOfDigs == 16)) && 
            (sumLastDig == 0))
    {
        cardID = 3;
    }
    return cardID;
}

// NAME: outputCardType
// IMPORT: cardID (int)
// EXPORT: none
// PURPOSE: Card input will have its outputted
// CREATION DATE: 25/04/2020
// LATEST MODIFICATION DATE: 25/04/2020

void outputCardType(int cardID)
{
    switch(cardID)
    {
        case 1:
            printf("AMEX\n");
            break;
        case 2:
            printf("MASTERCARD\n");
            break;
        case 3:
            printf("VISA\n");
            break;
        default:
            printf("INVALID\n");
            break;
    }
}
