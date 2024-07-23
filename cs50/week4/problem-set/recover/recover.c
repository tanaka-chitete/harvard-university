#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

// Type definition
typedef uint8_t BYTE;

// Run-time variable declaration
BYTE buffer[512];
FILE *disk_image;
char file_name[8];
FILE *jpg;
size_t bytes_read;

// Run-time variable initialisation
int file_number = 0;
int total_bytes_written = 0;

int main(int argc, char *argv[])
{
    // Checking for valid usage
    if (argc != 2)
    {
        printf("Usage: ./recover image\n");
        return 1;
    }

    // Opening disk image
    disk_image = fopen(argv[1], "r");

    // Checking for lack of image
    if (disk_image == NULL)
    {
        printf("Error: cannot open file\n");
        return 1;
    }

    // Reading and writing disk image to jpeg files
    while ((bytes_read = fread(buffer, 1, 512, disk_image)) > 0)
    {
        // Checking for jpeg signiture and either writing first file or subsequent files
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            // Writing first block to first jpg file
            if (jpg == NULL)
            {
                sprintf(file_name, "%03i.jpg", file_number);
                jpg = fopen(file_name, "w");
                fwrite(buffer, 1, bytes_read, jpg);
                fclose(jpg);
            }
            // Writing first block to subsequent jpg file
            else
            {
                file_number++;
                sprintf(file_name, "%03i.jpg", file_number);
                jpg = fopen(file_name, "w");
                fwrite(buffer, 1, bytes_read, jpg);
                fclose(jpg);
            }
        }
        else
        {
            // Writing subsequent blocks to jpg file
            if (jpg != NULL)
            {
                jpg = fopen(file_name, "a");
                fwrite(buffer, 1, bytes_read, jpg);
                fclose(jpg);
            }
        }
    }
}