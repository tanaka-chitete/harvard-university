#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Function definition
string encipher_plaintext(string a);

// Variable declaration
int k;
string plaintext, ciphertext;

int main(int argc, string argv[])
{
    // Checking if number of arguments is two
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    // Checking if second argument is a digit
    else;
    {
        for (int i = 0, ep = strlen(argv[1]); i < ep; i++)
        {
            if (isdigit(argv[1][i]) == false)
            {
                printf("Usage: ./caesar key\n");
                return 1;
            }
        }
    }
    // Converting second argument to an integer
    k = atoi(argv[1]);

    // Prompting user for plaintext (input)
    plaintext = get_string("plaintext: ");

    // Enciphering and printing plaintext
    encipher_plaintext(plaintext);
}

string encipher_plaintext(string a)
{
    printf("ciphertext: ");
    for (int i = 0, ep = strlen(plaintext); i < ep; i++)
    {
        if (isalpha(plaintext[i]))
        {
            if (isupper(plaintext[i]))
            {
                // Converting ASCII to alphabetical index
                plaintext[i] -= 65;
                // Shifting characters by key
                plaintext[i] = (plaintext[i] + k) % 26;
                // Converting ASCII back to alphabetical index
                plaintext[i] += 65;
                // Changing (or preserving) case
                plaintext[i] = toupper(plaintext[i]);
                // Printing characters
                printf("%c", plaintext[i]);
            }
            else
            {
                // Converting ASCII to alphabetical index
                plaintext[i] -= 97;
                // Shifting characters by key
                plaintext[i] = (plaintext[i] + k) % 26;
                // Converting ASCII back to alphabetical index
                plaintext[i] += 97;
                // Changing (or preserving) case
                plaintext[i] = tolower(plaintext[i]);
                // Printing characters
                printf("%c", plaintext[i]);
            }
        }
        else
        {
            printf("%c", plaintext[i]);
        }
    }
    printf("\n");
    return 0;
}