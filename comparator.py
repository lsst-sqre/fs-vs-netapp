#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Any

from dataclasses import dataclass, asdict

@dataclass
class Comparison:
    ratio: float
    netapp: int
    filestore: int

class Comparator:

    def __init__(self) -> None:
        self._cache: dict[
            str,
            dict[
                str,
                dict[int,
                     dict[int,int]
                     ]
                ]
        ] = {}

        self._actions = (
            "backward-read",
            "fread",
            "fwrite",
            "random-read",
            "random-write",
            "re-fread",
            "re-fwrite",
            "reader",
            "record-rewrite",
            "rereader",
            "rewriter",
            "stride-read",
            "writer"
        )            

        self.load_data()


    def load_data(self) -> None:
        for category in ("filestore", "netapp"):
            self._cache[category] = {}
            self.load_category(category)

    def load_category(self, category:str) -> None:
        for action in self._actions:
            self._cache[category][action] = {}
            self.load_report(category, action)

    def load_report(self, category:str, action:str) -> None:
        cat_pref = {
            "filestore": "fs1",
            "netapp": "na1"
        }
        filename = Path(category) / f"{cat_pref[category]}-{action}.tsv"
        inp_lines = filename.read_text().split("\n")

        header = ""
        blocksizes: list[int] = []
        for line in inp_lines:
            line=line.strip()
            # Skip any blank lines
            if not line:
                continue
            # Header is always the first thing in a file
            if not header:
                header = self.strip_quotes(line)
                continue
            # Blocksizes are the second thing
            if not blocksizes:
                blocksizes = [
                    int(self.strip_quotes(x)) for x in line.split()
                ]
                continue
            # Remaining lines are data
            fields = [ int(self.strip_quotes(x)) for x in line.split() ]
            filesize = fields[0]
            self._cache[category][action][filesize] = {}
            for idx, val in enumerate(fields[1:]):
                self._cache[category][action][filesize][blocksizes[idx]] = val

    @staticmethod
    def strip_quotes(entry: str) -> str:
        if len(entry)>2 and entry[0] == '"' and entry[-1] == '"':
            return entry[1:-1]
        return entry

    def compare(self) -> None:
        comparison: dict[
            str,
            dict[int,
                 dict[int,
                      dict[str, Any]
                      ]
                 ]
            ] = {}
        for action in self._actions:
            comparison[action] = {}
            
            na = self._cache["netapp"][action]
            fs = self._cache["filestore"][action]
            for filesize in na:
                comparison[action][filesize] = {}
                for bksz in na[filesize]:
                    na_val = na[filesize][bksz]
                    fs_val = fs[filesize][bksz]
                    ratio: float = 0.0
                    if fs_val != 0:
                        ratio = na_val / fs_val
                    cpsn = Comparison(
                        ratio = ratio,
                        netapp = na_val,
                        filestore = fs_val
                    )
                    comparison[action][filesize][bksz] = asdict(cpsn)

        output=json.dumps(comparison, sort_keys=True, indent=2)
        outfile = Path("comparison") / "netapp-to-filestore-ratio.json"
        outfile.write_text(output)

def main() -> None:
    """The main action."""
    c = Comparator()
    c.compare()

if __name__ == "__main__":
    main()
