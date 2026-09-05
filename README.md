# pyphy

A small Python library for querying the NCBI Taxonomy locally, backed by a SQLite database you build once from NCBI's own taxonomy dump. No network calls at query time — once the database is prepared, every lookup is a local, indexed SQLite query.

This is the Python implementation of the approach described in [this blog post](http://dgg32.blogspot.com/2013/07/pyphy-wrapper-program-for-ncbi-sqlite.html).

## Prerequisites

Just Python 3. SQLite support (the `sqlite3` module) ships with the standard library, so there's nothing extra to install.

## Installation

```
pip install pyphy
```

## Preparing the backend database

pyphy queries a local SQLite database built from NCBI's taxonomy dump — you need to build this once before the library can answer anything.

1. Download and unzip `taxdmp.zip` from `ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/`.
2. Find where pip installed pyphy:
   ```
   python -c "import pyphy, os; print(os.path.dirname(pyphy.__file__))"
   ```
3. Run `prepyphy.py` from that location, pointing it at the unzipped dump and at wherever you want the database written:
   ```
   python [pyphy_location]/prepyphy.py [path_to_unzipped_taxdmp] [path_for_the_new_database]
   ```
   For example:
   ```
   python /Users/dgg32/opt/anaconda3/envs/dbt/lib/python3.8/site-packages/pyphy/prepyphy.py \
       /Users/dgg32/Downloads/taxdmp \
       /Users/dgg32/opt/anaconda3/envs/dbt/lib/python3.8/site-packages/pyphy/ncbi.db
   ```

This also writes the database path into `pyphy.config` (next to `prepyphy.py`) automatically, so pyphy finds it without any further setup. NCBI revises the taxonomy regularly, so it's worth re-running this step periodically to stay current — re-running it against an existing database file is safe and just rebuilds it. If you move the database file afterwards, update `db` in `pyphy.config` to match.

## Using the library

```python
import pyphy

pyphy.getTaxidByName("Bacteria")            # [2]
pyphy.getNameByTaxid(2)                     # "Bacteria"
pyphy.getRankByTaxid(1224)                  # "phylum"
pyphy.getParentByTaxid(1224)                # the taxid of 1224's parent
pyphy.getPathByTaxid(1224)                  # [1, 131567, 2, 3379134, 1224] (root -> 1224)
pyphy.getDictPathByTaxid(1224)              # {'phylum': 1224, 'kingdom': 3379134, 'domain': 2, 'cellular root': 131567, 'no rank': 1}
pyphy.getSonsByTaxid(1224)                  # direct children of 1224
pyphy.getAllSonsByTaxid(1224)               # every descendant of 1224, any depth
```

Every `*ByTaxid` lookup has a `*ByName` counterpart that also resolves synonyms by default (e.g. `getRankByName`, `getParentByName`, `getSonsByName`), and every name/taxid lookup returns a documented sentinel (`pyphy.unknown` / `pyphy.no_rank`, or `"unknown"`) rather than raising when nothing matches. See the docstrings in [pyphy.py](src/pyphy/pyphy.py) for the full API and exact return shapes.

## Running the tests

`test_pyphy.py` runs against a small frozen snapshot of real NCBI data checked in as `src/pyphy/test_fixture.db`, not against your live `ncbi.db`. This keeps the suite deterministic: NCBI revises the real taxonomy constantly (renamed ranks, renamed preferred names, new species), so pinning tests to a moving target means an unrelated NCBI update could turn a correct assertion into a failure.

```
python src/pyphy/test_pyphy.py
```

If you deliberately want the fixture (and the test expectations) to track a newer NCBI release, rebuild it from a freshly-prepared `ncbi.db` and update the assertions in `test_pyphy.py` to match:

```
python src/pyphy/build_test_fixture.py [path_to_a_real_ncbi.db]
```

## Authors

* **Sixing Huang** - *Concept and Coding*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
