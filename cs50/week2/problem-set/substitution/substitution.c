/*
NAME: substitution
CREATOR: Tanaka Chitete
PROBLEM_SET: 2
PURPOSE: Implement a substitution cipher on input text given a cipher key
CREATION: 08/08/2020
LAST MODIFICATION: 08/08/2020
*/

#include <cs50.h>
#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>

// Program constants
const int CIPHER_KEY_LENGTH = 26;
const int UPPERCASE_A_ASCII = 65;
const int LOWERCASE_A_ASCII = 97;

// Function prototypes
bool validateAlphaOnly(string cipherKey);
string toUpperCipherKey(string cipherKey);
bool validateUniqueOnly(string cipherKey);
void calcCharKeys(string cipherKey, int charKeys[]);
string encipher(string plaintext, int charKeys[]);

int main(int argc, string argv[])
{
    string cipherKey = argv[1];

    // Executes if incorrect number of commandline arguments was provided
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    // Executes if provided key is not 26 characters in length
    if (strlen(cipherKey) != CIPHER_KEY_LENGTH)
    {
        printf("Key must be 26 characters in length\n");
        return 1;
    }

    // Executes if provided key consists of non-alphabet characters
    if (!validateAlphaOnly(cipherKey))
    {
        printf("Cipher key must consist of only alphabetic characters\n");
        return 1;
    }

    cipherKey = toUpperCipherKey(cipherKey);

    // Executes if provided key consists of repeated alphabetic characters
    if (!validateUniqueOnly(cipherKey))
    {
        printf("Cipher key must consist of non-repeated alphabetic characters\n");
        return 1;
    }

    // Calculates keys to shift each character in alphabet to cipher key
    // characters
    int charKeys[CIPHER_KEY_LENGTH];
    calcCharKeys(cipherKey, charKeys);

    string plaintext = get_string("plaintext: ");

    // Enciphers plaintext given cipher key to formulate ciphertext
    string ciphertext = encipher(plaintext, charKeys);
    printf("ciphertext: %s\n", ciphertext);

    return 0;
}

/*
NAME: validateAlphaOnly
IMPORT: cipherKey (string)
EXPORT: alphaOnly (bool)
PURPOSE: Validate whether cipher key consists of only alphabetic characters
CREATION: 08/08/2020
LAST MODIFICATION: 08/08/2020
*/

bool validateAlphaOnly(string cipherKey)
{
    // Validates each character of cipher key as being alphabetic
    bool alphaOnly = true;
    int i = 0;
    while (alphaOnly && i < strlen(cipherKey))
    {
        if (!isalpha(cipherKey[i]))
        {
            alphaOnly = false;
        }
        i++;
    }
    return alphaOnly;
}

/*
NAME: toUpperCipherKey
IMPORT: cipherKey (string)
EXPORT: cipherKey (string)
PURPOSE: Convert each letter of cipher key to its uppercase counterpart
CREATION: 08/08/2020
LAST MODIFICATION: 08/08/2020
*/

string toUpperCipherKey(string cipherKey)
{
    // Converts each letter of cipher key to its uppercase counterpart
    for (int i = 0; i < strlen(cipherKey); i++)
    {
        if (islower(cipherKey[i]))
        {
            cipherKey[i] = toupper(cipherKey[i]);
        }
    }
    return cipherKey;
}

/*
NAME: validateUniqueOnly
IMPORT: cipherKey (string)
EXPORT: uniqueOnly (bool)
PURPOSE: Validate whether cipher text consists of only unique characters
CREATION: 08/08/2020
LAST MODIFICATION: 08/08/2020
*/

bool validateUniqueOnly(string cipherKey)
{
    int counts[26] = {0};

    // Validates each character as being unique
    int i = 0;
    bool uniqueOnly = true;
    int charIndex;
    while (uniqueOnly && i < CIPHER_KEY_LENGTH)
    {
        charIndex = (int)cipherKey[i] - UPPERCASE_A_ASCII;
        if (counts[charIndex] == 0)
        {
            counts[charIndex]++;
        }
        else
        {
            uniqueOnly = false;
        }
        i++;
    }
    return uniqueOnly;
}

/*
NAME: calcCharKeys
IMPORT: cipherKey (string), charKeys[] (int)
EXPORT: none
PURPOSE: Calculate key to shift each character of the alphabet based on the
         cipher key
CREATION: 08/08/2020
LAST MODIFICATION: 08/08/2020
*/

void calcCharKeys(string cipherKey, int charKeys[])
{
    int cipherKeyASCII, alphaASCII;

    // Calculates key to shift each character
    for (int i = 0; i < CIPHER_KEY_LENGTH; i++)
    {
        cipherKeyASCII = (int)cipherKey[i];
        alphaASCII = i + UPPERCASE_A_ASCII;
        charKeys[i] = cipherKeyASCII - alphaASCII;
    }
}

/*
NAME: encipher
IMPORT: plaintext (string), charKeys[] (int)
EXPORT: plaintext (string)
PURPOSE: Encipher plaintext based on cipher key to formulate ciphertext
CREATION: 08/08/2020
LAST MODIFICATION: 08/08/2020
*/

string encipher(string plaintext, int charKeys[])
{
    int asciiToI;

    // Enciphers each letter of plaintext based on cipher key
    for (int i = 0; i < strlen(plaintext); i++)
    {
        if (isalpha(plaintext[i]))
        {
            // Lowercase key (97)
            asciiToI = LOWERCASE_A_ASCII;
            // Executes if current letter is uppercase
            if (isupper(plaintext[i]))
            {
                // Uppercase key (65)
                asciiToI = UPPERCASE_A_ASCII;
            }

            // Subtracts either 65 or 97 for uppercase or lowercase letters,
            // respectively, from letter in plain text to align indices of
            // plaintext and charKeys;
            plaintext[i] -= asciiToI;
            // Adds (or subtracts) key for character
            plaintext[i] += charKeys[(int)plaintext[i]];
            // Adds back either 65 or 97 to complete encipher
            plaintext[i] += asciiToI;
        }
    }
    return plaintext;
}