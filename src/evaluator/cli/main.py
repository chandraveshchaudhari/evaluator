# evaluator/cli/main.py

import click
from pathlib import Path
from evaluator import Evaluator

@click.group()
def cli():
    """Evaluator CLI – run evaluations from the terminal."""
    pass


@cli.command()
@click.option(
    "--solution",
    "-s",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="Path to instructor solution file (.ipynb or .csv)"
)
@click.option(
    "--submissions",
    "-f",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Folder containing student submissions"
)
@click.option(
    "--output",
    "-o",
    required=False,
    type=click.Path(),
    help="Optional output folder for reports"
)
def evaluate(solution, submissions, output):
    """
    Evaluate a folder of student submissions using the Evaluator class.
    """

    solution = Path(solution)
    submissions = Path(submissions)

    click.echo(f"Loading evaluator...")
    evaluator = Evaluator(
        solution_file_path=str(solution),
        submission_folder_path=str(submissions),
    )

    click.echo(f"Running evaluation...")
    report = evaluator.get_report()

    click.echo("\n=== Evaluation Report ===")
    click.echo(report)

    if output:
        # optional: write report to a JSON file
        import json
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        out_path = output / "report.json"
        out_path.write_text(json.dumps(report, indent=2), encoding="utf8")
        click.echo(f"\nSaved report to: {out_path}")


if __name__ == "__main__":
    cli()
    