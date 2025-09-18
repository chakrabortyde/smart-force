import nltk.data

try:
    nltk.data.find("taggers/averaged_perceptron_tagger_eng")
    print("averaged_perceptron_tagger_eng installed successfully!")
except LookupError:
    print("punkt_tab missing, using punkt only.")
    # nltk.download('averaged_perceptron_tagger_eng')