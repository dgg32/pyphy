import sqlite3
import shutil
import os
import configparser
import sys

db = "./ncbi.db"

config_file = os.path.join(os.path.dirname(os.path.realpath(__file__) ),'pyphy.config')

if os.path.exists(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)


    db = config['DEFAULT']['db']


#print (db)

unknown = -1
no_rank = "no rank"

#pyphy.getTaxidByName("Bacteria",1)
def getTaxidByName(name,limit=1, synonym=True):
    """get taxid given a taxonomic name or a synonym
    
    Args:
        name (str): query taxonomic name
        limit (int, optional): how many taxid to return
        synonym (bool, optional): should a synonym search be performed
    
    Returns:
        list: return a list of taxid if the name is found otherwise a list of unknown
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    command = "SELECT taxid FROM tree WHERE name = '" + str(name).replace("'", "''") +  "';"

    cursor.execute(command)
    results = cursor.fetchall()
    
    
    temp = []
    for result in results:
        temp.append(result[0])
    
    if len(temp) != 0:
        temp.sort()
        cursor.close()
        return temp[:limit]
    elif synonym == True:
  
        command = "SELECT taxid FROM synonym WHERE name = '" + str(name).replace("'", "''") +  "';"
        cursor.execute(command)
        results = cursor.fetchall()
        cursor.close()
        temp = []

        for result in results:
            temp.append(result[0])

        if len(temp) != 0:
            temp.sort()
            return temp[:limit]

        else:
            return [unknown]

    else:
        cursor.close()
        return [unknown]
    
#pyphy.getRankByTaxid("2")
def getRankByTaxid(taxid):
    """get the rank given a taxid
    
    Args:
        taxid (int or str):query taxid
    
    Returns:
        str: the rank of the taxid
    """
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    command = "SELECT rank FROM tree WHERE taxid = '" + str(taxid) +  "';"
    cursor.execute(command)
       
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return no_rank


def getRankByName(name, synonym=True):
    """get the rank given a taxonomic name or a synonym
    
    Args:
        name (str): query taxonomic name
        synonym (bool, optional): should a synonym search be performed
    
    Returns:
        str: the rank of the name if found otherwise no_rank
    """
    try:
        return getRankByTaxid(getTaxidByName(name, 1, synonym)[0])
    except:
        return no_rank



#pyphy.getNameByTaxid("2")
def getNameByTaxid(taxid):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    command = "SELECT name FROM tree WHERE taxid = '" + str(taxid) +  "';"
    cursor.execute(command)
    
    result = cursor.fetchone()
    cursor.close()   
    if result:
        return result[0]
    else:
        return "unknown"

def getAllNameByTaxid(taxid):
    result = []
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    command = "SELECT name FROM tree WHERE taxid = '" + str(taxid) +  "';"
    cursor.execute(command)
    
    name = cursor.fetchone()
       
    if name:
        result.append(name[0])
    
    command = "SELECT name FROM synonym WHERE taxid = '" + str(taxid) +  "';"
    cursor.execute(command)
    
    names = cursor.fetchall()
    cursor.close()   
    for name in names:
        result.append(name[0])

    if len(result) != 0:
        return result
    else:
        return ["unknown"]
    

def getParentByTaxid(taxid):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    command = "SELECT parent FROM tree WHERE taxid = '" + str(taxid) +  "';"
    cursor.execute(command)
    
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return unknown
    

#pyphy.getParentByName("Flavobacteriia")
def getParentByName(name, synonym=True):

    try:
        return getParentByTaxid(getTaxidByName(name, 1, synonym)[0])
    except:
        return unknown
    

def getPathByTaxid(taxid):
    path = []
    
    current_id = int(taxid)
    path.append(current_id)
    
    while current_id != 1 and current_id != unknown:
        #print current_id
        current_id = int(getParentByTaxid(current_id))
        path.append(current_id)
    
    return path[::-1]


def getDictPathByTaxid(taxid):
    path = {}

    current_id = int(taxid)
    rank = getRankByTaxid(current_id)
    path[rank] = current_id
    
    while current_id != 1 and current_id != unknown:
        #print current_id
        current_id = int(getParentByTaxid(current_id))
        rank = getRankByTaxid(current_id)

        path[rank] = current_id
    
    return path

    
def getTaxidByGi(gi, molecule="protein"):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    command = "SELECT taxid FROM gi_taxid WHERE gi = '" + str(gi) +  "';"
    if molecule=="dna":
        command = "SELECT taxid FROM nt_gi_taxid WHERE gi = '" + str(gi) +  "';"
    cursor.execute(command)
    
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return unknown
    
    
def getSonsByTaxid(taxid):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    command = "SELECT taxid FROM tree WHERE parent = '" + str(taxid) +  "';"
    result = [row[0] for row in cursor.execute(command)]
    cursor.close()
    return result


def getSonsByName(name, synonym=False):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    command = "SELECT taxid FROM tree WHERE parent = '" + str(getTaxidByName(name, 1, synonym)[0]) +  "';"
    result = [row[0] for row in cursor.execute(command)]
    cursor.close()
    return result


#If you create your database in a thread usually the main thread 
#and try to use it in another thread your will get: ProgrammingError: SQLite objects 
#created in a thread can only be used in that same thread. The object was created in 
#thread id SOME_ID and this is thread id SOME_ID. This is because you created the 
#cursor object in the main thread, 
#if you for example create only the connection object in the main thread and create 
#cursors when you want to query the database

def getGiByTaxid(taxid, molecule="protein"):
    conn = sqlite3.connect(db)
    command = "SELECT gi FROM gi_taxid WHERE taxid = '" + str(taxid) +  "';"
    if molecule == "dna":
        command = "SELECT gi FROM nt_gi_taxid WHERE taxid = '" + str(taxid) +  "';"
    cursor = conn.cursor()
    #print command
    try:
        result = [row[0] for row in cursor.execute(command)] 
        
        cursor.close()
        return result
    except:
        pass



#getAllSonsByTaxid legacy code, single thread = slow
#def getAllSonsByTaxid(taxid):
#    sons_for_result = [son for son in getSonsByTaxid(taxid)]
#    sons_for_search = [son for son in getSonsByTaxid(taxid)]
#    
#    for son in sons_for_search:
#        sons_for_result += getAllSonsByTaxid(son)
#    #print sons_for_result
#    return sons_for_result

def getTaxidByRef(ref):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    command = "SELECT taxid FROM nt_ref_taxid WHERE ref = '" + str(ref) +  "';"

    cursor.execute(command)
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    else:
        return unknown

def getAllSonsByTaxid(taxid):


    from threading import Thread
    import queue
    in_queue = queue.Queue()
    out_queue = queue.Queue()
    
    def work():
        while True:
            sonId = in_queue.get()
#
#if here use getAllSonsByTaxid, it will be true recursive,
#but it will run over the thread limit set by the os by trying "Flavobacteriia" (6000+)
#error: can't start new thread
#it is more elegant here

            for s_s_id in getSonsByTaxid(sonId):
                #print "s_s_id" + str(s_s_id)
                out_queue.put(s_s_id)
                in_queue.put(s_s_id)

       
            in_queue.task_done()
    
    for i in range(20):
        
        t = Thread(target=work)
        t.daemon = True
        t.start()
    

    for son in getSonsByTaxid(taxid):
        out_queue.put(son)
        in_queue.put(son)
        
    
    in_queue.join()   
 
    result = []
    
    while not out_queue.empty():
        
        result.append( out_queue.get())

    #print result
    return result
    


def getAllGiByTaxid(taxid):

    #import multiprocessing
    from threading import Thread
    import queue
    in_queue = queue.Queue()
    out_queue = queue.Queue()

    #queue = multiprocessing.Queue()
    #out_queue = multiprocessing.Queue()

    allSons = getAllSonsByTaxid(taxid)

    
    def work():
        while True:
            sonId = in_queue.get()
            out_queue.put(getGiByTaxid(sonId))
            in_queue.task_done()


    for i in range(20):
        
        t = Thread(target=work)
        #not daemon no exit in interpretor and script mode
        t.daemon = True

        #t = multiprocessing.Process(target=work, args=(queue,out_queue))
        #t.daemon=True

        #t = Worker(queue)

        t.start()
        
    in_queue.put(taxid)
    for son in allSons:
        in_queue.put(son)
        
    
    in_queue.join()        
    
    result = []

    while not out_queue.empty():
        
        result += out_queue.get()
   
    #print "time: " + str(time.time()-start)
    return result
    
    
    
if __name__ == '__main__':
    pass
    