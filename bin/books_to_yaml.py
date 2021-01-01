#!/usr/bin/env python3

"""
Convert my Excel book list to a yaml-file, ready for
consumption by Jekyll for my blog.
"""

from pathlib import Path
import datetime
import sys

from yaml import dump
import pandas as pd


def excel2yml(books_in, yaml_out):
    """Convert the specified file to yaml."""

    books_in = Path(books_in).expanduser()
    yaml_out = Path(yaml_out).expanduser()

    df = pd.read_excel(books_in)
    df = df[["Title", "Author", "Rating", "Read", "Pages", "Published"]]
    df.columns = [
        "title",
        "author",
        "rating",
        "date",
        "pages",
        "year",
    ]  # rename columns
    df = df.dropna(subset=["rating"])  # drop unfinished books
    df = df.sort_values(by="date", ascending=False)  # sort to most recent first

    # cutoff = datetime.datetime(2010, 1, 1)
    # df = df.loc[df["date"] >= cutoff]
    df["date"] = df["date"].dt.strftime("%d %b '%y")
    df["rating"] = df["rating"].astype(int)
    df["pages"] = df["pages"].astype(int)
    df["year"] = df["year"].astype(int)

    books = []
    for index, row in df.iterrows():
        books.append(row.to_dict())

    with yaml_out.open("w") as f:
        dump(books, f, default_flow_style=False)


if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = Path(__file__).parents[1] / "_data" / "books.yml"
    excel2yml(infile, outfile)
