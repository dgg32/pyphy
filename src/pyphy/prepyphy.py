import sys, sqlite3, os
import configparser

#python prepyphy.py folder db

if len(sys.argv) != 3:
    print("Usage: python prepyphy.py [ncbi_download_folder] [db_path]")
    sys.exit(1)

#taxid : Node
tree = {}

taxid_synonym = {}

folder = sys.argv[1]
db_path = sys.argv[2]

config_file = os.path.join(os.path.dirname(os.path.realpath(__file__) ),'pyphy.config')

config = configparser.ConfigParser()
if os.path.exists(config_file):
    config.read(config_file)

# always record where the freshly built database lives (as an absolute
# path, so it keeps resolving after pyphy is imported from another cwd),
# even on a first run where pyphy.config doesn't exist yet.
config["DEFAULT"]["db"] = os.path.abspath(db_path)
if "threads" not in config["DEFAULT"]:
    config["DEFAULT"]["threads"] = "20"

with open(config_file, 'w') as cfgfile:
    config.write(cfgfile)


if not folder.endswith("/"):
    folder += "/"


names_dmp = folder + "names.dmp"
#process the names.dmp
with open(names_dmp, 'r') as f:
    for line in f:
        fields = line.strip().split("\t")
        notion = fields[6]
        taxid = fields[0]
        name = fields[2]

        if notion== "scientific name":
            #tree[taxid] = None or [name,"0",""]
            if taxid not in tree:
                tree[taxid] = [name,"0",""]
        elif notion== "synonym" or notion == "equivalent name":
            if taxid not in taxid_synonym:
                taxid_synonym[taxid] = set()

            taxid_synonym[taxid].add(name)

            #synonym_taxid[name] = None or taxid


nodes_dmp = folder + "nodes.dmp"
#process the nodes.dmp
with open(nodes_dmp, 'r') as f:
    for line in f:
        fields = line.strip().split("\t")

        taxid = fields[0]
        parent = fields[2]
        rank = fields[4]

        if taxid in tree:
            tree.get(taxid)[1] = parent
            tree.get(taxid)[2] = rank


conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('''PRAGMA journal_mode = OFF''')

# drop any pre-existing tables so re-running this script to refresh the
# taxonomy (as recommended in the README) doesn't crash with
# "table already exists" on the second run.
cursor.execute("DROP TABLE IF EXISTS tree;")
cursor.execute("CREATE TABLE tree (taxid integer, name text, parent integer, rank text);")

cursor.executemany(
    "INSERT INTO tree VALUES (?, ?, ?, ?);",
    ((taxid, node[0], node[1], node[2]) for taxid, node in tree.items()),
)

###indexing

cursor.execute("CREATE UNIQUE INDEX taxid_on_tree ON tree(taxid);")
cursor.execute("CREATE INDEX name_on_tree ON tree(name);")
cursor.execute("CREATE INDEX parent_on_tree ON tree(parent);")


####synonym table

cursor.execute("DROP TABLE IF EXISTS synonym;")
cursor.execute("CREATE TABLE synonym (id integer, taxid integer, name text);")

def _synonym_rows():
    index = 0
    for taxid, names in taxid_synonym.items():
        for name in names:
            yield (index, taxid, name)
            index += 1

cursor.executemany("INSERT INTO synonym VALUES (?, ?, ?);", _synonym_rows())

cursor.execute("CREATE INDEX name_on_synonym ON synonym(name);")
cursor.execute("CREATE INDEX taxid_on_synonym ON synonym(taxid);")

conn.commit()
conn.close()
