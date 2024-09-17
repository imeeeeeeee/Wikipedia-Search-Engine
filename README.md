# Wikipedia search engine

This project implements a series of algorithms and utilities for text preprocessing, data filtering, matrix manipulation, and the PageRank algorithm. It is designed to rank pages based on their relevance and process large datasets (Wikipedia in our case) through custom filtering and transformation functions.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)

## Overview

The project focuses on:
- **Text Preprocessing**: Cleaning and splitting large datasets for analysis.
- **Matrix Manipulation**: Handling matrix operations, particularly in relation to PageRank.
- **PageRank Algorithm**: An algorithm used to rank pages or items based on their importance, often applied in search engines.

## Installation

To get started, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/imeeeeeeee/wikipedia-search-engine.git
cd project

# Install dependencies
pip install -r requirements.txt
```

## Dependencies
The project requires the following Python libraries:

- Flask
- Pickle
- re
- numpy
- xml.etree.ElementTree
Make sure you have Python 3.6+ installed.

## Usage

1. Data Preprocessing: You can clean XML files or other datasets by running the `splitter-cleaner.py` script:
```bash
python3 splitter-cleaner.py input.xml output.xml
```
2. PageRank Algorithm: To run the PageRank algorithm and rank the pages:
```bash
python3 pagerank.py
```
3. Server: The project includes a web interface for querying ranked pages. Start the Flask server:
```bash
python3 server.py
```
Then, open your browser and navigate to `http://localhost:8888`.

## File Descriptions
- `custom_pageid.py`: Handles custom mappings of page IDs.
- `dictionary.py`: Contains functions for processing dictionaries, likely related to term frequencies or word lookups.
- `filter.py`: Implements data filtering, used for preprocessing datasets.
- `matrix.py` & `matrix2.py`: Perform matrix operations needed for algorithms like PageRank.
- `pagerank.py`: The core PageRank algorithm implementation.
- `server.py`: Flask server to handle HTTP requests and serve the search results.
- `splitter-cleaner.py`: Cleans and processes text data, including removing unnecessary tags, subtitles, and refs.



