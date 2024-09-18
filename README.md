# Research

This repository contains working scripts using the [autogen framework](https://github.com/microsoft/autogen.git)

## Prerequisites

Before setting up the project, ensure that you have the following software installed on your system:

1. **Poetry installed**
2. a .env file in the root of this directory containing the following API keys:
    ```bash
    OPENAI_API_KEY=
    ANTHROPIC_API_KEY=
    ```

## configuring the environment
navigate to the project root directory (i.e. here) and run the following:
    ```
    poetry install
    ```
this will create the virtual environment. In order to activate the environment run ```poetry shell``` alternatively the python entry points can be run by using ```poetry run python <script_name.py>```
