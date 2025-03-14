#!/usr/bin/env python3

import json
from pathlib import Path
from typing import Any

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
        for category in ("filestore", "netapp", "nfsv4"):
            self._cache[category] = {}
            self.load_category(category)

    def load_category(self, category:str) -> None:
        for action in self._actions:
            self._cache[category][action] = {}
            self.load_report(category, action)

    def load_report(self, category:str, action:str) -> None:
        cat_pref = {
            "filestore": "fs1",
            "netapp": "na1",
            "nfsv4": "nfsv4"
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
            n4 = self._cache["nfsv4"][action]
            for filesize in na:
                comparison[action][filesize] = {}
                for bksz in na[filesize]:
                    na_val = na[filesize][bksz]
                    fs_val = fs[filesize][bksz]
                    n4_val = n4[filesize][bksz]
                    ratio_3: float = 0.0
                    if fs_val != 0:
                        ratio_3 = na_val / fs_val
                    ratio_4: float = 0.0
                    if fs_val != 0:
                        ratio_4 = n4_val / fs_val
                    ratio_34: float = 0.0
                    if n4_val != 0:
                        ratio_34 = na_val / n4_val
                    cpsn = {
                        "ratio_3": ratio_3,
                        "ratio_4": ratio_4,
                        "ratio_34": ratio_34,
                        "netapp": na_val,
                        "filestore": fs_val,
                        "nfsv4": n4_val
                    }
                    comparison[action][filesize][bksz] = cpsn

        output=json.dumps(comparison, sort_keys=True, indent=2)
        outfile = Path("comparison") / "netapp-3-and-4-to-filestore-ratio.json"
        outfile.write_text(output)

def main() -> None:
    """The main action."""
    c = Comparator()
    c.compare()

if __name__ == "__main__":
    main()
