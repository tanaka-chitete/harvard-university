// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>

#include "dictionary.h"

// Global variable declaration
unsigned int key;

// Global variable initialisation
unsigned int word_count = 0;

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
const unsigned int N = 26;

// Hash table
node *table[N];

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    // Hashing word input to determine which linked list to access
    hash(word);

    // Assigning traversing pointer to point at same node as head of list
    node *traverse_cursor = table[key];

    while (traverse_cursor != NULL)
    {
        if (strcasecmp(word, traverse_cursor->word) == 0)
        {
            return true;
        }
        traverse_cursor = traverse_cursor->next;
    }
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    if (isupper(word[0]) == true)
    {
        return word[0] - 65;
    }
    return word[0] - 97;
}

// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // Declaring dictionary_input
    FILE *dictionary_input;

    // Attempting to open dictionary
    dictionary_input = fopen(dictionary, "r");

    // Exiting program upon unsuccessful retrieval
    if (dictionary_input == NULL)
    {
        return false;
    }

    // Declaring buffer
    char buffer[LENGTH + 1];

    // Scanning words into hashtable
    while (fscanf(dictionary_input, "%s", buffer) == 1)
    {
        // Allocating memory to store node
        node *new_node = malloc(sizeof(node));

        // Exiting program upon unsuccessful retrieval
        if (new_node == NULL)
        {
            return false;
        }

        // Copying word from buffer into node
        strcpy(new_node->word, buffer);

        // Hashing word
        hash(new_node->word);

        // Adding new node to beginning of linked list
        new_node->next = table[key];
        table[key] = new_node;

        // Incrementing dictionary word count
        word_count++;

        // Calling size to return dictionary word count
        size();
    }

    // Closing dictionary
    fclose(dictionary_input);

    // Exiting program upon successful retrieval
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    return word_count;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    for (int i = 0; i < N; i++)
    {
        node *lead_cursor = table[i];
        node *trail_cursor = lead_cursor;

        while (lead_cursor != NULL)
        {
            lead_cursor = lead_cursor->next;
            free(trail_cursor);
            trail_cursor = lead_cursor;
        }
    }
    return true;
}