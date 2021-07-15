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

In order to use the library system wide, put the absolute path of "source" into your PYTHONPATH, 
```
export PYTHONPATH="${PYTHONPATH}:/my/own/pyphy/source/"
```

[source](https://stackoverflow.com/questions/3402168/permanently-add-a-directory-to-pythonpath). 


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


## Authors

* **Sixing Huang** - *Concept and Coding*

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details


