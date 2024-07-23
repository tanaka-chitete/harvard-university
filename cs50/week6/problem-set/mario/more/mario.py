from cs50 import get_int

while True:
    h = get_int("Enter a unit height for the pyramid: ")
    if (h >= 1 and h <= 8):
        break

# Establishes number of lines to print to representing height
for i in range(h):
    
    # Right-aligned pyramid
    # Prints spaces on each line to right-align first pyramid
    for j in range((h - i) - 1):
        print(' ', end='')
    
    # Prints '#' on each line to construct right-aligned pyramid
    for k in range(i + 1):
        print('#', end='')

    # Prints two spaces to prepare constructing left-aligned pyramid
    print('  ', end='')
    
    # Left-aligned pyramid
    # Prints spaces on each line to right-align the pyramid
    for k in range(i + 1):
        print('#', end='')
    
    # Prints new line to prepare constructing next line of pyramids
    print()