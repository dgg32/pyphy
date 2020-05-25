# pyphy
Python library that interacts with NCBI taxonomy 

This is the Python implementation of the blog post http://dgg32.blogspot.com/2013/07/pyphy-wrapper-program-for-ncbi-sqlite.html

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites


 
```
sqlite

```

### Installing

Scripts can be run as is without installation.

## Preparing the backend database

Download the taxdmp.zip from ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/ and unzip it.

```
python prepyphy.py [ncbi_download_folder] [db_path]
```

Set the db variable in pyphy.config to db_path.


### Using the library

Once the database is setup, you can import the pyphy library in your Python code by

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

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details


