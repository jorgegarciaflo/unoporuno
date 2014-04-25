#coding:utf-8

import sys
import langid
import mysql.connector
import nltk
from mysql.connector import errorcode



if __name__=='__main__':

    # text =  '''Join Facebook to connect with Anas Khchaf and
    #         others you may know. Facebook gives people the power to share and makes the
    #         '''

    
    # text = '''This module allows you to search google by scraping the results.\
    #  It does NOT use the Google Search API. PLEASE DO NOT ABUSE THIS.\
    #   The intent of using this is convenience vs the cruft that exists in the Google Search API.'''
    # print text
    # print text.lower()
    # language = detect_language(text.lower())

    # print language


    # test de Mysql db



    
    config = {
       'user': 'root',
       'password': '',
       'host': '127.0.0.1',
       'database': 'unoporuno',
       'raise_on_warnings': True
     }

    # cnx = mysql.connector.connect(**config)
    # cursor = cnx.cursor()
    # query = ("SELECT * FROM `unoporuno_features` ")
    # cursor.execute(query)
    # for (id,snippet_id,type,value) in cursor:
    #     print " {} {} {} ".format(id,snippet_id,type,value)
    # C = cnx.cursor()
    # newD=("INSERT INTO `unoporuno_features` (`snippet_id`,`type`,`value`) VALUES (%s,%s,%s)")
    # d=(1,30,20)
    # C.execute(newD,d)
    # C.close()
    # cursor.close()
    # cnx.commit()
    # cnx.close()
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # query = ("SELECT id, description FROM unoporuno_snippet "
    #           "WHERE id NOT IN (SELECT snippet_id from unoporuno_features) LIMIT 0,10")
    query = ("SELECT s.id, s.description FROM unoporuno_snippet s,  unoporuno_features f \
     WHERE s.id=f.snippet_id and f.value='en' LIMIT 0,1")
    



    cursor.execute(query)

    for (id, description) in cursor:
        print "******************************************"
        print "******************************************"
        description= description.decode('utf8')
        descriptionL = nltk.pos_tag(description.decode('utf8').lower())
        descriptionO = nltk.pos_tag(description)
        print  "Texte brut : " , description
        text = nltk.word_tokenize(description)
        print "Analyse du Text : " , nltk.pos_tag(text)
        text = nltk.word_tokenize(description.lower())
        print "Analyse du Text (Lower): " , nltk.pos_tag(text)
        phrase =  nltk.corpus.treebank.tagged_sents()[22]
        print " chunk : ", nltk.ne_chunk(descriptionL) 
        print "DescriptionL" ,type(descriptionL)
        print "Description" ,type(descriptionO)
        print "Phrase" ,type(phrase)
        # # print "Text Brut : ", description
        # langids = langid.classify(description.lower());
        # # print "langid Classification : " , langids
        # # language = detect_language(description.lower());
        
        # langrec= str(langids[0])
        # stat= str(langids[1])
        # if not(stat) :
        #     stat=0
        # print "******************************************"
        # print "Description : ",description.encode('utf8')

        # print("Langid =>  {} , stat : {} ".format(langrec,stat))
        # # print("nltk   =>  {} ".format(language))
        # print "******************************************"
        # cnxx = mysql.connector.connect(**config)
        # C = cnxx.cursor()
        # NewFeature = ("INSERT INTO  `unoporuno_features` (`snippet_id`,`value`,statistic) VALUES (%s,%s,%s)")
        # FeatureData= (id,langrec,stat,)
        # C.execute(NewFeature,FeatureData)
        # C.close()
        # cnxx.commit()
        # cnxx.close()


    cursor.close()
    cnx.commit()
    cnx.close()
    print "Connexion fermee"
    # except mysql.connector.Error as err:
    #     if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    #         print("Something is wrong with your user name or password")
    #     elif err.errno == errorcode.ER_BAD_DB_ERROR:
    #         print("Database does not exists")
    #     else:
    #         print(err)
    # else:
    #     cnx.close()
    #     print "Connexion fermee"