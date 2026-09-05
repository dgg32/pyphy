import sqlite3
import os
import configparser

db = "./ncbi.db"
threads = 20  # kept for backward compatibility; no longer used internally

config_file = os.path.join(os.path.dirname(os.path.realpath(__file__) ),'pyphy.config')

if os.path.exists(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)

    db = config['DEFAULT'].get('db', db)
    threads = int(config['DEFAULT'].get('threads', threads))


#print (db)

unknown = -1
no_rank = "no rank"


def _connect():
    """open a new connection to the configured NCBI taxonomy database"""
    return sqlite3.connect(db)


def _fetchall(command, params=()):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(command, params)
        return cursor.fetchall()
    finally:
        conn.close()


def _fetchone(command, params=()):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(command, params)
        return cursor.fetchone()
    finally:
        conn.close()


def _to_taxid(value):
    """best-effort conversion of a taxid-like value to int, falling back to `unknown`"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return unknown


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
    rows = _fetchall("SELECT taxid FROM tree WHERE name = ? ORDER BY taxid;", (str(name),))
    temp = [row[0] for row in rows]

    if len(temp) != 0:
        return temp[:limit]
    elif synonym:
        rows = _fetchall("SELECT taxid FROM synonym WHERE name = ? ORDER BY taxid;", (str(name),))
        temp = [row[0] for row in rows]

        if len(temp) != 0:
            return temp[:limit]
        else:
            return [unknown]
    else:
        return [unknown]

#pyphy.getRankByTaxid("2")
def getRankByTaxid(taxid):
    """get the rank given a taxid

    Args:
        taxid (int or str):query taxid

    Returns:
        str: the rank of the taxid
    """
    result = _fetchone("SELECT rank FROM tree WHERE taxid = ?;", (str(taxid),))
    return result[0] if result else no_rank


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
    except (sqlite3.Error, IndexError):
        return no_rank



def getNameByTaxid(taxid):
    """get taxonomic name given a taxid

    Args:
        taxid (str or int): query taxid


    Returns:
        str: return a taxonomic name if it is found otherwise unknown
    """
    result = _fetchone("SELECT name FROM tree WHERE taxid = ?;", (str(taxid),))
    return result[0] if result else "unknown"

def getAllNameByTaxid(taxid):
    """get taxonomic names and synonyms given a taxid

    Args:
        taxid (str or int): query taxid


    Returns:
        list: return a list taxonomic names and synonyms if it is found otherwise unknown
    """
    result = []
    conn = _connect()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM tree WHERE taxid = ?;", (str(taxid),))
        name = cursor.fetchone()
        if name:
            result.append(name[0])

        cursor.execute("SELECT name FROM synonym WHERE taxid = ?;", (str(taxid),))
        result.extend(row[0] for row in cursor.fetchall())
    finally:
        conn.close()

    return result if len(result) != 0 else ["unknown"]


def getParentByTaxid(taxid):
    """get parent taxid given a taxid

    Args:
        taxid (str or int): query taxid


    Returns:
        int: return the parent taxid if it is found otherwise unknown
    """
    result = _fetchone("SELECT parent FROM tree WHERE taxid = ?;", (str(taxid),))
    return result[0] if result else unknown


#pyphy.getParentByName("Flavobacteriia")
def getParentByName(name, synonym=True):
    """get parent taxid given a taxonomic name

    Args:
        name (str): query name


    Returns:
        list: return the parent taxid if it is found otherwise unknown
    """

    try:
        return getParentByTaxid(getTaxidByName(name, 1, synonym)[0])
    except (sqlite3.Error, IndexError):
        return unknown


def getPathByTaxid(taxid):
    """get the taxonomic path given a taxid

    Args:
        taxid (str or int): query taxid


    Returns:
        list: return a list of parent taxid if it is found otherwise an empty list
    """

    current_id = _to_taxid(taxid)
    path = [current_id]

    conn = _connect()
    try:
        cursor = conn.cursor()
        while current_id != 1 and current_id != unknown:
            cursor.execute("SELECT parent FROM tree WHERE taxid = ?;", (str(current_id),))
            row = cursor.fetchone()
            current_id = int(row[0]) if row else unknown
            path.append(current_id)
    finally:
        conn.close()

    return path[::-1]


def getDictPathByTaxid(taxid):
    """get the taxonomic path with the ranks as keys given a taxid

    Args:
        taxid (str or int): query taxid


    Returns:
        dict: return a dict of rank: parent taxid if it is found otherwise an empty dict
    """

    current_id = _to_taxid(taxid)
    path = {}

    conn = _connect()
    try:
        cursor = conn.cursor()

        def rank_of(tid):
            cursor.execute("SELECT rank FROM tree WHERE taxid = ?;", (str(tid),))
            row = cursor.fetchone()
            return row[0] if row else no_rank

        path[rank_of(current_id)] = current_id

        while current_id != 1 and current_id != unknown:
            cursor.execute("SELECT parent FROM tree WHERE taxid = ?;", (str(current_id),))
            row = cursor.fetchone()
            current_id = int(row[0]) if row else unknown
            path[rank_of(current_id)] = current_id
    finally:
        conn.close()

    return path


def getSonsByTaxid(taxid):
    """get the 1st-level sons given a taxid

    Args:
        taxid (str or int): query taxid


    Returns:
        list: return a list of son taxid if it is found otherwise an empty list
    """
    return [row[0] for row in _fetchall("SELECT taxid FROM tree WHERE parent = ?;", (str(taxid),))]


def getSonsByName(name, synonym=False):
    """get the 1st-level sons given a taxonomic name

    Args:
        name (str): query name


    Returns:
        list: return a list of son taxid if it is found otherwise an empty list
    """
    return getSonsByTaxid(getTaxidByName(name, 1, synonym)[0])



def getAllSonsByTaxid(taxid):
    """get the sons of all levels given a taxid

    Args:
        taxid (str or int): query taxid


    Returns:
        list: return a list of son taxid if it is found otherwise an empty list
    """

    current_id = _to_taxid(taxid)

    # a single recursive query lets sqlite walk the whole subtree in one
    # shot instead of the old per-node BFS that spun up a fresh Python
    # thread pool (and a fresh sqlite connection per node) on every call.
    command = """
        WITH RECURSIVE descendants(taxid) AS (
            SELECT taxid FROM tree WHERE parent = ?
            UNION ALL
            SELECT tree.taxid FROM tree
            JOIN descendants ON tree.parent = descendants.taxid
        )
        SELECT taxid FROM descendants;
    """
    return [row[0] for row in _fetchall(command, (current_id,))]





if __name__ == '__main__':
    pass
