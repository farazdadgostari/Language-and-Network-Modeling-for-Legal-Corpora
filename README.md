# Language-and-Network-Modeling-for-Legal-Corpora
This repository contains the code required for building the language and network model described in the X Paper. The search algorithms, including the reinforcemet algorithm developed in the paper use this model as a representation of the knowledge space for law search.  The code for the search algorithms described in the Paper could be found in this [Reinforcement-Learning-for-Law-Search repository](https://github.com/farazdadgostari/Reinforcement-Learning-for-Law-Search).

The [Language-and-Network-Modeling-for-Legal-Corpora repository](https://github.com/farazdadgostari/Language-and-Network-Modeling-for-Legal-Corpora) contains the code required to
- Acquire and clean legal documents for network and language modeling
- Language and Network Modeling of a legal corpus (here SCOTUS)
## Data Sources:
We used the raw SCOTUS opinions (as a set of .json files) from the data set downloaded from: https://www.courtlistener.com/api/bulk-data/

## Code Organization:
### 0-Data acquisition and cleaning.py
This code, 
   1. Reads raw SCOTUS opinions (as a set of .json files) from the data set downloaded from [courtlistener](https://www.courtlistener.com/api/bulk-data/).
   2. Extracts text of each opinion excluding all citations. Each opinion is saved as .txt file in the 'output_data_paths'.
   3. Generates citation counters and citation vectors for each opinion
        - Counter of the number of citations (cited and cited by) regardless of that if the citation is within the same corpus.
        - Counter of the number of citations (cited and cited by) only considering the citations within the corpus.
   4. Creates citation databases (sqlite3) for a specified time span
   
**Note:**   The data sets generated in this code are saved in 'output_data_paths' including:
- opinion_save_path
- opinion_save_path_original
- output_path
These files contain most of the input data for the Language and Network Modeling code as well as the search algorithms of the "Reinforcement Learning for Law Search" Repository.

### 1-LgNetModelGen.py
This code reads the data generated by "Data acquisition and cleaning.py" code and uses 'btl_f' library to create a "Similarity Matrix" of the documents contained in the corpus based on an algebraic aggregation of topic model and citation network of the corpus. Here the SQLite3 database and data sets generated by "0-Data acquisition and cleaning.py" are being used to provide the necessary documents to form the topic model and citation network.

Change this as necessary for your own database, or form the corpus from a directory of files or a list of strings using the various helper functions in "corpus_f.py".

### corpus_f.py
This code includes functions and classes for tokenizing texts, constructing a
dictionary, and computing a document-term matrix suitable 
for input to a topic modeller such as LDA.


### topic_f.py
This code computes similarity with a Latent Dirichlet Allocation (LDA) topic model, 
which determines the distribution of TOPICS (collections of terms from
the dictionary) in each document.

### topic_f.py
This is a library to create a "Similarity Matrix" of the documents contained in the corpus based on an 
algebraic aggregation of topic model and citation network of the corpus.


**NOTE:** The data generated by this repository could be found in [here](https://www.dropbox.com/sh/0hq42zyxgr1q4tb/AACtrT85-hMG81e7nCePr1c0a?dl=0) and [here](https://www.dropbox.com/sh/k5owze4y7me51eb/AADZb3cKMJ6eefyPD4qU5b1ua?dl=0). 
