
# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 12:34:44 2017
@author: ramya.ananth
"""
"""
This Code will generate the Sentiment ,Escalation and Problem Detection Result
Input file should contain 'Collated_REFERENCE_ID'	'INCIDENT_THREAD_ID'	'Channel'	'Transcript'Columns
Column name spelling should be exactly same as I mentioned above.
Please go through TextMining Documnent that we shared before running this code
Kindly use Command line to run this code
Please make sure that you have installed "nltk" Package and "NLTK Data" Please follow this link "http://www.nltk.org/data.html"
Make sure that os.environ["JAVA_HOME"] Variable has been set correctly
Please also  change the 'text_mine_output_path' Variable
"""
import sys
import os
from subprocess import check_output

import time

startTime = time.time()


#home = os.path.dirname(os.path.abspath(__file__))
#os.sys.path.append(home)
#os.chdir(home)
#print home
print os.getcwd()
import pandas as pd


os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"

import cPickle as pickle
import mine_text.mtServicesAPI as mt
import mine_text.mcsa_word_relationships as mcwa

print sys.argv[1][-3:]      

if sys.argv[1][-3:] == "csv":
    print 4

    path_of_transcript_files = sys.argv[1]
    print(path_of_transcript_files)
    name_of_transcript_file = path_of_transcript_files.split("/")[-1]
    print(name_of_transcript_file)
    name_of_transcript_file = name_of_transcript_file[:-4]
    print name_of_transcript_file
    

print("processing the transcript.csv for text mining input")

text_mine_output_path = "/home/nitin/Desktop/Outputs/"
try:
    os.mkdir("".join((text_mine_output_path,name_of_transcript_file)))	
    print("i am making the results folder as it does not exist")
except:
    pass    

import pandas as pd
import re
import nltk
import math

print 4
input_file_path= "".join((path_of_transcript_files))
print input_file_path
#input_file_path = path_of_transcript_files

print 5

data = pd.read_csv(input_file_path) 


#grouped_data = data.groupby(['FileName'])

#final_data = grouped_data.Transcripts.apply(lambda x: ". ".join([str(i) for i in x]))
final_data = data
#writing files to a csv 

filename = []
rank = []
channel = []
index = []
cust_texts = []
#base_ref = []
collated_ref = []
incident_thread_id = []
#thread_created  = []


for ind,chat in enumerate(final_data['Transcript']):
    print(ind)
    try:
        cust_text = nltk.sent_tokenize(chat)
    except:
        print("current chat failed")
        continue
    for i,ct in enumerate(cust_text):
        filename.append(final_data.index[ind])
        rank.append(i+1)
        channel.append(final_data.ix[final_data.index[ind],'Channel'])
        #base_ref.append(final_data.ix[final_data.index[ind],'B_RNT_ReferenceId_A_Category_N'])
        collated_ref.append(final_data.ix[final_data.index[ind],'Collated_REFERENCE_ID'])
        incident_thread_id.append(final_data.ix[final_data.index[ind],'INCIDENT_THREAD_ID'])
        #thread_created.append(final_data.ix[final_data.index[ind],'THREAD_CREATED'])
        index.append(ind)
        cust_texts.append(ct)

result = pd.DataFrame({"filename":filename,"rank":rank,"channel": channel,"collate_Ref_IDs":collated_ref,"INCIDENT_THREAD_ID":incident_thread_id,"index":index,"cust_text":cust_texts})
result["sentence_sentiment"]="neutral"
result["overall_sentiment"]=""
result["problem_detection"]=0
result["prior_escalation"]=0
result["current_escalation"]=0


data = result

analytical_data = pd.DataFrame()
total_rows =0
unique_index=0
data = result

try:
    l1 = list(data.columns).index("caller")
    caller_name = data.ix[0,"caller"]
    index_fill=[]
    for i in data.index:
        if data.ix[i,"caller"] == caller_name:
            index_fill.extend([i])
        else:
            caller_name = data.ix[i,"caller"]
            data.ix[index_fill,"unique_index"] = unique_index
            unique_index = unique_index + 1 
            pop_value = index_fill.pop(len(index_fill)-1)
            data.ix[index_fill,"overall_sentiment"] = ""
            index_fill=[i]
            try:
                if(math.isnan(float(data.ix[pop_value,"overall_sentiment"]))):
                    print("not relevant")
                    data.ix[pop_value,"overall_sentiment"] = "not relevant"
            except:
                pass
    data.ix[index_fill,"unique_index"] = unique_index
    pop_value = index_fill.pop(len(index_fill)-1)
    data.ix[index_fill,"overall_sentiment"] = ""
    unique_index = unique_index + 1
    try:
        if(math.isnan(float(data.ix[pop_value,"overall_sentiment"]))):
            print("not relevant")
            data.ix[pop_value,"overall_sentiment"] = "not relevant"
    except:
        pass
    data = data[["unique_index","rank","channel","collate_Ref_IDs","INCIDENT_THREAD_ID","cust_text","sentence_sentiment","overall_sentiment","problem_detection","prior_escalation","current_escalation"]]

except:
    l1 = list(data.columns).index("index")
    index_n = data.ix[0,"index"]
    index_fill=[]
    for i in data.index:
        if data.ix[i,"index"] == index_n:
            index_fill.extend([i])
        else:
            index_n = data.ix[i,"index"]
            data.ix[index_fill,"unique_index"] = unique_index
            unique_index = unique_index + 1 
            pop_value = index_fill.pop(len(index_fill)-1)
            data.ix[index_fill,"overall_sentiment"] = ""
            index_fill=[i]
            try:
                if(math.isnan(float(data.ix[pop_value,"overall_sentiment"]))):
                    print("not relevant")
                    data.ix[pop_value,"overall_sentiment"] = "not relevant"
            except:
                pass
    data.ix[index_fill,"unique_index"] = unique_index
    pop_value = index_fill.pop(len(index_fill)-1)
    data.ix[index_fill,"overall_sentiment"] = ""
    unique_index = unique_index + 1   
    try:
        if(math.isnan(float(data.ix[pop_value,"overall_sentiment"]))):
            print("not relevant")
            data.ix[pop_value,"overall_sentiment"] = "not relevant"
    except:
        pass
    #data = data[["unique_index","filename","cust_text","sentence_sentiment","overall_sentiment","problem_detection","prior_escalation","current_escalation"]]
    data = data[["unique_index","rank","channel","collate_Ref_IDs","INCIDENT_THREAD_ID","cust_text","sentence_sentiment","overall_sentiment","problem_detection","prior_escalation","current_escalation"]]
total_rows = total_rows + data.shape[0]
print(data.problem_detection.unique()[0])
if data.problem_detection.unique()[0] == 0 or data.problem_detection.unique()[0] == 1:
    print("i am here")
    analytical_data = analytical_data.append(data)
else:
    print("i came here and failed")
    
    
#cleaning the data
del_from_data = ["&lt;br /&gt;","&amp;#39;", "&amp;nbsp;"," &amp;amp;" ,"&amp;quot", " &amp;" , "&gt;","&lt;"]
for dels in del_from_data:
    analytical_data.cust_text = analytical_data.cust_text.apply(lambda x:str(x).replace(dels,""))


print("starting the text mining processing")
#analytical_data.to_csv(("".join((text_mine_output_path,name_of_transcript_file,"/AnalyticsData.csv")),encoding = "latin"))
data = analytical_data
data.to_csv("".join((text_mine_output_path,name_of_transcript_file,"/AnalyticsData.csv")))


#clean text

def clean_text(text):
    text = text.split(" ")
    text = [te[:-2] for te in text]
    text= " ".join(text)
    return(text)
    
#list of output files for transcript results
entitySentimentPath="".join((text_mine_output_path,name_of_transcript_file,"/entitySentiment.csv"))
escalationPath="".join((text_mine_output_path,name_of_transcript_file,"/escalation.csv"))
sentimentPath="".join((text_mine_output_path,name_of_transcript_file,"/sentiment.csv"))
problemDetectionPath="".join((text_mine_output_path,name_of_transcript_file,"/problemDetection.csv"))
keywordsPath="".join((text_mine_output_path,name_of_transcript_file,"/keywords.csv"))


#opening the csv object to write the files
entitySentiment=open(entitySentimentPath,"wb")
entitySentiment.write("unique_index|text_rank|type|collate_Ref_IDs|INCIDENT_THREAD_ID|cust_text|Entity|Phrase|Sentiment\n")



escalation=open(escalationPath,"wb")
escalation.write("unique_index|text_rank|type|collate_Ref_IDs|INCIDENT_THREAD_ID|cust_text|current_escalation|current_esc_prob|previous_escalation|previous_esc_prob\n")

sentiment=open(sentimentPath,"wb")
sentiment.write("unique_index|text_rank|type|collate_Ref_IDs|INCIDENT_THREAD_ID|cust_text|sentiment|prob\n")


problemDetection=open(problemDetectionPath,"wb")
problemDetection.write("unique_index|text_rank|type|collate_Ref_IDs|INCIDENT_THREAD_ID|cust_text|Context|result|prob\n")

keywords = open(keywordsPath,"wb")
keywords.write("unique_index|text_rank|type|collate_Ref_IDs|INCIDENT_THREAD_ID|cust_text|Keywords|Modifiers\n")

print(data.shape)
print(data.cust_text)
print(data.columns)
#import pymysql
#db = pymysql.connect("10.10.100.31","root","Tr3dence@123","CSAT")
#cursor = db.cursor()
#print(cursor)
for ind,calls in enumerate(data.cust_text):
    print(ind)
    try:
        
        unique_index = data.ix[data.index[ind],"unique_index"]
        rank = data.ix[data.index[ind],"rank"]
        channel = data.ix[data.index[ind],"channel"]
        #print("i came here")
        #REFERENCE_ID = data.ix[data.index[ind],"filename"]
        #base_ref     = data.ix[data.index[ind],"base_ref"]
        collated_ref =  data.ix[data.index[ind],"collate_Ref_IDs"]
        incident_thread_id = data.ix[data.index[ind],"INCIDENT_THREAD_ID"]
        #thread_created = data.ix[data.index[ind],"THREAD_CREATED"]
        #print 222,calls
        nlp=mt.mtRunServices(calls)
        #print (nlp[0]["entitySentiment"]["result"])
        for items in nlp[0]["entitySentiment"]["result"]:
            #print 3
            
            
            entitySentiment.write("%d|%d|%s|%s|%s|%s|%s|%s|%s\n"%(unique_index,rank,channel,collated_ref,incident_thread_id,calls,clean_text(items["entity"]),clean_text(items["phrase"]),items["sentiment"]))
	    #query=('insert into entitySentiment values ('+str(unique_index)+','+'"'+str(REFERENCE_ID)+'"'+','+'"'+calls+'"'+','+'"'+clean_text(items["entity"])+'"'+','+'"'+clean_text(items["phrase"])+'"'+','+'"'+items["sentiment"]+'"'+")")
	    #print(query)
	    #cursor.execute(query)
	    #db.commit()
            #escalation.write("%d|%s|%s|%s|%s|%s|%s|%s|%f|%s|%f\n"%(unique_index,base_ref,collated_ref,incident_thread_id,thread_created,calls,nlp[0]["escalation"]["result"]["current_escalation"]["result"],nlp[0]["escalation"]["result"]["current_escalation"]["scores"][nlp[0]["escalation"]["result"]["current_escalation"]["result"]],nlp[0]["escalation"]["result"]["previously_escalated"]["result"],nlp[0]["escalation"]["result"]["previously_escalated"]["scores"][nlp[0]["escalation"]["result"]["previously_escalated"]["result"]]))
        escalation.write("%d|%d|%s|%s|%s|%s|%s|%f|%s|%f\n"%(unique_index,rank,channel,collated_ref,incident_thread_id,calls,nlp[0]["escalation"]["result"]["current_escalation"]["result"],nlp[0]["escalation"]["result"]["current_escalation"]["scores"][nlp[0]["escalation"]["result"]["current_escalation"]["result"]],nlp[0]["escalation"]["result"]["previously_escalated"]["result"],nlp[0]["escalation"]["result"]["previously_escalated"]["scores"][nlp[0]["escalation"]["result"]["previously_escalated"]["result"]]))
        #print "FFFF"
        sentiment.write("%d|%d|%s|%s|%s|%s|%s|%f\n"%(unique_index,rank,channel,collated_ref,incident_thread_id,calls,nlp[0]["sentiment"]["result"],nlp[0]["sentiment"]["scores"][nlp[0]["sentiment"]["result"]]))
        pContexts= nlp[0]["problemDetection"]["context"]
        pContexts.extend(nlp[0]["problemDetection"]["contextDomainNoun"])
        if pContexts.__len__():
            for indp,context in enumerate(pContexts):
                problemDetection.write("%d|%d|%s|%s|%s|%s|%s|%d|%f\n"%(unique_index,rank,channel,collated_ref,incident_thread_id,calls,context,nlp[0]["problemDetection"]["result"],nlp[0]["problemDetection"]["scores"][str(nlp[0]["problemDetection"]["result"])]))
        else:
            problemDetection.write("%d|%d|%s|%s|%s|%s|%s|%d|%f\n"%(unique_index,rank,channel,collated_ref,incident_thread_id,calls,"",nlp[0]["problemDetection"]["result"],nlp[0]["problemDetection"]["scores"][str(nlp[0]["problemDetection"]["result"])]))
    #getting the modifiers
        res=mt._mtNLPipeline(calls)
        ver=mcwa.findNounrelatedKeyVerbs(res)
        adj=mcwa.findNounIntensifyingAdj(res)
    #cleaning the ver and adj keys:
        ver1={}
        for key in ver.keys():
            key1=key[:-2]
            key1 = key1.replace("_NG_"," ")
            ver1[key1] = ver[key]

        adj1={}
        for key in adj.keys():
            key1=key[:-2]
            key1 = key1.replace("_NG_"," ")
            adj1[key1] = adj[key]

        for words in nlp[0]["keywords"]["result"]:
            modifiers=[]
            if ver1.has_key(words):
                modifiers.extend(ver1[words])
            if adj1.has_key(words):
                modifiers.extend(adj1[words])
            mod = " ".join(modifiers) 
            keywords.write("%d|%d|%s|%s|%s|%s|%s|%s\n"%(unique_index,rank,channel,collated_ref,incident_thread_id,calls,words,clean_text(mod)))
    except:
        continue
    
        
entitySentiment.close()
escalation.close()
sentiment.close()
problemDetection.close()
keywords.close()
#cursor.close()        
path_dataset = sentimentPath

data =  pd.read_csv(path_dataset,sep="|",encoding="latin")
data["predicted_overall_sentiment"] = ""

uniq =  data.unique_index.unique()

for ind,index in enumerate(uniq):
    print(ind) 
    subset = data[data.unique_index == index]
    index_for_os = subset.index[subset.index.__len__()-1]
    current_sentence_sentiment = subset.sentiment
    sent_senti_under_consideration = current_sentence_sentiment[-5:]
    overall_sentiment = "neutral"
    if "positive" in sent_senti_under_consideration.value_counts().keys() and sent_senti_under_consideration.value_counts()["positive"] > 3:
        overall_sentiment = "positive"
    elif "negative" in sent_senti_under_consideration.value_counts().keys() and  sent_senti_under_consideration.value_counts()["negative"] > 3:
        overall_sentiment = "negative"
    elif "positive" in sent_senti_under_consideration[-3:].value_counts().keys() and sent_senti_under_consideration[-3:].value_counts()["positive"] == 3:
        overall_sentiment = "positive"
    elif "negative" in sent_senti_under_consideration[-3:].value_counts().keys() and sent_senti_under_consideration[-3:].value_counts()["negative"] == 3:
        overall_sentiment = "negative"
    elif "positive" in sent_senti_under_consideration[-2:].value_counts().keys() and sent_senti_under_consideration[-2:].value_counts()["positive"] == 2 and "neutral" in sent_senti_under_consideration.value_counts().keys() and sent_senti_under_consideration.value_counts()["neutral"] >= 2:
        overall_sentiment = "positive"
    elif "negative" in sent_senti_under_consideration[-2:].value_counts().keys() and sent_senti_under_consideration[-2:].value_counts()["negative"] >= 1:
        overall_sentiment = "negative"
    elif "negative" in sent_senti_under_consideration.value_counts().keys() and "positive" in sent_senti_under_consideration.value_counts().keys() and sent_senti_under_consideration.value_counts()["negative"] >= sent_senti_under_consideration.value_counts()["positive"]:
        overall_sentiment = "negative"
    elif "negative" in sent_senti_under_consideration.value_counts().keys() and "positive" not in sent_senti_under_consideration.value_counts().keys():
        overall_sentiment = "negative"
    elif "positive" in sent_senti_under_consideration.value_counts().keys() and "negative" not in sent_senti_under_consideration.value_counts().keys() and sent_senti_under_consideration.value_counts()["positive"] >= 1:
        overall_sentiment = "positive"
    
    data.ix[index_for_os,"predicted_overall_sentiment"] = overall_sentiment
        
   
data.to_csv("".join((text_mine_output_path,name_of_transcript_file,"/sentiment_with_os.csv")),encoding = "latin")

print(data.shape)
print(data.sentiment)
print("completed the text mining processing")


data =  pd.read_csv(escalationPath,sep="|",encoding="latin")
del data['current_esc_prob']
del data['previous_esc_prob']
del data['unique_index']
data.to_csv("".join((text_mine_output_path,name_of_transcript_file,"/escalation.csv")),encoding = "latin",index = False)
data =  pd.read_csv(sentimentPath,sep="|",encoding="latin")
del data['unique_index']
data.to_csv("".join((text_mine_output_path,name_of_transcript_file,"/sentiment.csv")),encoding = "latin",index = False)
data =  pd.read_csv(problemDetectionPath,sep="|",encoding="latin")
del data['unique_index']
data.to_csv("".join((text_mine_output_path,name_of_transcript_file,"/problemDetection.csv")),encoding = "latin",index = False)
data =  pd.read_csv(keywordsPath,sep="|",encoding="latin")
del data['unique_index']
data.to_csv("".join((text_mine_output_path,name_of_transcript_file,"/keywords.csv")),encoding = "latin",index = False)
data =  pd.read_csv(entitySentimentPath,sep="|",encoding="latin")
del data['unique_index']
data.to_csv("".join((text_mine_output_path,name_of_transcript_file,"/entitySentiment.csv")),encoding = "latin",index = False)
import os
data =  pd.read_csv(entitySentimentPath,sep="|",encoding="latin")
os.remove("".join((text_mine_output_path,name_of_transcript_file,"/entitySentiment.csv")))
os.remove("".join((text_mine_output_path,name_of_transcript_file,"/keywords.csv")))
os.remove("".join((text_mine_output_path,name_of_transcript_file,"/sentiment.csv")))
endTime = time.time()

print "Total Time Taken is ",endTime-startTime, "seconds"
