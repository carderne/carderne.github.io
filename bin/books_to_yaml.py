#!/usr/bin/env python3

"""
Convert my Excel book list to a yaml-file, ready for
consumption by Jekyll for my blog.
"""

from pathlib import Path
import sys

from yaml import dump
import pandas as pd


def excel2yml(books_in, yaml_out):
    """Convert the specified file to yaml."""

    books_in = Path(books_in).expanduser()
    yaml_out = Path(yaml_out).expanduser()

    df = pd.read_excel(books_in)
    cols = [
        "Title",
        "Author",
        "Rating",
        "Read",
        "Pages",
        "Published",
        "Reread",
        "Audiobook",
    ]
    df = df[cols]

    df = df.dropna(subset=["Rating"])  # drop unfinished books
    df = df.sort_values(by="Read", ascending=False)  # sort to most recent first

    df = df.assign(Read=df.Read.dt.strftime("%d %b '%y"))
    df = df.fillna({"Reread": "n", "Audiobook": "n"})
    df = df.astype({"Rating": int, "Pages": int, "Published": int})

    books = []
    for index, row in df.iterrows():
        books.append(row.to_dict())

    with yaml_out.open("w") as f:
        dump(books, f, default_flow_style=False)


if __name__ == "__main__":
    infile = sys.argv[1]
    outfile = Path(__file__).parents[1] / "_data" / "books.yml"
    excel2yml(infile, outfile)
