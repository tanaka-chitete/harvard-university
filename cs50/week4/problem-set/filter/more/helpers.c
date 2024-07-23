#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    int avgCol;

    // Iterates through each row of input image
    for (int i = 0; i < height; i++)
    {
        // Iterates through each column of input image
        for (int j = 0; j < width; j++)
        {
            // Obtains average RGB value of each pixel
            avgCol = round(((double)image[i][j].rgbtRed +
                            (double)image[i][j].rgbtGreen +
                            (double)image[i][j].rgbtBlue) / 3.0);

            // Assigns RGB values to the same value (avgCol)
            image[i][j].rgbtRed = avgCol;
            image[i][j].rgbtGreen = avgCol;
            image[i][j].rgbtBlue = avgCol;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    int jRight, jLeft;
    RGBTRIPLE temp;
    // Iterates through each row of input image
    for (int i = 0; i < height; i++)
    {
        // Iterates (only) through each column on the left side of input image
        // to prevent reflection overlap
        for (int j = 0; j < width / 2; j++)
        {
            // Reassigns j for readability purposes
            jLeft = j;
            // Obtains the corresponding vertically reflected value of j
            jRight = (width - 1) - jLeft;

            // Obtains jLeft pixel
            temp = image[i][jLeft];
            // Assigns jRight pixel to jLeft pixel (part one of reflection)
            image[i][jLeft] = image[i][jRight];
            // Assigns jLeft pixel (in temp) to jRight pixel (part two of reflection)
            image[i][jRight] = temp;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    // Helper function prototypes
    void deepCopy(int height, int width,
                  RGBTRIPLE imageCopy[height][width],
                  RGBTRIPLE image[height][width]);

    // Copies input image to perform blur transformation on a copy
    RGBTRIPLE imageCopy[height][width];
    deepCopy(height, width, imageCopy, image);

    int sumRed = 0;
    int sumGreen = 0;
    int sumBlue = 0;
    int sumDenominator = 0;

    BYTE avgRed;
    BYTE avgGreen;
    BYTE avgBlue;

    // Performs blur transformation
    // Iterates through each row of input image
    for (int i = 0; i < height; i++)
    {
        // Iterates through each column of input image
        for (int j = 0; j < width; j++)
        {
            // Iterates through each row of pixels within one pixel of current pixel
            for (int k = i - 1; k <= i + 1; k++)
            {
                // Iterates through each column of pixels within one pixel of current pixel
                for (int l = j - 1; l <= j + 1; l++)
                {
                    // Executes if either k or l is not out of bounds
                    if (!(k < 0 || k >= height || l < 0 || l >= width))
                    {
                        // Cumulatively sums each colour value of current pixel
                        sumRed += imageCopy[k][l].rgbtRed;
                        sumGreen += imageCopy[k][l].rgbtGreen;
                        sumBlue += imageCopy[k][l].rgbtBlue;

                        // Increments the number of pixels successfully processed
                        sumDenominator++;
                    }
                }
            }

            // Calculates average colour values of current pixel
            avgRed = round((double)sumRed / (double)sumDenominator);
            avgGreen = round((double)sumGreen / (double)sumDenominator);
            avgBlue = round((double)sumBlue / (double)sumDenominator);

            // Copies averages to current pixel of input image
            image[i][j].rgbtRed = avgRed;
            image[i][j].rgbtGreen = avgGreen;
            image[i][j].rgbtBlue = avgBlue;

            // Resets necesarry variables for use in next iteration
            sumRed = 0;
            sumGreen = 0;
            sumBlue = 0;
            sumDenominator = 0;
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    // Helper function prototypes
    void deepCopy(int height, int width,
                  RGBTRIPLE imageCopy[height][width],
                  RGBTRIPLE image[height][width]);

    int gX[3][3] =
    {
        {-1, 0, 1},
        {-2, 0, 2},
        {-1, 0, 1}
    };

    int gY[3][3] =
    {
        {-1,-2,-1},
        { 0, 0, 0},
        { 1, 2, 1}
    };

    // Copies input image to perform edge-detection transformation on a copy
    RGBTRIPLE imageCopy[height][width];
    deepCopy(height, width, imageCopy, image);

    int gXgYred;
    int gXgYgreen;
    int gXgYblue;

    int sumGxRed = 0;
    int sumGyRed = 0;
    int sumGxGreen = 0;
    int sumGyGreen = 0;
    int sumGxBlue = 0;
    int sumGyBlue = 0;

    // PERFORMS EDGE DETECTION TRANSFORMATION
    // Iterates through each row of input image and its copy
    for (int i = 0; i < height; i++)
    {
        // Iterates through each column of input image and its copy
        for (int j = 0; j < width; j++)
        {
            // Iterates through each row of pixels within one pixel of current pixel
            for (int k = i - 1; k <= i + 1; k++)
            {
                // Iterates through each column of pixels within one pixel of current pixel
                for (int l = j - 1; l <= j + 1; l++)
                {
                    // Executes if any surrounding pixel is not out of bounds
                    if (!(k < 0 || k >= height || l < 0 || l >= width))
                    {
                        // Cumulatively sums product of red value of current surrounding pixel
                        // and corresponding pixel of Gx and Gy kernels
                        sumGxRed += imageCopy[k][l].rgbtRed * gX[k - i + 1][l - j + 1];
                        sumGyRed += imageCopy[k][l].rgbtRed * gY[k - i + 1][l - j + 1];

                        // Cumulatively sums product of green value of current surrounding pixel
                        // and corresponding pixel of Gx and Gy kernels
                        sumGxGreen += imageCopy[k][l].rgbtGreen * gX[k - i + 1][l - j + 1];
                        sumGyGreen += imageCopy[k][l].rgbtGreen * gY[k - i + 1][l - j + 1];

                        // Cumulatively sums product of green value of current surrounding pixel
                        // and corresponding pixel of Gx and Gy kernels
                        sumGxBlue += imageCopy[k][l].rgbtBlue * gX[k - i + 1][l - j + 1];
                        sumGyBlue += imageCopy[k][l].rgbtBlue * gY[k - i + 1][l - j + 1];
                    }
                }
            }

            // Calculates Gx and Gy RGB values of current pixel using formula and
            gXgYred = round(sqrt(pow(sumGxRed, 2) + pow(sumGyRed, 2)));
            gXgYgreen = round(sqrt(pow(sumGxGreen, 2) + pow(sumGyGreen, 2)));
            gXgYblue = round(sqrt(pow(sumGxBlue, 2) + pow(sumGyBlue, 2)));

            if (gXgYred > 255)
            {
                gXgYred = 255;
            }

            if (gXgYgreen > 255)
            {
                gXgYgreen = 255;
            }

            if (gXgYblue > 255)
            {
                gXgYblue = 255;
            }

            image[i][j].rgbtRed = gXgYred;
            image[i][j].rgbtGreen = gXgYgreen;
            image[i][j].rgbtBlue = gXgYblue;

            sumGxRed = 0;
            sumGyRed = 0;
            sumGxGreen = 0;
            sumGyGreen = 0;
            sumGxBlue = 0;
            sumGyBlue = 0;
        }
    }
    return;
}

void deepCopy(int height, int width,
              RGBTRIPLE imageCopy[height][width],
              RGBTRIPLE image[height][width])
{
    // Iterates through each row of input image
    for (int i = 0; i < height; i++)
    {
        // Iterates through each column of input image
        for (int j = 0; j < width; j++)
        {
            // Copies pixel from input image
            imageCopy[i][j] = image[i][j];
        }
    }
    return;
}
