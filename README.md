# pyphy
Python library that interacts with NCBI taxonomy 

This is the Python implementation of the blog post http://dgg32.blogspot.com/2013/07/pyphy-wrapper-program-for-ncbi-sqlite.html.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites


 
```
sqlite
```


## Preparing the backend database

Notice: please perform this step periodically to stay up to date with the NCBI Taxonomy.

Download the taxdmp.zip from ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/ and unzip it.

```
python prepyphy.py [ncbi_download_folder] [db_path]
```

This step will set up the "db_path" in pyphy.config automatically.

If you move the database afterwards, please don't forget to refresh db_path in pyphy.config.


### Using the library

Install the library via pip

```
pip install pyphy
```

Use pip show to show the package location. Copy the value in "Location"

```
pip show pyphy 
```

For example, mine is /Users/dgg32/opt/anaconda3/envs/dbt/lib/python3.8/site-packages.

Then run prepyphy.py to prepare the database. It is in your "Location/" + pyphy folder.
```
python [location of your prepyphy.py] [location of taxdmp] [location_you_want_to_put_your_ncbi_database]

```

For example, mine is 

```
python /Users/dgg32/opt/anaconda3/envs/dbt/lib/python3.8/site-packages/pyphy/prepyphy.py /Users/dgg32/Downloads/taxdump /Users/dgg32/opt/anaconda3/envs/dbt/lib/python3.8/site-packages/pyphy/ncbi

```


Then you can import the pyphy library in your Python code by


```
import pyphy
```

pyphy provides the following queries inside the NCBI taxonomy:

Taxonomy name <-> NCBI TaxID

NCBI TaxID -> Full lineage

NCBI TaxID -> Taxonomic rank

NCBI TaxID -> all children

For code examples and documentation please refer to documentations.


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


