import json
import os
from typing import List, Dict, Tuple, Optional

# ---- helpers ---------------------------------------------------------------


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def first_sample_block(sample_field):
    """
    Your structure is usually: sample -> [[{ ...fields... }]]
    Return that inner dict ({} if not found).
    """
    blk = sample_field
    if isinstance(blk, list) and blk:
        blk = blk[0]
    if isinstance(blk, list) and blk:
        blk = blk[0]
    return blk if isinstance(blk, dict) else {}


def extract_fields_from_demod(
    demod_dict: dict, fields: Tuple[str, ...] = ("frequency", "x", "y", "r", "phase")
) -> Dict[str, list]:
    """
    From a single demod node (with 'sample': [[{...}]]) pull selected fields.
    Accept both 'frequency' and the typo 'fraquency'.
    """
    sample = demod_dict.get("sample", {})
    blk = first_sample_block(sample)

    out = {}
    for f in fields:
        if f in blk:
            out[f] = blk[f]
        elif f == "frequency" and "fraquency" in blk:  # tolerate typo
            out["frequency"] = blk["fraquency"]
    return out


# ---- main merging logic ----------------------------------------------------


def merge_demods_from_files(
    timestamps: List[str],
    foldernames: List[str],
    device_id: str = "dev1657",
    demod_ids: Tuple[str, ...] = ("1", "3"),
    fields: Tuple[str, ...] = ("frequency", "x", "y", "r", "phase"),
    whole_name: List[str] = [""],
    parent_folder: str = "./results",
) -> Dict[str, dict]:
    """
    Read multiple JSONs and build:
    {
      "<name>": { "demods": { "1": {fields...}, "3": {fields...} } },
      ...
    }
    - name = file stem by default, or overridden by name_map[path]
    """
    merged = {}
    counter = 0
    for p in timestamps:
        p = f"{parent_folder}/{foldernames[counter]}/alldatas_{p}.json"
        name = whole_name[counter]
        counter += 1
        data = load_json(p)

        dev_block = data.get(device_id, {})
        demods = dev_block.get("demods", {})

        # normalize keys to strings
        demods = {str(k): v for k, v in demods.items()}

        demods_out = {}
        for demod_id in demod_ids:
            demod_dict = demods.get(demod_id, {})
            picked = extract_fields_from_demod(demod_dict, fields)
            demods_out[demod_id] = picked  # {} if missing; fine

        merged[name] = {"demods": demods_out}
    with open(
        f"{parent_folder}/{parent_folder[10:]}_merged_sweeps.json",
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    return merged


# ---- example ---------------------------------------------------------------

if __name__ == "__main__":
    files = [
        "2508191839",
        "2508191850",
    ]
    foldernames = [
        "2508191839_amp1_1_amp2_0.01",
        "2508191850_amp1_1_amp2_0.01",
    ]
    name_map = None

    merged = merge_demods_from_files(
        files,
        foldernames,
        device_id="dev1657",
        demod_ids=("1", "3"),
        fields=("frequency", "x", "y", "r", "phase"),
        name_map=name_map,
    )
