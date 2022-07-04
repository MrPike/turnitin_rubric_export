# Turnitin Rubric Export Tool
This simple application allows teachers who use Turnitin's Grademark rubric tool for grading assessments to export from Turnitin's property '.rbc' format to HTML, 
which may then be distributed to students.


## Installation
This project has a single dependency - [Jinja2](http://jinja.palletsprojects.com), which can be install this using the `pip` command:

```shell
pip3 install Jinja2
```

It's recommended, however, that you use [Poetry](https://python-poetry.org) to resolve the application's dependencies:

```shell
poetry install
```

## Usage
Having created your assessment's rubric using Turnitin, export it by clicking the "Share" icon (top-right corner of the rubric editor interface) and select "Export...".
This will result in a '.rbc' file being downloaded.

If you're using Poetry, run:
```shell
poetry shell
python3 turnitin_rubric_export.py myRubric.rbc outputFile.html
```
otherwise, just execute the second line (`python3 ....`).

