# Language-and-Network-Modeling-for-Legal-Corpora
This repository contains the code required to
- Aquire and clean legal documents for network and langauage modeling
- Language and Network Modeling of a legal corpus (here SCOTUS)
## Data Sources


## Code Organization:

### 0-Data acquisition and cleaning.py:
This code, 
   1. Reads raw SCOTUS opinions (as a set of .json files) from the data set downloaded from: https://www.courtlistener.com/api/bulk-data/
   2. Extracts text of each opinion excluding all citations. Each opinion is saved as .txt file in the 'output_data_paths'.
   3. Generates citation counters and citation vectors for each opinion
        - Counter of the number of citations (cited and cited by) regardless of that if the citation is within the same corpus.
        - Counter of the number of citations (cited and cited by) only considering the citations within the corpus.
    4.  Creates citation databases (sqlite3) for specified time span
   
**Note:**   The data sets generated in this code are saved in 'output_data_paths' including:
- opinion_save_path
- opinion_save_path_original
- output_path
These files contains most of the input data for the Language and Network Modeling code as well as the search algorithms of the X Repository.
   
