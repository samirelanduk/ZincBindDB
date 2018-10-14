# ZincBind
[![Build Status](https://travis-ci.org/samirelanduk/ZincBind.svg)](https://travis-ci.org/samirelanduk/ZincBind)
[![Coverage Status](https://coveralls.io/repos/github/samirelanduk/ZincBind/badge.svg)](https://coveralls.io/github/samirelanduk/ZincBind)

## About

ZincBind is a database of Zinc Binding Sites. It was made, and is currently maintained, by [Sam Ireland](https://samireland.com/) (that's me!) as part of my PhD.

## Local Use

To spin up your own local version of ZincBind:

1. Download this repository using the button above.
2. Unzip the folder and cd into it.
3. Install requirements with ``pip install -r requirements.txt -r requirements-dev.txt -r requirements-test.txt``.
4. Create the database with ``python manage.py migrate``.
5. Populate the database with ``python scripts/build_db.py; python scripts/cluster.py``.
6. View local site by running ``python manage.py runserver`` and going to http://localhost:8000 in your browser.

Note that ZincBind is a Python 3 application! It does not support Python 2 and if you try to use Python 2 you will have a bad time. In many operating systems the default ``python`` command *still* points to Python 2 for some reason, so you may need to use ``python3`` and ``pip3`` instead.

(Alternatively, and preferably, just use a virtual environment.)
