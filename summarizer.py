from string import punctuation
from heapq import nlargest

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

def nltk_summarize(text_content, percent):
    # Frequency Based Summarization using NLTK
    # Store a tokenized copy of text, using NLTK's recommended word tokenizer
    tokens = word_tokenize(text_content)

    # Import the stop words from NLTK toolkit
    stop_words = stopwords.words('english')

    # import punctuations from strings library.
    punctuation_items = punctuation + '\n'

    # Create the dictionary with key as words and value as number of times word is repeated.
    # Scoring words by its occurrence.
    word_frequencies = {}
    for word in tokens:
        if word.lower() not in stop_words:
            if word.lower() not in punctuation_items:
                if word not in word_frequencies.keys():
                    word_frequencies[word] = 1
                else:
                    word_frequencies[word] += 1

    # Finding frequency of most occurring word
    max_frequency = max(word_frequencies.values())

    # Divide Number of occurrences of all words by the max_frequency
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / max_frequency

    # Save a sentence-tokenized copy of text
    sentence_token = sent_tokenize(text_content)

    # Create the dictionary with key as sentences and value as sum of each important word.
    # Scoring sentences by its words.
    sentence_scores = {}
    for sent in sentence_token:
        sentence = sent.split(" ")
        for word in sentence:
            if word.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word.lower()]
                else:
                    sentence_scores[sent] += word_frequencies[word.lower()]

    # Finding number of sentences and applying percentage on it: since we require to show most X% lines in summary.
    select_length = int(len(sentence_token) * (int(percent) / 100))

    # Using nlargest library to get the top x% weighted sentences.
    summary = nlargest(select_length, sentence_scores, key=sentence_scores.get)

    # Later joining it to get the final summarized text.
    final_summary = [word for word in summary]
    summary = ' '.join(final_summary)

    # Returning NLTK Summarization Output
    return summary


