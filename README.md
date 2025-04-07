GKE Filesystem Comparative Benchmarking
=======================================

This is some data collected with iozone about the relative performance
of filestore over NFSv3, Cloud NetApp Volumes over NFSv3, and
Cloud NetApp Volumes over NFSv4.

Virtualenv for viewing results
------------------------------

Install a local jupyterlab environment however you like to (`python -m
venv`), `mkvirtualenv`, `uv venv`, whatever).  Then 
`pip install -r requirements.txt` (or `uv pip install`...)

After that, just run `jupyter lab`, select `comparison.ipynb`, and run
it.

Note that in the last cell, you have the opportunity to plot either
raw performance or the ratio of performance for the various
technologies, and the opportunity to choose different read and write
strategies.  In my experience, choosing one of the two plots, and
comparing just two strategies works the best: Plotly is a fantastic
tool, but it creates a lot of Javascript and uses a lot of memory, and
can easily crush a smallish laptop like mine.

