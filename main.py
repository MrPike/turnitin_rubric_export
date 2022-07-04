import argparse
import json
from pathlib import Path
from typing import Union

from jinja2 import Template


def validate_rubric_path_exists(in_path: Path) -> Union[Path, FileNotFoundError]:
    if in_path.exists() and in_path.is_file():
        return in_path.absolute()
    else:
        raise FileNotFoundError(f'The specified Turnitin Rubric file ({in_path}), could not be found.')


def parse_args() -> argparse.Namespace:
    """
    Parses user provided command line arguments to the program.
    :return: A dictionary-like object containing user's arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('input_rubric', type=lambda p: validate_rubric_path_exists(Path(p)),
                        help="A valid Turnitin Rubric File (.rbc).")
    parser.add_argument('output_rubric', type=lambda p: Path(p).absolute(),
                        help="An output path for the exported rubric (.html)")
    parser.add_argument('--template', type=lambda p: Path(p).absolute(), default=Path('templates/turnitin.html'),
                        help="HTML file containing the output template.")

    args = parser.parse_args()

    return args


def load_rubric(rubric_path: Path) -> dict:
    """
    Validates that the specified rubric file is valid and trans-morphs it's values into a more template friendly format.
    :param rubric_path: The path to the rubric file to be parsed
    :return: A dictionary containing the title, header, rows and scales of the rubric.
    """
    if not rubric_path.exists():
        raise FileNotFoundError(f'The specified Turnitin Rubric file ({rubric_path}), could not be found.')

    # The rubric file is actually just JSON. Ensure it parses accordingly.
    try:
        rubric = json.loads(rubric_path.read_text())
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f'Error parsing the specified Turnitin Rubric file ({rubric_path}. '
                                   f'The following error was generated: \n {e}')

    # Ensure all the keys we need to work with are present
    if not all(k in rubric.keys() for k in ('Rubric', 'RubricScale', 'RubricCriterion', 'RubricCriterionScale')):
        raise KeyError('Expected key not found in rubric file. Is this a Turnitin rubric?')

    # Ensure that the all expected fields are present
    if not len(rubric['Rubric']) == 1 and len(rubric['RubricScale']) > 0 and len(rubric['RubricCriterion']) > 0 and \
            (len(rubric['RubricScale']) * len(rubric['RubricCriterion'])) == len(rubric['RubricCriterionScale']):
        raise ValueError(f'Rubric is not valid. There is a mismatch between the expected and actual number '
                         f'of rubric items present in {rubric_path}.')

    # The "left-hand side" of the resulting matrix, showing each criterion, it's weight and description.
    index = [{'criterion': rc['name'], 'weight': rc['value'], 'description': rc['description']} for rc in
             rubric['RubricCriterion']]
    # A lookup table used to pair id's to individual rubric criterion scale descriptors (an item within the matrix)
    values = {v['id']: v['description'] for v in rubric['RubricCriterionScale']}
    # The resulting matrix
    matrix = [[values[criterion_scale] for criterion_scale in RubricCriterion['criterion_scales']]
              for RubricCriterion in rubric['RubricCriterion']]

    return {'title': rubric['Rubric'][0]['name'], 'header': rubric['RubricScale'], 'rows': list(zip(index, matrix)),
            'scale': rubric['RubricCriterion']}


def export_rubric(rubric: dict, out_path: Path, template: Path) -> None:
    """
    Exports the parsed rubric using the specified template, with the result being written to disk.
    :param rubric: The parsed rubric file to be written.
    :param out_path: The location where the result should be saved.
    :param template: The template file against which the rubric values will be rendered.
    """

    if not template.exists() and template.is_file():
        raise FileNotFoundError(f'Specified template file ({template}) not found.')

    out_path.parent.mkdir(exist_ok=True, parents=True)
    t = Template(template.read_text())
    out_path.write_text(t.render(rubric=rubric))


if __name__ == '__main__':
    args = parse_args()
    export_rubric(load_rubric(args.input_rubric), args.output_rubric, args.template)
