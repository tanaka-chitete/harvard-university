#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    int average_colour;

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Obtaining average RGB values of each pixel
            average_colour = round(((double) image[i][j].rgbtRed + (double) image[i][j].rgbtGreen + (double) image[i][j].rgbtBlue) / 3);

            // Setting RGB values to the same value (average_colour)
            image[i][j].rgbtRed = average_colour;
            image[i][j].rgbtGreen = average_colour;
            image[i][j].rgbtBlue = average_colour;
        }
    }
    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Applying sepia formula
            int sepia_red   = round((double) 0.393 * image[i][j].rgbtRed + (double) 0.769 * image[i][j].rgbtGreen +
                                    (double) 0.189 * image[i][j].rgbtBlue);
            int sepia_green = round((double) 0.349 * image[i][j].rgbtRed + (double) 0.686 * image[i][j].rgbtGreen +
                                    (double) 0.168 * image[i][j].rgbtBlue);
            int sepia_blue  = round((double) 0.272 * image[i][j].rgbtRed + (double) 0.534 * image[i][j].rgbtGreen +
                                    (double) 0.131 * image[i][j].rgbtBlue);

            // Checking if RGB values are above 255
            if (sepia_red > 255)
            {
                sepia_red = 255;
            }

            if (sepia_green > 255)
            {
                sepia_green = 255;
            }

            if (sepia_blue > 255)
            {
                sepia_blue = 255;
            }

            // Storing sepia values in 2d array of image
            image[i][j].rgbtRed   = sepia_red;
            image[i][j].rgbtGreen = sepia_green;
            image[i][j].rgbtBlue  = sepia_blue;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int sp = j;
            int ep = width - j - 1;

            if (sp < ep)
            {
                RGBTRIPLE temp = image[i][sp];
                image[i][sp] = image[i][ep];
                image[i][ep] = temp;
            }
            else
            {
                ;
            }
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temp_image[height][width];

    // Copying "image" to "temp_image"
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            temp_image[i][j] = image[i][j];
        }
    }

    // Blurring pixels
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Initialising counters
            int total_red = 0;
            int total_green = 0;
            int total_blue = 0;
            int total_pixels = 0;

            // Initialising colour averages
            BYTE avg_red;
            BYTE avg_green;
            BYTE avg_blue;

            // Iterating through 3x3 grid of surroundings of each pixel
            for (int k = i - 1, epk = i + 1; k <= epk; k++)
            {
                for (int l = j - 1, epl = j + 1; l <= epl; l++)
                {
                    // Checking if variable is not out of bounds
                    if (k < 0 || k >= height || l < 0 || l >= width)
                    {
                        continue;
                    }
                    // Incrementing counters upon successful verification
                    else
                    {
                        total_red += image[k][l].rgbtRed;
                        total_green += image[k][l].rgbtGreen;
                        total_blue += image[k][l].rgbtBlue;
                        total_pixels++;
                    }
                }
            }

            // Calculating average colours of pixel
            avg_red = round((double) total_red / (double) total_pixels);
            avg_green = round((double) total_green / (double) total_pixels);
            avg_blue = round((double) total_blue / (double) total_pixels);

            // Assigning "temp_image" the average colour
            temp_image[i][j].rgbtRed = avg_red;
            temp_image[i][j].rgbtGreen = avg_green;
            temp_image[i][j].rgbtBlue = avg_blue;
        }
    }

    // Copying "temp_image" to "image"
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = temp_image[i][j];
        }
    }
    return;
}