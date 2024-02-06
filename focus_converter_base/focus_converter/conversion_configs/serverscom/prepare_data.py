import argparse
import calendar
import csv
import datetime
import os
from typing import Dict, List


def validate_input_file(input_file: str) -> None:
    """Validate the existence of the input file."""
    if not os.path.isfile(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' not found.")


def process_data(
    items: List[Dict[str, str]],
    issue_date: datetime.datetime,
    account_id: str,
    account_name: str,
) -> List[Dict[str, str]]:
    """Process CSV data and prepare records."""
    named_resources = {
        record["service_id"]: record["title"]
        for record in items
        if record["parent_service_id"] == "" and record["title"] != ""
    }
    prepared_data = []

    for record in items:
        if record["parent_service_id"] != "":
            record["title"] = named_resources.get(record["parent_service_id"], "")

        # Extracting the first word from 'title'
        record["title"] = record["title"].split(" ")[0]

        # Formatting invoice date
        record["billing_start"] = issue_date.strftime("%d.%m.%y")
        record["billing_end"] = issue_date.replace(
            day=calendar.monthrange(issue_date.year, issue_date.month)[1]
        ).strftime("%d.%m.%y")
        record["billing_account_id"] = account_id
        record["billing_account_name"] = account_name
        record["description"] = " ".join(
            [record["title"], record["service_type"], record["description"]]
        )
        record["usage_unit"] = (
            record["quantity"].split(" ")[1]
            if len(record["quantity"].split(" ")) > 1
            else ""
        )
        record["quantity"] = record["quantity"].split(" ")[0]
        record["list_unit_price"] = float(record["subotal"]) / float(record["quantity"])
        prepared_data.append(record)

    return prepared_data


def write_to_csv(
    output_file: str, fieldnames: List[str], data: List[Dict[str, str]]
) -> None:
    """Write processed data to a CSV file."""
    with open(output_file, "w", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames)
        writer.writeheader()
        writer.writerows(data)


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Process CSV data and generate an output file."
    )

    # Add arguments
    parser.add_argument("--input-file", help="Input CSV file path", required=True)
    parser.add_argument(
        "--invoice-date",
        help="Invoice date in format DD.MM.YYYY",
        default=datetime.datetime.now().replace(day=1),
        type=lambda x: datetime.datetime.strptime(x, "%d.%m.%Y"),
    )
    parser.add_argument("--output-file", help="Output CSV file", default="output.csv")
    parser.add_argument("--billing-account-id", help="Billing account ID", default="1")
    parser.add_argument(
        "--billing-account-name", help="Billing account name", default="My organization"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    try:
        # Validate input file existence
        validate_input_file(args.input_file)

        # Read CSV data
        with open(args.input_file, newline="") as datafile:
            items = csv.DictReader(datafile)
            read_items = [x for x in items]

        # Process data
        prepared_data = process_data(
            read_items,
            args.invoice_date,
            args.billing_account_id,
            args.billing_account_name,
        )

        # Write processed data to CSV
        fieldnames = prepared_data[0].keys()
        write_to_csv(args.output_file, fieldnames, prepared_data)

        print(f"Processing complete. Output written to '{args.output_file}'.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
