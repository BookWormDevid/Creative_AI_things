"""Reproduce the local lab in a new output directory using only the standard library."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import lab01_generator as gen

LAB = Path(__file__).resolve().parents[1]


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    out = a.out.resolve()
    if out.exists():
        ap.error("Output already exists; choose a new directory to preserve evidence.")
    protocol_path = LAB / "configs/protocol.json"
    registration = json.loads((LAB / "reports/registration.json").read_text(encoding="utf-8"))
    protocol_bytes = protocol_path.read_bytes()
    assert hashlib.sha256(protocol_bytes).hexdigest() == registration["protocol_sha256"], "Registered protocol changed"
    protocol = json.loads(protocol_bytes)
    for name, expected in registration["source_sha256"].items():
        assert gen.sha256((LAB / "src" / name).read_bytes()) == expected, f"Source changed: {name}"
    out.mkdir(parents=True)
    commands = []

    def run(args, log_name):
        cmd = [sys.executable, *map(str, args)]
        started = datetime.now(timezone.utc).isoformat()
        result = subprocess.run(cmd, cwd=LAB.parent, capture_output=True, encoding="utf-8", errors="strict")
        record = {"started_utc": started, "argv": cmd, "cwd": str(LAB.parent), "exit_code": result.returncode}
        commands.append(record)
        (out / log_name).write_text("COMMAND: " + subprocess.list2cmdline(cmd) + "\n" + "CWD: " + str(LAB.parent)
                                    + "\nSTART UTC: " + started + "\n\nSTDOUT:\n" + result.stdout + "\nSTDERR:\n" + result.stderr,
                                    encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"Command failed: {cmd}; see {log_name}")

    generator = LAB / "src/lab01_generator.py"
    params = ["--size", "96", "--cell", "2", "--octaves", "2", "--persistence", "0.7", "--quantize", "8", "--interp", "smooth"]
    for name, seed in (("noseed_1", None), ("noseed_2", None), ("seed_1", 101), ("seed_2", 101)):
        run([generator, *params, *(["--seed", seed] if seed is not None else []), "--out", out / "error_demo" / name], name + ".log")
    error_runs = {name: json.loads(next((out / "error_demo" / name).glob("result_*.json")).read_text(encoding="utf-8"))
                  for name in ("noseed_1", "noseed_2", "seed_1", "seed_2")}
    assert error_runs["noseed_1"]["sha256_pixels"] != error_runs["noseed_2"]["sha256_pixels"]
    assert error_runs["seed_1"]["sha256_pixels"] == error_runs["seed_2"]["sha256_pixels"]
    summaries = {}
    for n in (protocol["main_n"], *protocol["additional_n"]):
        folder = out / f"v27_n{n}"
        run([LAB / "src/lab01_experiment.py", "--variant", 27, "--seed", 101, "--n", n, "--out", folder], f"n{n}.log")
        result = json.loads((folder / "results.json").read_text(encoding="utf-8"))
        assert result["eq"] == {"EQ_1_2": True, "EQ_1_4": True, "EQ_1_3": False, "EQ_2_4": True}
        rows = []
        for seed in range(101, 101 + n):
            pair = {}
            for condition, p in (("base", protocol["base"]), ("factor", protocol["perturbed"])):
                pixels = gen.generate(p, seed)
                r = gen.run_once(p, seed)
                blocks = [sum(pixels[y * 96 + x] for y in range(by, by + 24) for x in range(bx, bx + 24)) / (24 * 24 * 255)
                          for by in range(0, 96, 24) for bx in range(0, 96, 24)]
                pair[condition] = {**r, "pixel_min": min(pixels), "pixel_max": max(pixels),
                                   "block_means_4x4": blocks, "block_mean_stdev": statistics.stdev(blocks)}
            rows.append({"seed": seed, **pair})
        paired = {}
        for metric in ("mean", "contrast", "edge", "entropy"):
            b = [r["base"][metric] for r in rows]
            f = [r["factor"][metric] for r in rows]
            t = result["metrics_table"][metric]
            assert math.isclose(statistics.mean(b), t["mean_base"], abs_tol=1e-14)
            assert math.isclose(statistics.stdev(b), t["s_base"], abs_tol=1e-14)
            assert math.isclose(statistics.mean(f), t["mean_pert"], abs_tol=1e-14)
            assert math.isclose(statistics.stdev(f), t["s_pert"], abs_tol=1e-14)
            assert t["significant"] == (abs(t["delta"]) > 2 * t["s_base"])
            ds = [x - y for x, y in zip(f, b)]
            paired[metric] = {"mean_difference": statistics.mean(ds), "se_paired": statistics.stdev(ds) / math.sqrt(n)}
        spatial = {c: {"mean": statistics.mean(r[c]["block_mean_stdev"] for r in rows),
                       "stdev": statistics.stdev(r[c]["block_mean_stdev"] for r in rows)} for c in ("base", "factor")}
        write_json(folder / "per_seed.json", rows)
        write_json(folder / "analysis.json", {"n": n, "paired": paired, "spatial": spatial})
        summaries[str(n)] = {"metrics": result["metrics_table"], "paired": paired, "spatial": spatial}
    run([LAB / "src/lab01_experiment.py", "--variant", 1, "--seed", 101, "--n", 5, "--out", out / "demo_v01"], "demo_v01.log")
    demo = json.loads((out / "demo_v01/results.json").read_text(encoding="utf-8"))
    expected = ["93fae5913d797284", "93fae5913d797284", "79aa3ff4187bbfe8", "93fae5913d797284"]
    assert [r["sha256_pixels"][:16] for r in demo["runs_repro"]] == expected
    expected_metrics = {"mean": (0.4782, 0.0481, 0.4952), "contrast": (0.1311, 0.0102, 0.1254),
                        "edge": (0.0097, 0.0006, 0.0100), "entropy": (6.9969, 0.1264, 6.9664)}
    for m, values in expected_metrics.items():
        assert all(round(demo["metrics_table"][m][k], 4) == v for k, v in zip(("mean_base", "s_base", "mean_pert"), values))
    write_json(out / "commands.json", commands)
    write_json(out / "summary.json", {"series": summaries, "error_demo": error_runs, "demo_pixel_prefixes_match": True,
                                      "demo_metrics_match_4dp": True, "completed_utc": datetime.now(timezone.utc).isoformat()})
    print(json.dumps({"output": str(out), "verified_series": [5, 20, 50], "demo_match": True}, ensure_ascii=False))


if __name__ == "__main__":
    main()
