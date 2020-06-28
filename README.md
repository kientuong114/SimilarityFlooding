# Similarity Flooding

Python3 implementation of the Similarity Flooding algorithm (S. Melnik, H. Garcia-Molina, E. Rahm "Similarity Flooding: A Versatile Graph Matching Algorithm")

## Table of Contents
1. [Project Description](#project-description)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Credits](#credits)

## Project Description

The project implements the Similarity Flooding algorithm as explained in the paper "Similarity Flooding: A Versatile Graph Matching Algorithm", by S. Melnik, H Garcia-Molina and E. Rahm.
The implementation is written in Python3, relying mostly on the [NetworkX](https://networkx.github.io/) library to easily create the necessary graphs.

The project is separated in various modules that should be imported separately, for additional information refer to the [Usage section](#usage).

This work has been done for the "Progetto di Ingegneria Informatica" course (Computer Engineering Project) in Politecnico di Milano.

## Installation

Python3 is required to run the project, please refer to the [Python website](https://www.python.org/downloads/) for additional information on how to install Python.

It is advised to use Pipenv to manage the project dependencies:

If you do not have Pipenv installed:
```
$ pip install pipenv
```

After installing pipenv, move to the project directory and install the required dependencies:

```
$ cd SimilarityFlooding
$ pipenv install
```

You should now be able to run the `main.py` file:

```
$ pipenv run python3 main.py
```

## Usage

The modules contained in the top level package `similarityflooding` are the following:
- `parse`: contains all parser for various schema formats (Namely: SQL DDL, XML and XDR)
- `initialmap`: contains the modules required to compute the initial mapping for the algorithm
- `sf`: contains the modules required for the actual similarity flooding computation
- `filter`: contains the modules required to compute the final results
- `utils`: contains various modules useful to the entire project

In general the flow is the following:
- Choose a parse module to receive a graph from the desired schema format
- Eventually compress the graph (see the report for additional information)
- Create a `SFGraphs` object
- Run the similarity flooding algorithm by providing the `SFGraphs` object
- Execute the final filter

For an example usage, please refer to the `main.py` file.

## Credits

- [Stefan Djokovic](https://github.com/StefanDjokovic): ste dot djokovic at gmail dot com
- [Kien Tuong Truong](https://github.com/kientuong114): kientuong at gmail dot com
