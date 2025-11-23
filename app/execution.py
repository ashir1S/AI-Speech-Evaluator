# execution.py
import json
from scorer import evaluate_transcript
from rubric_loader import load_rubric


def run_evaluation(transcript_path="sample_data/sample_transcript.txt",
                   rubric_path="rubric/rubric.xlsx"):
    """
    Main execution function:
    - Loads rubric
    - Loads transcript text file
    - Runs evaluation
    - Prints clean JSON output
    """

    # Load rubric from Excel
    print("Loading rubric...")
    rubric = load_rubric(rubric_path)

    # Load transcript
    print("Loading transcript...")
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read().strip()

    # Evaluate
    print("Running evaluation...")
    results = evaluate_transcript(transcript, rubric)

    # Pretty JSON output
    print("\n===== FINAL OUTPUT =====\n")
    print(json.dumps(results, indent=4))

    return results


if __name__ == "__main__":
    run_evaluation()
