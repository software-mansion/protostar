from pathlib import Path
from typing import List


def resolve_cairo_targets(targets: List[str]) -> List[Path]:
    filepaths: List[Path] = []
    for target in [Path(t) for t in targets]:
        if target.is_file():
            filepaths.append(target.resolve())
        else:
            filepaths.extend(
                [
                    f
                    for f in target.resolve().glob("**/*.cairo")
                    if f.is_file()
                ]
            )

    return filepaths
