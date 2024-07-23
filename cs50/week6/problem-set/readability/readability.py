from cs50 import get_string

global letterCount, wordCount, sentenceCount, index

def main():

    text = get_string("Text: ")

    countLetters(text)

    countWords(text)

    countSentences(text)
    
    colemanLiauIndex(letterCount, wordCount, sentenceCount)
    
    gradeLevel(index)

# Counts letters in input text for later use in Coleman-Liau index calculation
def countLetters(text):
    global letterCount
    letterCount = 0
    for char in text:
        if char.isalpha():
            letterCount += 1

# Counts words in input text for later use in Coleman-Liau index calculation
def countWords(text):
    global wordCount
    wordCount = 1
    for char in text:
        if char.isspace():
            wordCount += 1

# Counts sentences in input text for later use in Coleman-Liau index 
# calculation
def countSentences(text):
    global sentenceCount
    sentenceCount = 0
    for char in text:
        if char == '.' or char == '!' or char == '?':
            sentenceCount += 1

# Applies formula to calculate Coleman-Liau index
def colemanLiauIndex(letterCount, wordCount, sentenceCount):
    global index
    l = (float(letterCount) / float(wordCount)) * 100
    s = (float(sentenceCount) / float(wordCount)) * 100
    index = int(round(0.0588 * l - 0.296 * s - 15.8))

# Uses previously calculated Coleman-Liau index to determine approximate
# corresponding grade level
def gradeLevel(index):
    if index >= 1:
        if index <= 16:
            print(f"Grade {index}")
        else:
            print("Grade 16+")
    else:
        print("Before Grade 1")

if __name__ == "__main__":
    main()