"""Build the tiny, frozen sqlite fixture that test_pyphy.py runs against.

test_pyphy.py used to run against whatever ncbi.db a developer had locally
(via pyphy.config). That db is a live snapshot of NCBI's taxonomy, and NCBI
revises it constantly -- ranks get renamed (e.g. "superkingdom" -> "domain"),
new intermediate ranks get inserted (e.g. "cellular root", "kingdom"), names
get replaced by newer preferred names with the old one demoted to a synonym
(e.g. "Proteobacteria" -> "Pseudomonadota"), and new species get added under
existing genera. Every one of those routine updates could silently turn a
previously-correct assertion into a failure that has nothing to do with a
code regression.

The fix is to stop testing against a moving target: this script extracts
just the handful of real taxa the test suite cares about (plus their real
ancestor chains, synonyms, and children/descendants, exactly as NCBI defines
them) out of a full ncbi.db built by prepyphy.py, and freezes them into
src/pyphy/test_fixture.db, which is committed to the repo. test_pyphy.py
always points pyphy.db at that frozen file, so the suite is deterministic
and never needs a taxdmp download to run.

When you deliberately want the fixture -- and the test assertions -- to
track a newer NCBI release, rebuild it and diff the output against the old
expectations:

    python build_test_fixture.py /path/to/a/fresh/ncbi.db

then update the hardcoded expected values in test_pyphy.py to match.
"""

import sqlite3
import sys
import os

FIXTURE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_fixture.db')

# taxa the test suite touches directly, and what each one needs pulled in
# alongside it. Add an entry here (and a matching assertion in
# test_pyphy.py) whenever a new test starts relying on another taxon.
ANCHORS = {
    2: {"ancestors": True},                        # Bacteria
    1224: {"ancestors": True, "synonyms": True},    # Pseudomonadota / nee Proteobacteria
    976: {"synonyms": True},                        # Bacteroidota / nee Bacteroidetes
    179: {"children": True},                        # Leptospirillum (genus)
    2629551: {"descendants": True},                 # unclassified Leptospirillum
}


def fetch_row(cursor, taxid):
    cursor.execute("SELECT taxid, name, parent, rank FROM tree WHERE taxid = ?", (taxid,))
    return cursor.fetchone()


def fetch_ancestors(cursor, taxid):
    rows = {}
    current = taxid
    while True:
        row = fetch_row(cursor, current)
        if not row:
            break
        rows[row[0]] = row
        if row[0] == row[2] or row[0] == 1:  # root points to itself
            break
        current = row[2]
    return rows


def fetch_children(cursor, taxid):
    cursor.execute("SELECT taxid, name, parent, rank FROM tree WHERE parent = ?", (taxid,))
    return {row[0]: row for row in cursor.fetchall()}


def fetch_descendants(cursor, taxid):
    command = """
        WITH RECURSIVE descendants(taxid) AS (
            SELECT taxid FROM tree WHERE parent = ?
            UNION ALL
            SELECT tree.taxid FROM tree JOIN descendants ON tree.parent = descendants.taxid
        )
        SELECT tree.taxid, tree.name, tree.parent, tree.rank
        FROM tree JOIN descendants ON tree.taxid = descendants.taxid;
    """
    cursor.execute(command, (taxid,))
    return {row[0]: row for row in cursor.fetchall()}


def fetch_synonyms(cursor, taxid):
    cursor.execute("SELECT taxid, name FROM synonym WHERE taxid = ?", (taxid,))
    return cursor.fetchall()


def build(source_db_path, fixture_path=FIXTURE_PATH):
    src = sqlite3.connect(source_db_path)
    src_cursor = src.cursor()

    tree_rows = {}
    synonym_rows = []

    for taxid, needs in ANCHORS.items():
        row = fetch_row(src_cursor, taxid)
        if not row:
            raise SystemExit(f"taxid {taxid} not found in {source_db_path} -- update ANCHORS")
        tree_rows[taxid] = row

        if needs.get("ancestors"):
            tree_rows.update(fetch_ancestors(src_cursor, taxid))
        if needs.get("children"):
            tree_rows.update(fetch_children(src_cursor, taxid))
        if needs.get("descendants"):
            tree_rows.update(fetch_descendants(src_cursor, taxid))
        if needs.get("synonyms"):
            synonym_rows.extend(fetch_synonyms(src_cursor, taxid))

    src.close()

    if os.path.exists(fixture_path):
        os.remove(fixture_path)

    dst = sqlite3.connect(fixture_path)
    cursor = dst.cursor()
    cursor.execute("CREATE TABLE tree (taxid integer, name text, parent integer, rank text);")
    cursor.execute("CREATE TABLE synonym (id integer, taxid integer, name text);")

    cursor.executemany("INSERT INTO tree VALUES (?, ?, ?, ?);", tree_rows.values())
    cursor.executemany(
        "INSERT INTO synonym VALUES (?, ?, ?);",
        ((i, taxid, name) for i, (taxid, name) in enumerate(synonym_rows)),
    )

    cursor.execute("CREATE UNIQUE INDEX taxid_on_tree ON tree(taxid);")
    cursor.execute("CREATE INDEX name_on_tree ON tree(name);")
    cursor.execute("CREATE INDEX parent_on_tree ON tree(parent);")
    cursor.execute("CREATE INDEX name_on_synonym ON synonym(name);")
    cursor.execute("CREATE INDEX taxid_on_synonym ON synonym(taxid);")

    dst.commit()
    dst.close()

    print(f"wrote {len(tree_rows)} tree rows and {len(synonym_rows)} synonym rows to {fixture_path}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python build_test_fixture.py [path_to_a_real_ncbi.db]")
        sys.exit(1)
    build(sys.argv[1])
