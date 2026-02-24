from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, Iterable

import numpy as np

# ---- Zurich Instruments ----
from zhinst.core import ziDAQServer


def to_jsonable(obj: Any):
    """Convert numpy / bytes / complex / sets etc. to JSON-friendly types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, (set, tuple)):
        return list(obj)
    if isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}
    if isinstance(obj, (bytes, bytearray)):
        try:
            return obj.decode("utf-8")
        except Exception:
            return obj.hex()
    # Let json handle the rest (dict, list, str, int, float, bool, None)
    raise TypeError(f"Type not JSON serializable: {type(obj).__name__}")


def purify(obj: Any) -> Any:
    """transform the entire structure to pure Python types, useful for further processing or inspection."""
    if isinstance(obj, dict):
        return {k: purify(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [purify(v) for v in obj]
    if isinstance(obj, tuple):
        return [purify(v) for v in obj]
    if isinstance(obj, set):
        return [purify(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, (bytes, bytearray)):
        try:
            return obj.decode("utf-8")
        except Exception:
            return obj.hex()
    if isinstance(obj, complex):
        return {"real": obj.real, "imag": obj.imag}
    return obj


def get_lockin_settings(
    host: str = "127.0.0.1",
    port: int = 8005,
    api_level: int = 1,
    device: str = "dev1657",
) -> Dict[str, Any]:
    """
    Read Zurich Instruments Lock-in Amplifier settings.

    Parameters:
        host     : LabOne Data Server host
        port     : LabOne Data Server port
        api_level: API version
        device   : Device ID, e.g. 'dev1657'

    Return:
        settings: dict of settings
    """
    daq = ziDAQServer(host, port, api_level)
    try:
        daq.connect()

        nodes_to_read: Iterable[str] = [
            f"/{device}/oscs/*",  # Oscillator
            f"/{device}/demods/*",  # Demodulator
            f"/{device}/sigouts/*",  # Output settings
            f"/{device}/sigins/*",  # Input settings
            f"/{device}/mods/*",  # Modulation settings (if any)
            # f"/{device}/sweeper/*",
        ]

        settings: Dict[str, Any] = {}
        for node in nodes_to_read:
            try:
                data = daq.get(node)
                settings[node] = data
            except Exception as e:
                settings[node] = f"Error reading {node}: {e}"

        return settings
    finally:
        try:
            daq.disconnect()
        except Exception:
            pass


def find_first_osc_data(cfg: Dict[str, Any], device: str) -> Any:
    needle = f"/{device}/oscs/"
    for k, v in cfg.items():
        if isinstance(k, str) and needle in k:
            return v
    star_key = f"/{device}/oscs/*"
    if star_key in cfg:
        return cfg[star_key]
    return None


def create_allsettings_json(
    HOST="127.0.0.1", PORT=8005, API_LEVEL=1, DEVICE="dev1657", path="", timestamp=""
):
    # ---- get setting ----
    cfg = get_lockin_settings(host=HOST, port=PORT, api_level=API_LEVEL, device=DEVICE)

    # ---- save a pure json
    pure_json_path = os.path.join(path, f"allsettings_{timestamp}.json")
    with open(pure_json_path, "w", encoding="utf-8") as f:
        json.dump(purify(cfg), f, indent=2, ensure_ascii=False)

    print(f"[OK] Settings saved to:\n {pure_json_path}")
    return 0


def generate_setting(setting, filename="", folder=""):
    with open("./module/amplifier.json", "r", encoding="utf-8") as f:
        extra_data = json.load(f)

    setting["Other"] = extra_data

    os.makedirs(folder, exist_ok=True)

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"settings_{timestamp}.json"
    else:
        filename = f"settings_{filename}.json"

    full_path = os.path.join(folder, filename)

    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(setting, f, indent=2, ensure_ascii=False)

    print(f"[OK] setting saved to: {full_path}")
    return full_path


if __name__ == "__main__":
    from tools import create_new_folder

    HOST = "127.0.0.1"
    PORT = 8005  # LabOne Data Server port
    API_LEVEL = 1
    DEVICE = "dev1657"

    setting = {
        "amp1": [1.25, 1, 0.75, 0.5],  # Amplitude for drive output
        "amp2": [0.4],  # Amplitude for modulation output
        "frerange": [[61500, 63000], [61500, 63000]],  # Frequency range for sweeper
    }
    # ---- create output dir ----
    path, timestamp = create_new_folder(prefix="")
    create_allsettings_json(
        HOST, PORT, API_LEVEL, DEVICE, path=path, timestamp=timestamp
    )
    generate_setting(setting=setting, filename=timestamp, folder=path)

    # ---- save a json----
    # json_path = os.path.join(path, "settings.json")
    # with open(json_path, "w", encoding="utf-8") as f:
    #     json.dump(cfg, f, indent=2, ensure_ascii=False, default=to_jsonable)

    # ---- search----
    # osc_data = find_first_osc_data(cfg, DEVICE)
    #  OSCS info preview
    # if osc_data is not None:
    #     try:
    #         preview = purify(osc_data)
    #
    #         s = json.dumps(preview, ensure_ascii=False)[:500]
    #         print(f"OSC settings preview: {s}...")
    #     except Exception:
    #         print("OSC settings preview: <non-printable>")
    # else:
    #     print("OSC settings: <not found>")
