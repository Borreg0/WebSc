# Data Extraction tool from the Spanish digital newspaper La Razón.

## 1. Scraps the web  
- **Stores news in "data" folder in json format**
 

## 2. Process the files
- **Splits the list of news in *n*-chunks for further reading and tokenizing**
- **Creates *n* temporary files where news of every chunk are written**

## 3. Tokenization  
- **Opens and groups all temporary files to tokenize and write them in plain text**
- **Writes every token in a json file as list**

## 4. Tagging
- **Adds the gramathical cathegory to every word**

## 5. Frequencies
*Example in freqs folder*
- **Counts the times that a word with a given tag appears in the corpora**
