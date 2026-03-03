#!/usr/bin/env python3
"""
Regression runner for Procedure Suite extraction outputs.

Usage:
  python tests/regression/run_regressions.py --runner "python -m proc_suite.extract" \
      --fixtures tests/regression/fixtures --expects tests/regression/expectations/expectations.json

The runner command should accept:
  --input <note_txt_path>
and print JSON to stdout.
If your pipeline uses a different CLI, adjust in this script.

This script supports:
- must_equal paths
- must_contain_all / must_contain_any / must_not_contain for cpt_codes list
- several custom checks tailored to the failures in the March 2026 batch review
"""
import argparse, json, os, re, subprocess, sys
from typing import Any, Dict, List

def get_path(obj: Any, path: str):
    # Minimal dot-path + [index] accessor, like registry.a.b[0].c
    cur = obj
    for part in path.split("."):
        if part == "":
            continue
        m = re.match(r"^([^\[]+)(?:\[(\d+)\])?$", part)
        if not m:
            raise KeyError(path)
        key = m.group(1)
        idx = m.group(2)
        if isinstance(cur, dict):
            cur = cur.get(key)
        else:
            return None
        if idx is not None:
            if not isinstance(cur, list): 
                return None
            i = int(idx)
            cur = cur[i] if i < len(cur) else None
    return cur

def listify(x):
    if x is None: return []
    return x if isinstance(x, list) else [x]

def has_node_station(output: Dict[str, Any], station: str, action_in: List[str]):
    node_events = get_path(output, "registry.procedures_performed.linear_ebus.node_events") or []
    for ev in node_events:
        if not isinstance(ev, dict): 
            continue
        if str(ev.get("station","")).upper() == station.upper():
            if not action_in or ev.get("action") in action_in:
                return True
    return False

def run_one(cmd_template: str, note_path: str) -> Dict[str, Any]:
    cmd = cmd_template.format(input=note_path)
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"Runner failed for {note_path}:\nSTDERR:\n{p.stderr}")
    try:
        return json.loads(p.stdout)
    except Exception as e:
        raise RuntimeError(f"Invalid JSON for {note_path}: {e}\nRaw:\n{p.stdout[:2000]}")

def assertions(note_id: str, out: Dict[str, Any], exp: Dict[str, Any]) -> List[str]:
    errors = []
    # convenience
    cpts = out.get("cpt_codes") or get_path(out, "cpt_codes") or get_path(out, "registry.billing.cpt_codes")
    # normalize if registry.billing.cpt_codes is list of dicts
    if cpts and isinstance(cpts, list) and cpts and isinstance(cpts[0], dict):
        cpts = [d.get("code") for d in cpts if isinstance(d, dict) and d.get("code")]
    cpts = listify(cpts)

    def fail(msg): errors.append(f"{note_id}: {msg}")

    for path, expected in exp.get("must_equal", {}).items():
        got = get_path(out, path)
        if got != expected:
            fail(f"must_equal failed for {path}: expected={expected!r} got={got!r}")

    for path, vals in exp.get("must_contain_all", {}).items():
        if path == "cpt_codes":
            missing = [v for v in vals if v not in cpts]
            if missing:
                fail(f"cpt_codes missing required {missing}; got={cpts}")
        else:
            got = listify(get_path(out, path))
            missing = [v for v in vals if v not in got]
            if missing:
                fail(f"{path} missing required {missing}; got={got}")

    for path, vals in exp.get("must_contain_any", {}).items():
        if path == "cpt_codes":
            if not any(v in cpts for v in vals):
                fail(f"cpt_codes missing any of {vals}; got={cpts}")
        else:
            got = listify(get_path(out, path))
            if not any(v in got for v in vals):
                fail(f"{path} missing any of {vals}; got={got}")

    for path, vals in exp.get("must_not_contain", {}).items():
        if path == "cpt_codes":
            bad = [v for v in vals if v in cpts]
            if bad:
                fail(f"cpt_codes contains forbidden {bad}; got={cpts}")
        else:
            got = listify(get_path(out, path))
            bad = [v for v in vals if v in got]
            if bad:
                fail(f"{path} contains forbidden {bad}; got={got}")

    for custom in exp.get("custom", []):
        t = custom.get("type")
        if t == "set_equals":
            got = get_path(out, custom["path"]) or []
            if set(got) != set(custom["expected_set"]):
                fail(f"set_equals failed for {custom['path']}: expected_set={custom['expected_set']} got={got}")
        elif t == "regex_match":
            got = get_path(out, custom["path"]) or ""
            if not re.search(custom["pattern"], str(got)):
                fail(f"regex_match failed for {custom['path']}: pattern={custom['pattern']} got={got!r}")
        elif t == "node_event_includes_station":
            if not has_node_station(out, custom["station"], custom.get("action_in", [])):
                fail(f"node_event_includes_station failed: station={custom['station']} action_in={custom.get('action_in')}")
        elif t == "station_outcome":
            node_events = get_path(out, "registry.procedures_performed.linear_ebus.node_events") or []
            ok = False
            for ev in node_events:
                if str(ev.get("station","")).upper() == custom["station"].upper():
                    outcome = (ev.get("outcome") or ev.get("rose_result") or "").lower()
                    if any(outcome == x.lower() or x.lower() in outcome for x in custom["expected_outcome_in"]):
                        ok = True
            if not ok:
                fail(f"station_outcome failed: station={custom['station']} expected_in={custom['expected_outcome_in']}")
        elif t == "nonstation_ebus_target_present":
            # allow a future field like targets_sampled; else look for the phrase in note evidence_quote/node_events
            text = json.dumps(out)
            if custom["expected_substring"].lower() not in text.lower():
                fail(f"nonstation_ebus_target_present failed: missing substring {custom['expected_substring']!r} anywhere in output")
        elif t == "must_have_min_node_events":
            node_events = get_path(out, "registry.procedures_performed.linear_ebus.node_events") or []
            if len(node_events) < int(custom["min_count"]):
                fail(f"must_have_min_node_events failed: need >= {custom['min_count']} got {len(node_events)}")
        elif t == "must_include_finding_substring":
            got = get_path(out, custom["path"]) or ""
            if custom["substring"].lower() not in str(got).lower():
                fail(f"must_include_finding_substring failed: {custom['substring']!r} not in {custom['path']}")
        elif t == "mechanical_debulking_indication":
            # check for future field, else infer from text
            ind = get_path(out, "registry.procedures_performed.mechanical_debulking.indication") or ""
            blob = (ind + " " + json.dumps(get_path(out, "registry.procedures_performed.mechanical_debulking") or {})).lower()
            if not any(x in blob for x in custom["expected_in"]):
                fail(f"mechanical_debulking_indication failed: expected one of {custom['expected_in']} in mechanical_debulking block")
        elif t == "stent_cycle":
            v = get_path(out, "registry.procedures_performed.airway_stent.action_type") or ""
            if str(v).lower() not in [x.lower() for x in custom["expected_in"]]:
                # allow 'removal' with separate placement fields later; just warn as fail for now
                fail(f"stent_cycle failed: action_type={v!r} expected_in={custom['expected_in']}")
        elif t == "peripheral_target_not":
            targets = get_path(out, "registry.procedures_performed.peripheral_tbna.targets_sampled") or []
            if any(t in targets for t in custom["bad_values"]):
                fail(f"peripheral_target_not failed: found bad targets {custom['bad_values']} in {targets}")
        elif t == "peripheral_target_in":
            targets = get_path(out, "registry.procedures_performed.peripheral_tbna.targets_sampled") or []
            blob = " ".join([str(x) for x in targets]).lower()
            if not any(x.lower() in blob for x in custom["expected_any"]):
                fail(f"peripheral_target_in failed: expected any {custom['expected_any']} in targets {targets}")
        elif t == "age_must_be_null_or_reasonable":
            age = get_path(out, "registry.patient_demographics.age_years")
            if age is None:
                pass
            else:
                try:
                    age_i = int(age)
                    if not (custom["min_reasonable"] <= age_i <= custom["max_reasonable"]):
                        fail(f"age_must_be_null_or_reasonable failed: age={age_i}")
                except:
                    fail(f"age_must_be_null_or_reasonable failed: non-int age={age!r}")
        elif t == "must_have_procedure":
            got = get_path(out, custom["path"])
            if got != custom["expected"]:
                fail(f"must_have_procedure failed: {custom['path']} expected={custom['expected']} got={got}")
        elif t == "must_equal_any":
            got = get_path(out, custom["path"])
            if got not in custom["expected_any"]:
                fail(f"must_equal_any failed: {custom['path']} expected_any={custom['expected_any']} got={got!r}")
        elif t == "must_equal":
            got = get_path(out, custom["path"])
            if got != custom["expected"]:
                fail(f"must_equal failed: {custom['path']} expected={custom['expected']} got={got!r}")
        elif t == "must_have_ultrasound_both_sides_details":
            # expects left+right hemithorax fields present; adapt to your schema
            us = get_path(out, "registry.procedures_performed.chest_ultrasound") or {}
            blob = json.dumps(us).lower()
            if not ("left" in blob and "right" in blob):
                fail("must_have_ultrasound_both_sides_details failed: expected left+right findings in chest_ultrasound")
        else:
            fail(f"Unknown custom check type: {t}")

    return errors

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runner", required=True,
                    help="Command template. Use {input} where the note path should be inserted. Example: 'python -m proc_suite.extract --input {input}'")
    ap.add_argument("--fixtures", default="tests/regression/fixtures")
    ap.add_argument("--expects", default="tests/regression/expectations/expectations.json")
    args = ap.parse_args()

    with open(args.expects, "r", encoding="utf-8") as f:
        exp_all = json.load(f)

    failures = []
    for fn in sorted(os.listdir(args.fixtures)):
        if not fn.endswith(".txt"): 
            continue
        note_id = fn.replace(".txt","")
        exp = exp_all.get(note_id)
        if not exp:
            continue
        out = run_one(args.runner, os.path.join(args.fixtures, fn))
        failures.extend(assertions(note_id, out, exp))

    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("All regressions passed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
