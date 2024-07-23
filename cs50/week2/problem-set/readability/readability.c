#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

// Function definition
double coleman_liau_index(int a, int b, int c);
int count_letters(string x), count_words(string x), count_sentences(string x);
int grade_level(double a);

// Main variable declaration
double index;
float l, s;
int i, ep;
int number_of_letters, number_of_words, number_of_sentences;
string text;

// Main function
int main(void)
{
    // User input
    text = get_string("Text: ");

    // Counting letters
    count_letters(text);

    // Counting words
    count_words(text);

    // Counting sentences
    count_sentences(text);

    // Index calculation
    coleman_liau_index(number_of_letters, number_of_words, number_of_sentences);

    // Printing grade level
    grade_level(index);
}

//Letter-counting function
int count_letters(string x)
{
    for (i = 0, ep = strlen(text); i < ep; i++)
    {
        if (isalpha(text[i]))
        {
            number_of_letters++;
        }
    }
    return 0;
}

//Word-counting function
int count_words(string x)
{
    number_of_words++;
    for (i = 0, ep = strlen(text); i < ep; i++)
    {
        if (isspace(text[i]))
        {
            number_of_words++;
        }
    }
    return 0;
}

//Sentence-counting function
int count_sentences(string x)
{
    for (i = 0, ep = strlen(text); i < ep; i++)
    {
        if ((text[i] == '.') || (text[i] == '!') || (text[i] == '?'))
        {
            number_of_sentences++;
        }
    }
    return 0;
}

double coleman_liau_index(int a, int b, int c)
{
    l = (double) number_of_letters / number_of_words * 100;
    s = (double) number_of_sentences / number_of_words * 100;
    index = round(0.0588 * l - 0.296 * s - 15.8);
    return 0;
}

int grade_level(double a)
{
    if (index > 1)
    {
        if (index < 16)
        {
            printf("Grade %.0lf\n", index);
        }
        else
        {
            printf("Grade 16+\n");
        }
    }
    else
    {
        printf("Before Grade 1\n");
    }
    return 0;
}