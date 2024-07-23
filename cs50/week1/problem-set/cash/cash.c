#include <cs50.h>
#include <stdio.h>
#include <math.h>

int main(void)
{
    // Variable declaration
    float change_in_dollars, change_in_cents;
    int quarters_used, dimes_used, nickels_used, pennies_used, total_coins_used; 
    
    // Change input in dollars
    do
    {
        change_in_dollars = get_float("Enter required amount of change: ");
    }
    while (change_in_dollars < 0.00);
    
    // Change input in dollars converted to cents
    change_in_cents = round(change_in_dollars * 100);
    
    // Quarters
    for (quarters_used = 0; 25 <= change_in_cents; quarters_used++)
    {
        change_in_cents -= 25;
    }
    
    // Dimes
    for (dimes_used = 0; 10 <= change_in_cents; dimes_used++)
    {
        change_in_cents -= 10;
    }
    
    // Nickels
    for (nickels_used = 0; 5 <= change_in_cents; dimes_used++)
    {
        change_in_cents -= 5;
    }
    
    // Pennies
    for (pennies_used = 0; 1 <= change_in_cents; pennies_used++)
    {
        change_in_cents -= 1;
    }
    
    // Total coins used
    total_coins_used = quarters_used +
                       dimes_used +
                       nickels_used +
                       pennies_used;
    
    printf("Total coins used: %i\n", total_coins_used);
}
