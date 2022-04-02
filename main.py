import argparse
import json
from pathlib import Path
from datetime import datetime

from jinja2 import Template

VERBOSE: bool = False


def progress_update(message: str) -> None:
    if VERBOSE:
        print(f"{datetime.now().strftime('%H:%M:%S')}:: {message}")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=lambda p: Path(p).absolute(), help="The Turnitin rubric file (.rbc) to process.")
    parser.add_argument('output', type=lambda p: Path(p).absolute(), help="The output path of the processed rubric.")
    parser.add_argument('--verbose', type=bool, default=False, help="Displays verbose logs of processing procedure.")
    args = parser.parse_args()
    return args.__dict__


def load_rubric(rubric_path: Path) -> dict:
    progress_update(f"Loading specified rubric: {rubric_path}")

    if rubric_path.exists():
        try:
            rubric = json.loads(rubric_path.read_text())
        except json.JSONDecodeError as e:
            progress_update("Unable to decode specified rubric file. Exiting.")
            raise e

        if {'Rubric', 'RubricScale', 'RubricCriterion', 'RubricCriterionScale'} <= rubric.keys():
            progress_update("All expected keys are present in the specified rubric file.")

            lr, lrs, lrc, lrcs = len(rubric['Rubric']), len(rubric['RubricScale']), len(rubric['RubricCriterion']), \
                                 len(rubric['RubricCriterionScale'])

            if lr == 1 and lrs > 0 and lrc > 0 and (lrs * lrc) == lrcs:
                progress_update("All rubrics items are of the correct length.")
            else:
                m = "Rubric is not valid. Mismatch in the expected versus actual length of rubric fields."
                progress_update(m)
                raise ValueError(m)

            headers = [f"{r['name']} <br/> {r['value']}" for r in rubric['RubricScale']]
            index = []
            for rc in rubric['RubricCriterion']:
                index.append({'criterion': rc['name'], 'weight': rc['value'], 'description': rc['description']})

            values = {}
            for v in rubric['RubricCriterionScale']:
                values[v['id']] = v['description']
            matrix = []
            for c in rubric['RubricCriterion']:
                temp = []
                for cs in c['criterion_scales']:
                    temp.append(values[cs])
                matrix.append(temp)
            final = {
                'name': rubric['Rubric'][0]['name'],
                'header': headers,
                'rows': list(zip(index, matrix))
            }
            return final

    else:
        m = f'The specified rubric ({rubric_path}) was not found.'
        progress_update(f"{m} Exiting.")
        raise FileNotFoundError(m)


def export_rubric(rubric: dict, out_path: Path) -> None:
    t = Template(Path('template.html').read_text())
    html = t.render(rubric=rubric)
    out_path.write_text(html)
    return


def run_main():
    global VERBOSE
    args = parse_args()
    VERBOSE = args['verbose']

    rubric = load_rubric(args['input'])
    export_rubric(rubric, args['output'])


if __name__ == '__main__':
    run_main()
