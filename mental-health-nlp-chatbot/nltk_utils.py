"""
NLP Utilities for Mental Health Chatbot.
Provides tokenization, Porter stemming, and Bag-of-Words feature extraction.
"""

from typing import List, Sequence
import numpy as np
import nltk
from nltk.stem.porter import PorterStemmer

# Ensure necessary NLTK data packages are present
for resource in ("punkt", "punkt_tab"):
    try:
        nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        try:
            nltk.download(resource, quiet=True)
        except Exception:
            pass

stemmer = PorterStemmer()


def tokenize(sentence: str) -> List[str]:
    """
    Split a sentence into an array of words/tokens.
    A token can be a word, punctuation mark, or number.
    """
    if not sentence:
        return []
    return nltk.word_tokenize(sentence)


def stem(word: str) -> str:
    """
    Find the root stem of a given word using Porter Stemmer.
    Example:
        stem("organizing") -> "organ"
    """
    return stemmer.stem(word.lower())


def bag_of_words(tokenized_sentence: Sequence[str], words: Sequence[str]) -> np.ndarray:
    """
    Return a bag-of-words vector:
    1 for each vocabulary word that exists in the stemmed sentence, 0 otherwise.

    Args:
        tokenized_sentence: List of tokens from user input.
        words: Vocabulary list of stemmed words.

    Returns:
        np.ndarray: Binary 1D float32 array of shape (len(words),)
    """
    sentence_words = {stem(w) for w in tokenized_sentence}
    bag = np.zeros(len(words), dtype=np.float32)

    for idx, w in enumerate(words):
        if w in sentence_words:
            bag[idx] = 1.0

    return bag