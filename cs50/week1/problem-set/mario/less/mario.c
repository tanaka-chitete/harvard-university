#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // Variable declaration
    int h, i, j, k;
    // Height input from user
    do
    {
        h = get_int("Enter a unit height for the pyramid: ");
    }
    while (h < 1 || h > 8);
    
    for (i = 1; i <= h; i++)
    {
        // Print spaces to right-align
        for (k = 1; k <= h - i; k++)
        {
            printf(" ");
        }
        
        // Print '#' on each line 
        for (j = 1; j <= i; j++)
        {
            printf("#");
        }
        // Print new line
        printf("\n");
    }
}
