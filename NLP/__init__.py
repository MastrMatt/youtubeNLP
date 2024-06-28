# make sure to download nltk data when importing the module
import os
import nltk

# make sure nltk loads the data from the current directory
nltk.data.path.append("./nltk_data")

# download the necessary nltk data to the current directory
nltk.download("vader_lexicon", download_dir="./nltk_data")
nltk.download("punkt", download_dir="./nltk_data")
nltk.download("averaged_perceptron_tagger", download_dir="./nltk_data")
nltk.download("maxent_ne_chunker", download_dir="./nltk_data")
nltk.download("words", download_dir="./nltk_data")
