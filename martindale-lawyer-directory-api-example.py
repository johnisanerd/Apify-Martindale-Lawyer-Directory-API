"""Martindale Lawyer Directory API: A Quick Start Example.

See more at: https://apify.com/johnvc/lawyer-directory-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/lawyer-directory-api/input-schema?fpr=9n7kx3

This script shows how to call the Martindale Lawyer Directory API on Apify from
Python and read its structured JSON output. Every run returns one row per US
attorney profile: bar admissions with their years, law school, first admission
year, practice areas, firm and role, office address, phones, website,
languages, and peer review stars.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3

Examples:
  uv run python martindale-lawyer-directory-api-example.py
  uv run python martindale-lawyer-directory-api-example.py --example default
  uv run python martindale-lawyer-directory-api-example.py --example credentials
  uv run python martindale-lawyer-directory-api-example.py --example watchlist
"""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from typing import Any

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

ACTOR_ID = "johnvc/lawyer-directory-api"


def _run(client: ApifyClient, run_input: dict[str, Any]) -> list[dict[str, Any]]:
    """Run the Actor with the given input and return the dataset rows.

    Args:
        client: An authenticated Apify client.
        run_input: The Actor input. `mode` is always required; `search` mode
            uses `keywords` plus `maxResultsPerKeyword`, `url` mode uses
            `profileUrls`.

    Returns:
        One row per profile collected. Rows carry `result_type` of either
        "lawyer" or "error", so an input that matched nothing stays visible
        instead of disappearing.
    """
    # apify-client 3.x returns a typed Run object, not a dict, so read the
    # dataset id as an attribute.
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    if run is None:
        raise SystemExit("The Actor run did not return a result.")

    print(f"Run id: {run.id}")
    return list(client.dataset(run.default_dataset_id).iterate_items())


def _split_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Separate attorney profile rows from error rows."""
    lawyers = [r for r in rows if r.get("result_type") == "lawyer"]
    errors = [r for r in rows if r.get("result_type") == "error"]
    return lawyers, errors


def _report_errors(errors: list[dict[str, Any]]) -> None:
    """Print any keyword or URL that produced no profile."""
    for row in errors:
        source = row.get("sourceUrl") or row.get("searchKeyword") or "(unknown input)"
        print(f"  no profiles for {source}: {row.get('error_message')}")


def run_default(client: ApifyClient) -> None:
    """Cheap general quick-start showing the widest slice of the output."""
    # One keyword and maxResultsPerKeyword=2 keeps this first run inexpensive.
    # Billing is one charged event per profile pushed to the dataset, so
    # maxResultsPerKeyword is both your result cap and your cost cap. Raise it
    # (up to 2000) once you have your own API key and know your budget. You can
    # pass up to 20 keywords in a single run.
    rows = _run(
        client,
        {
            "mode": "search",
            "keywords": ["medical malpractice Philadelphia"],
            "maxResultsPerKeyword": 2,
        },
    )
    lawyers, errors = _split_rows(rows)
    print(f"Returned {len(lawyers)} attorney profile(s).\n")

    for lawyer in lawyers:
        print(f"{lawyer.get('name')}  (ISLN {lawyer.get('isln')})")
        print(f"  Matched keyword: {lawyer.get('searchKeyword')}")
        print(f"  Practice areas:  {lawyer.get('areasOfPractice')}")
        print(f"  Practice count:  {lawyer.get('practiceCount')}")
        print(f"  Firm and role:   {lawyer.get('firm')}")
        print(f"  State:           {lawyer.get('state')}")
        print(f"  Address:         {lawyer.get('address')}")
        print(f"  Phones:          {lawyer.get('phones')}")
        print(f"  Website:         {lawyer.get('website')}")
        print(f"  Law school:      {lawyer.get('lawSchool')}")
        print(f"  University:      {lawyer.get('university')}")
        print(f"  First admitted:  {lawyer.get('firstAdmissionYear')}")
        print(f"  Admissions:      {lawyer.get('admissions')}")
        print(f"  Languages:       {lawyer.get('languages')}")
        print(f"  Peer review:     {lawyer.get('peerReview')}")
        print(f"  Profile:         {lawyer.get('profileUrl')}")
        print(f"  Summary:         {lawyer.get('summary')}\n")

    _report_errors(errors)


def run_credentials(client: ApifyClient) -> None:
    """Credential screening: who is admitted where, and since when.

    This is the layer that separates directory data from a plain contact list.
    `firstAdmissionYear` is a clean integer you can subtract from the current
    year for time in practice, and `admissions` carries every listed
    jurisdiction with its year, federal district and appeals courts included.
    """
    # Two profiles is enough to show the shape, so this recipe costs two
    # charged records.
    rows = _run(
        client,
        {
            "mode": "search",
            "keywords": ["employment law Chicago"],
            "maxResultsPerKeyword": 2,
        },
    )
    lawyers, errors = _split_rows(rows)

    current_year = datetime.now(timezone.utc).year
    for lawyer in lawyers:
        admitted = lawyer.get("firstAdmissionYear")
        years_in_practice = current_year - admitted if admitted else None
        print(f"{lawyer.get('name')}")
        print(f"  Law school:       {lawyer.get('lawSchool')}")
        print(f"  Undergraduate:    {lawyer.get('university')}")
        print(f"  First admitted:   {admitted}")
        print(f"  Years in practice:{years_in_practice}")
        print(f"  All admissions:   {lawyer.get('admissions')}")
        print(f"  Memberships:      {lawyer.get('memberships')}")
        print(f"  Awards:           {lawyer.get('awards')}")
        print(f"  Languages:        {lawyer.get('languages')}")
        print(f"  Peer review:      {lawyer.get('peerReview')}")
        print(f"  Profile:          {lawyer.get('profileUrl')}\n")

    # Fields the profile does not list come back as None, so check before you
    # depend on one. Languages, memberships, and awards are the usual gaps.
    _report_errors(errors)


def run_watchlist(client: ApifyClient) -> None:
    """Re-collect a fixed list of attorney profiles by URL.

    URL mode takes profile URLs you already hold, up to 500 per run. Because
    `isln` is stable across firm moves and name changes, the same attorney
    joins cleanly across runs, so comparing the `firm` field between two runs
    shows who moved. `fetched_at` dates every observation.
    """
    # Two URLs, so this recipe costs two charged records. Swap in your own list
    # and schedule the run to build a history.
    rows = _run(
        client,
        {
            "mode": "url",
            "profileUrls": [
                "https://www.martindale.com/attorney/benjamin-john-simmons-168779542/",
                "https://www.martindale.com/attorney/marcus-aric-washington-168778862/",
            ],
        },
    )
    lawyers, errors = _split_rows(rows)

    for lawyer in lawyers:
        print(f"{lawyer.get('name')}  (ISLN {lawyer.get('isln')})")
        print(f"  Firm and role: {lawyer.get('firm')}")
        print(f"  Address:       {lawyer.get('address')}")
        print(f"  Phones:        {lawyer.get('phones')}")
        print(f"  Admissions:    {lawyer.get('admissions')}")
        print(f"  Observed at:   {lawyer.get('fetched_at')}\n")

    _report_errors(errors)


def main() -> None:
    """Dispatch one of the example recipes."""
    parser = argparse.ArgumentParser(
        description="Martindale Lawyer Directory API examples"
    )
    parser.add_argument(
        "--example",
        default="default",
        choices=["default", "credentials", "watchlist"],
        help="Which recipe to run (see the README Recipes section).",
    )
    args = parser.parse_args()

    token = os.getenv("APIFY_API_TOKEN")
    if not token:
        raise SystemExit("Set APIFY_API_TOKEN in .env or the environment.")

    client = ApifyClient(token)
    dispatch = {
        "default": run_default,
        "credentials": run_credentials,
        "watchlist": run_watchlist,
    }
    dispatch[args.example](client)


if __name__ == "__main__":
    main()
