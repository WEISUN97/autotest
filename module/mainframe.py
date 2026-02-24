import pyvisa
from time import sleep

# ==================== CONFIGURATION ====================
VISA_RESOURCE = "GPIB0::2::INSTR"  # GPIB mainframe address (change if needed)
# VISA_RESOURCE = "ASRLCOM3::INSTR"  # RS-232 connection
TIMEOUT_MS = 2000  # VISA timeout in milliseconds
# =======================================================


def initialize():
    """Open SIM900 mainframe connection."""
    rm = pyvisa.ResourceManager()
    sim = rm.open_resource(VISA_RESOURCE)
    sim.timeout = TIMEOUT_MS
    sim.write_termination = "\n"
    sim.read_termination = "\n"
    sim.clear()
    print(f"Connected to {VISA_RESOURCE}")
    return sim


def safe_query(sim, cmd, delay=0.15):
    """Perform query safely and handle timeout."""
    try:
        sleep(delay)
        return sim.query(cmd).strip()
    except Exception as e:
        return f"[No response: {e}]"


def read_module_id(sim, slot):
    """Connect to slot using xyZy path, query ID, disconnect."""
    try:
        sim.write(f'CONN {slot},"xyZy"')
        sleep(0.2)
        idn = safe_query(sim, "*IDN?")
    finally:
        sim.write("xyZy")  # disconnect
    return idn


def read_module_config(sim, slot, idn):
    """
    Read configuration depending on module type.
    Returns dict with ID and any available parameters.
    """
    data = {"Slot": slot, "ID": idn}

    # SIM965 (Anolog Filter)
    if "SIM965" in idn:
        sim.write(f'CONN {slot},"xyZy"')
        sleep(0.2)
        data["FREQ"] = safe_query(sim, "FREQ?")
        data["TYPE"] = safe_query(sim, "TYPE?")
        data["PASS"] = safe_query(sim, "PASS?")
        data["SLPE"] = safe_query(sim, "SLPE?")
        data["COUP"] = safe_query(sim, "COUP?")
        sim.write("xyZy")  # disconnect

    # SIM928 (Isolated Voltage Source)
    elif "SIM928" in idn:
        sim.write(f'CONN {slot},"xyZy"')
        sleep(0.2)
        data["VOUT"] = safe_query(sim, "VOLT?")
        data["EXON"] = safe_query(sim, "EXON?")  # 1=enabled
        sim.write("xyZy")

    # SIM964 (Analog Limiter)
    elif "SIM964" in idn:
        sim.write(f'CONN {slot},"xyZy"')
        sleep(0.2)
        data["ULIM"] = safe_query(sim, "ULIM?")
        data["LLIM"] = safe_query(sim, "LLIM?")
        data["AWAK"] = safe_query(sim, "AWAK?")
        data["ULCR"] = safe_query(sim, "ULCR?")
        data["LLCR"] = safe_query(sim, "LLCR?")
        data["OVLD"] = safe_query(sim, "OVLD?")

        sim.write("xyZy")

    # SIM980 (Summing Amplifier)
    elif "SIM980" in idn:
        sim.write(f'CONN {slot},"xyZy"')
        sleep(0.2)
        data["CHAN"] = safe_query(sim, "CHAN? 0")
        data["READ"] = safe_query(sim, "READ?")
        sim.write("xyZy")

    # SIM911 (RF lock-in)
    elif "SIM911" in idn:
        sim.write(f'CONN {slot},"xyZy"')
        sleep(0.2)
        data["GAIN"] = safe_query(sim, "GAIN?")
        data["INPT"] = safe_query(sim, "INPT?")
        data["COUP"] = safe_query(sim, "COUP?")
        data["SHLD"] = safe_query(sim, "SHLD?")
        sim.write("xyZy")

    # Others – only IDN known
    return data


def mainframe():
    sim = initialize()

    # Ensure disconnected before mainframe ID query
    sim.write("xyZy")
    main_id = safe_query(sim, "*IDN?")
    print(f"\nMainframe ID: {main_id}")

    # Try to read module map
    # modmap = safe_query(sim, "MOD?")
    # print(f"Module map: {modmap}\n")

    print("=== Scanning all slots (1–8) ===")
    results = []

    for slot in range(1, 9):
        idn = read_module_id(sim, slot)
        if "SIM900" in idn or "No response" in idn:
            print(f"Slot {slot}: Empty or no response.")
            continue

        # print(f"\nSlot {slot}: {idn}")
        cfg = read_module_config(sim, slot, idn)
        results.append(cfg)

        # for k, v in cfg.items():
        #     if k not in ["Slot", "ID"]:
        #         print(f"  {k}: {v}")

    sim.close()
    print("\nSession closed.\n")

    # print("=== Summary ===")
    # for r in results:
    #     print(f"Slot {r['Slot']} | {r['ID']}")
    #     for k, v in r.items():
    #         if k not in ["Slot", "ID"]:
    #             print(f"   {k}: {v}")
    return results


if __name__ == "__main__":
    mainframe()
