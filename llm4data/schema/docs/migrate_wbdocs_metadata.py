import json
from typing import Union, Optional
from pathlib import Path
import fire
from tqdm.auto import tqdm
from llm4data.schema.docs import wbdocs


def main(source_dir: Union[str, Path], target_dir: Optional[Union[str, Path]] = None):
    source_dir = Path(source_dir)
    assert source_dir.exists(), f"{source_dir} does not exist"

    if target_dir:
        target_dir = Path(target_dir)
        assert target_dir.exists(), f"{target_dir} does not exist"

    for p in tqdm(sorted(source_dir.glob("D*.metadata.json"))):
        metadata = json.loads(p.read_text())
        s = wbdocs.WBDocsToSchema(metadata)
        sc = s.schema()

        if not target_dir:
            p.write_text(json.dumps(sc.dict(exclude_none=True)))
        else:
            target_path = target_dir / p.name
            target_path.write_text(json.dumps(sc.dict(exclude_none=True)))


if __name__ == "__main__":
    # python -m llm4data.schema.docs.migrate_wbdocs_metadata --source_dir=<source_dir> --target_dir=<target_dir>
    fire.Fire(main)
