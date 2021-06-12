#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 18:10:42 2017
This code, 
    1-  Reads raw SCOTUS opinions (as a set of .json files) from the data set downloaded from: https://www.courtlistener.com/api/bulk-data/
    2-  Extracts text of each opinion excluding all citations. Each opinion is saved as .txt file in the "opinion_save_path" path.
    3- Generates citation counters and citation vectors for each opinion
        - Counter of the number of citations (cited and cited by) regardless of that if the citation is within the same corpus.
        - Counter of the number of citations (cited and cited by) only considering the citations within the corpus.
    4- Creates citation databases (sqlite3) for specified time span
@author: faraz dadgostari
"""

import os 
import re
import shutil
import json
from bs4 import BeautifulSoup

from datetime import datetime      
import time

from django.utils.encoding import smart_str   #pip install Djsmart_strango==1.11.2
import cProfile, pstats, io
import itertools


"""
FUNCTIONS
"""

"""
Remove citations from an opinion:
"""
def remove(soup, tagname):                
    for tag in soup.findAll(tagname):
        tag.extract()
"""
Replace citations from an opinion with "somthing" (here with "white space")        
"""        
def replace(soup, tagname, content):      
    for tag in soup.findAll(tagname):
        tag.replace_with(content)

"""
Save 1st section of the code's output data in some files:
it prevents the need to repeat the 1st part of the code, when the 2nd part is being debugged     
"""        
   
"""OR"""

""" 
Save the files of resulted data that is generated in the 2st section of the code-
It contains most of input data for the RL-algorithm and DB generation phase
"""    
def save_to (listORdict,name,path):     
    workingdatapath=os.path.join(path, name)
    data = open(workingdatapath, 'w')
    json.dump(listORdict, data)


"""
Read back the constructed data in the first part of the code to be used in the second part    
"""
def load_from(name,path):
    with open (os.path.join(path, name)) as f:
        return json.load(f)    
    
"""
Copies the opinion if it was filed during a specific timespan-reads from the "opinion_save_path"    

"""
def extract_timespan_opinions(opinion,start,end,R_opiniondatas_number,timespan_opinions_save_path,timespan_opinions_list):
    if R_opiniondatas_number[opinion]<end and R_opiniondatas_number[opinion]>start:
        shutil.copy2(os.path.join(opinion_save_path_original, opinion), timespan_opinions_save_path) # target filename is /dst/dir/file.ext
        timespan_opinions_list.append(opinion)

""""###########################"""

pr0 = cProfile.Profile()
pr0.enable()

#To keep track of the running time
print("It starts at: ", time.strftime('%X %x %Z'))
Starttime=time.time()


"""##########################setting paths and some other env veriables##########################"""
#list of paths to be generated
output_data_paths=[]

"""setting working dir path and other env veriables"""
dir_path = "/Users/faraz/Dropbox (Team Beling)/1.Edu-PhD/1-Research/1.Research Projects/6.Computational Law/Code/0-Data aquisation and cleaning-Github2" 
#running on any platform, if you set this address right other paths will be generated automatically
os.chdir(dir_path)



"""setting the paths for source data to be read from"""
#algorithm  is feeded using the SCOTUS bulk data downloaded from Courtlistener.com
Rawdata_path = "../../"+"Data/0-Courtlistener.com"
Raw_opinions_path = Rawdata_path+'/scotus-raw'
Cluster_metadata_path= Rawdata_path+'/Cluster_metadata'
Docket_metadata_path= Rawdata_path+'Docket_metadata'


"""setting target path for output data to be saved in"""
path = 'Code\'s data lake'
output_data_paths.append(path)

opinion_save_path = path + '/Extracted opinions in the text format-no citation-from html_with_citations tag'
output_data_paths.append(opinion_save_path)




opinion_save_path_original = path + '/Extracted opinions in the text format-no citation-from html_with_citations tag with Opinion_ID naming'
output_data_paths.append(opinion_save_path_original)



#a folder to save the files of resulted data that is generated in the 2st section of the code-
#it contains most of input data for the RL-algorithm and DB generation phase
output_path = path + '/output data'
output_data_paths.append(output_path)


for p in output_data_paths:
    if not os.path.exists(p):
        os.makedirs(p)
"""##############################################################################################"""




pr1 = cProfile.Profile()
pr1.enable()
"""#################################Part1-Extracting and cleaning the data-"www.courtlistener.com" database of SCOTUS#################################"""

n, m = 0, 0
printing_interval= 250
opiniondatas={}
Error=[]
dict={}
dict2={}
dict3={}
opiniondatas_number={}
opiniondatas_names={}
Opinion_IDs_triple=[]
Nodateopinions=[]   #it records the .json files in which the date_filed tag is empty and then we don't have when the opinion has been filed
Nonameopinions=[]   #it records the .json files in which the federal_cite_one tag is empty and then we don't have any citation name for that
Badnameopinions=[]
titels=[]           #list of opinions, as they should be cited
Opinions=[]         #list of opinions, as they have been nemed by unique IDs in Courtlistener.com
Opinion_IDs_File_Names_dictionary={}




if os.path.exists(Raw_opinions_path+"/.DS_Store"):
    os.remove(Raw_opinions_path+"/.DS_Store")
files = os.listdir(Raw_opinions_path)

print("count of opinions:", len(files))
for Opinion_ID in files:
    O = re.sub('\.json$', '', Opinion_ID)
    if n==m:
        print("\nOpinion is: ", Opinion_ID)
        print("it is at line n = ", n ," in the data folder")   #it should end up at 63,865 items
    opinion=open(Raw_opinions_path+"/"+Opinion_ID).read()
    data = json.loads(opinion)
    
    """=====Meta_data aquisation for the opinion as: date it has been filed, citation names, ... ====="""
    OpinioninCluster = data["cluster"]
    OpinioninClusterID = re.findall("/([0-9]+)/",OpinioninCluster)[0]+".json"
    opinionmeta_C = open(Cluster_metadata_path+"/"+OpinioninClusterID).read()
    metadata_C = json.loads(opinionmeta_C)
    OpinionDocket= metadata_C["docket"]
    OpinionDocketID=re.findall("/([0-9]+)/",OpinionDocket)[0]+".json"
    Opinion_IDs_triple.append((Opinion_ID,OpinioninClusterID,OpinionDocketID))
    
    datestring=metadata_C["date_filed"]
    date=datetime.strptime(datestring, '%Y-%m-%d')
            
    if len(datestring)<1:
        Nodateopinions.append(Opinion_ID)       
    
    Ntitle=metadata_C["federal_cite_one"]
    if len(Ntitle)<1:
        Ntitle = "nocitationName"+" "+O
        Nonameopinions.append(Opinion_ID)
        
    title=Ntitle.replace("U.S.", "US").replace(" ","_")+".txt"   
    #this changes the format of the name of the opinion +.txt
    
    if title in titels:
        title=Ntitle.replace("U.S.", "US").replace(" ","_")+"(copy but different-it is txt for "+Opinion_ID+").txt"
        Ntitle=Ntitle+"(copy but different-it is txt for "+Opinion_ID+")"
    
    titels.append(title)
    Opinions.append((Opinion_ID))
    
    if not "U.S." in Ntitle:
        Badnameopinions.append(Opinion_ID) 
    if n==m:
        print("title: ", title)
        
    

    """--------------------------------------------------------------------------------------------------"""


    """=====reading the text of the opinion and writing it to .txt files (2 versions====="""
    #reading the text file after removal of the citations####################################
    html=smart_str(data["html"])
    filenamepath=os.path.join(Raw_opinions_path, Opinion_ID)
    handle=open(filenamepath).read()
    html_with_citations=smart_str(data["html_with_citations"])
    bs = BeautifulSoup(html_with_citations, "html.parser")
    replace(bs,"a","      ")  # it removes the citations from the text of the opinion

    html_no_citations=smart_str(bs)        
    txt=bs.get_text()  #it can be used instead of html2text in the case we get 'ascii' error
    
    #writing text to a .txt file, version 1: naming the .txt file using "title"###############
    filenamepath=os.path.join(opinion_save_path, title)
    tx = open(filenamepath, 'w')
    tx.write(txt)
    tx.close()
    
    
    
    #writing text to a .txt file, version 2: naming the .txt file using "Opinion_ID"###########
    filenamepathoriginal=os.path.join(opinion_save_path_original, Opinion_ID)
    txo = open(filenamepathoriginal, 'w')
    txo.write(txt)
    txo.close()
    if n==m:
        print("It is: ", time.strftime('%X %x %Z') )
        print("passed time: ", time.strftime("%H:%M:%S", time.gmtime(time.time()-Starttime)))
        m=n+printing_interval
    n=n+1
    """-------------------------------------------------------------------------------------"""
    
    """recording the metadata and their associations"""
    dict[Opinion_ID]=Ntitle
    dict2[Opinion_ID]=title
    Opinion_ID_number=Opinion_ID.replace(".json","")
    dict3[Opinion_ID_number]=title

    
    opiniondatas_number[Opinion_ID]=date.isoformat()
    opiniondatas_names[title]=date.isoformat()
    """---------------------------------------------"""

"""###################################################################################################################################################"""
pr1.disable()
s = io.StringIO()
sortby = 'cumulative'
ps1 = pstats.Stats(pr1, stream=s).sort_stats(sortby)
pstats.Stats(pr1).print_stats()
print(s.getvalue())




pr2 = cProfile.Profile()
pr2.enable()
"""######################################Part2-Extracting and cleaning the data-"www.courtlistener.com" database of SCOTUS#####################################"""

"""=======================================Generation of citation counters and citation vectors for each opinion==========================================="""
AvailableOpinions=tuple(R_Opinions)
fhandle=open(Rawdata_path+"/US_all_citations.csv")  #original name was all.csv and it includes citaions other than SCOTUS opinions
#file=fhandle.read()



"""-------------Loop 1: counting number of citations(cited and cited by) regardless of that if it is a S-court opinion or not----------------"""
cited_all_US_corpus={}      #includes non-supreme court citations-number of citations of an opinion, regardless of that if it is a S-court opinion or not
cited_by_US_corpus_all={}   #includes non-supreme court citations-number of citations recieved by an opinion, regardless of that if it is a S-court opinion or not


n, m = 0, 0
for line in fhandle:
    citation=line.split(",") 
    if n==m:
        print("\nwe are at the first loop line n: ", n   )
        print("It is: ", time.strftime('%X %x %Z') )
        print("passed time: ", time.strftime("%H:%M:%S", time.gmtime(time.time()-Starttime)))
        m=n+10000*printing_interval
    if citation[0] not in cited_all_US_corpus:
        cited_all_US_corpus[citation[0]]=1
    else:
        cited_all_US_corpus[citation[0]]=cited_all_US_corpus[citation[0]]+1           
    if citation[1].rstrip() not in cited_by_US_corpus_all:
        cited_by_US_corpus_all[citation[1].rstrip()]=1
    else:
        cited_by_US_corpus_all[citation[1].rstrip()]=cited_by_US_corpus_all[citation[1].rstrip()]+1
    n=n+1
        
        
#saving it to output data folder
save_to (cited_all_US_corpus,"cited_all_US_corpus",output_path)
save_to (cited_by_US_corpus_all,"cited_by_US_corpus_all",output_path)    

R_cited_all_US_corpus=load_from ("cited_all_US_corpus",output_path)
R_cited_by_US_corpus_all=load_from ("cited_by_US_corpus_all",output_path)


"""---------------Loop 2: counting number of citations(cited and cited by) only considering S-court opinion as citer or cited---------------"""
fhandle=open(Rawdata_path+"/US_all_citations.csv")  #original name was all.csv and it includes citaions other than SCOTUS opinions



"""generation of a citaion and citation_by vector for each opinion in courpus in the form of 2 dictionaries"""
cited_the_SCOTUS_corpus_vectors={}     #includes just supreme court citations
cited_by_SCOTUS_corpus_vectors={}      #includes just supreme court citations
          
m=0; n=0; v=0
m0=0
for line in fhandle:
    n=n+1        
    citation=line.split(",") 
    cite=citation[0]+".json"
    if cite in AvailableOpinions:
        if citation[1].rstrip()+".json" in AvailableOpinions:
            if citation[0] not in cited_the_SCOTUS_corpus_vectors:
                cited_the_SCOTUS_corpus_vectors[citation[0]]=[citation[1].rstrip()]
                print("\nn = ",n)
                print("v = ", v)
                print("m0 = ",m0)
                if v>=0:
                    m0=v+printing_interval/20
                m=m+1
                v=v+1
            else:
                cited_the_SCOTUS_corpus_vectors[citation[0]].append(citation[1].rstrip())
                m=m+1
            if citation[1].strip() not in cited_by_SCOTUS_corpus_vectors:
                cited_by_SCOTUS_corpus_vectors[citation[1].rstrip()]=[citation[0]]
            else:
                cited_by_SCOTUS_corpus_vectors[citation[1].rstrip()].append(citation[0])      
                    
save_to (cited_the_SCOTUS_corpus_vectors,"cited_the_SCOTUS_corpus_vectors",output_path)
R_cited_the_SCOTUS_corpus_vectors=load_from ("cited_the_SCOTUS_corpus_vectors",output_path)

save_to (cited_by_SCOTUS_corpus_vectors,"cited_by_SCOTUS_corpus_vectors",output_path) 
R_cited_by_SCOTUS_corpus_vectors=load_from ("cited_by_SCOTUS_corpus_vectors",output_path)
print("It is the end of Loop 2, recorded at: ", time.strftime('%X %x %Z') )



"""counting the number of citaions and citation_bys for each opinion in courpus in the form of 2 dictionaries"""
cited_the_SCOTUS_corpus_count={}             #includes just supreme court citations
cited_by_SCOTUS_corpus_count={}              #includes just supreme court citations     

for opinion in cited_the_SCOTUS_corpus_vectors:
    cited_the_SCOTUS_corpus_count[opinion]=len(cited_the_SCOTUS_corpus_vectors[opinion])
      
for opinion in cited_by_SCOTUS_corpus_vectors:
    cited_by_SCOTUS_corpus_count[opinion]=len(cited_by_SCOTUS_corpus_vectors[opinion]) 
   
save_to (cited_the_SCOTUS_corpus_count,"cited_the_SCOTUS_corpus_count",output_path)
save_to (cited_by_SCOTUS_corpus_count,"cited_by_SCOTUS_corpus_count",output_path)  

R_cited_the_SCOTUS_corpus_count=load_from ("cited_the_SCOTUS_corpus_count",output_path)
R_cited_by_SCOTUS_corpus_count=load_from ("cited_by_SCOTUS_corpus_count",output_path)
"""-----------------------------------------------------------------------------------------------------------------------------------------------------------""" 
pr2.disable()
s = io.StringIO()
sortby = 'cumulative'
ps2 = pstats.Stats(pr2, stream=s).sort_stats(sortby)
pstats.Stats(pr2).print_stats()
print(s.getvalue())

        
        
pr0.disable()
s = io.StringIO()
sortby = 'cumulative'
ps0 = pstats.Stats(pr0, stream=s).sort_stats(sortby)
pstats.Stats(pr0).print_stats()
print(s.getvalue())       

###extracting opinions of specified interval
interval_start = 1946
interval_end = 2005
start = str(interval_start)+"-00-00T00:00:00"
end = str(interval_end+1)+"-00-00T00:00:00"
time_span=str(interval_start)+'-'+str(interval_end)



timespan_opinions_save_path = path + '/'+time_span+' extracted in the text format-no citation-from no citation num.txt files folder' #the folder to save the opinions filed in the time_span

if not os.path.exists(timespan_opinions_save_path):
    os.makedirs(timespan_opinions_save_path)

n_availabale_opinions=len(AvailableOpinions)   
timespan_opinions_list=[]
map(extract_timespan_opinions,AvailableOpinions,itertools.repeat(start,n_availabale_opinions),
    itertools.repeat(end,n_availabale_opinions), itertools.repeat(R_opiniondatas_number,n_availabale_opinions), 
    itertools.repeat(timespan_opinions_save_path,n_availabale_opinions),
    itertools.repeat(timespan_opinions_list,n_availabale_opinions))

save_to (timespan_opinions_list,"timespan_opinions_list",output_path)  
R_timespan_opinions_list=load_from ("timespan_opinions_list",output_path)

#building the citation vectors for the time span as a blackbox
cited_by_timespan_SCOTUS_corpus_vectors={}   #a vector for each timespan SCOTUS opinion cited by other timespan SCOTUS opinions
for op in R_cited_by_SCOTUS_corpus_vectors:
    if op+".json" in R_timespan_opinions_list:
        citationlist=[]
        for citation in R_cited_by_SCOTUS_corpus_vectors[op]:
            if citation+".json" in R_timespan_opinions_list:
               citationlist.append(citation) 
        cited_by_timespan_SCOTUS_corpus_vectors[op]=citationlist
        
        
        
cited_the_timespan_SCOTUS_corpus_vectors={}    #a vector for each timespan SCOTUS opinion citing other timespan SCOTUS opinions
for op in R_cited_the_SCOTUS_corpus_vectors:
    if op+".json" in R_timespan_opinions_list:
        citationlist=[]
        for citation in R_cited_the_SCOTUS_corpus_vectors[op]:
            if citation+".json" in R_timespan_opinions_list:
               citationlist.append(citation) 
        cited_the_timespan_SCOTUS_corpus_vectors[op]=citationlist              ###it produce empty citation vectors###############
        
        

save_to (cited_by_timespan_SCOTUS_corpus_vectors,"cited_by_timespan_SCOTUS_corpus_vectors",output_path)
R_cited_by_timespan_SCOTUS_corpus_vectors=load_from ("cited_by_timespan_SCOTUS_corpus_vectors",output_path)
save_to (cited_the_timespan_SCOTUS_corpus_vectors,"cited_the_timespan_SCOTUS_corpus_vectors",output_path)
R_cited_the_timespan_SCOTUS_corpus_vectors=load_from ("cited_the_timespan_SCOTUS_corpus_vectors",output_path)

S1=set(R_cited_the_timespan_SCOTUS_corpus_vectors.keys())
S2=set(R_cited_by_timespan_SCOTUS_corpus_vectors.keys())
ST=S1|S2 #all the SCOTUS cases in the timespan which are not isolated from the citation network
save_to (sorted(list(ST)),"in_network_SCOTUS_timespan_opinions_list_z",output_path)
R_in_network_SCOTUS_timespan_opinions_list=load_from ("in_network_SCOTUS_timespan_opinions_list_z",output_path)
#Building the in_network time_span opinions data folder 

in_network_timespan_opinions_save_path = path + '/'+time_span+' in_the_network extracted in the text format-no citation-from no citation num.txt files folder' #the folder to save the opinions filed in the time_span
if not os.path.exists(in_network_timespan_opinions_save_path):
    os.makedirs(in_network_timespan_opinions_save_path)
for op in ST:    
    shutil.copy2(os.path.join(opinion_save_path_original, op+".json"),in_network_timespan_opinions_save_path)




#DB-----creating citation file for in_network SCOTUS opinions in the specified time span
import sqlite3     # Part of standard library, used in from_database()
conn = sqlite3.connect("SCOTUS_citation_network_in_the_time_span_GitHub.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE "Nodes"(
	"ID" INTEGER,
	"courtlistener_ID"	TEXT,
	"USID_index"	TEXT,
	"date"	TEXT,
     PRIMARY KEY("ID")
    )"""
        );

n=0
for op in R_in_network_SCOTUS_timespan_opinions_list:
    n=n+1
    cur.execute("""
                INSERT INTO Nodes ("courtlistener_ID", "USID_index", "date")
                VALUES (?,?,?)
                """, (op, dict[op+".json"],opiniondatas_number[op+".json"])
                );

cur.execute("""
       SELECT "ID", "courtlistener_ID" 
       FROM Nodes
""");
         
           
foreign_ID_dict={}           
for row in cur:
    foreign_ID_dict[row[1]]=row[0]          
           
cur.execute("""
CREATE TABLE "Citations"(
    "ID-citing" INTEGER,
    "ID-cited" INTEGER,
	"listner_CaseID-citing"	TEXT,
	"listner_CaseID-cited"	    TEXT,
    "USID_index_citing"	TEXT,
    "USID_index_cited" 	TEXT
    )"""
        );

n=0
for op in S1:
    for cited_op in cited_the_timespan_SCOTUS_corpus_vectors[op]:
        n=n+1
        cur.execute("""
                    INSERT INTO Citations ("ID-citing", "ID-cited", "listner_CaseID-citing", "listner_CaseID-cited",USID_index_citing,USID_index_cited)
                    VALUES (?,?,?,?,?,?)
                    """, (foreign_ID_dict[op], foreign_ID_dict[cited_op], op, cited_op, dict[op+".json"], dict[cited_op+".json"])
                    );
           

conn.commit()
conn.close()






