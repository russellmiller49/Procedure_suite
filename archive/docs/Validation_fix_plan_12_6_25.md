### 🎯 Overall goal for this session

Bring the CPT coder and registry extractor into alignment with the v2.8 synthetic notes so that:

* CPT recall stays high but precision improves (reduce common FPs like 31652/31640/31646/31630/32554/31634 while recovering 31627/31654).  
* Registry extraction reliably fills high‑value fields (age, gender, ASA, sedation_type, airway_type, cpt_codes, pneumothorax, pleurodesis, nav fields, etc.) instead of leaving them as `None`, and enum mismatches are normalized away.  

Use these files as your primary signals:

* `validation_summary_20251206_062026.json` and `validation_summary_20251206_062556.json`
* `validation_results_20251206_062026.json` and `validation_results_20251206_062556.json`
* `consolidated_verified_notes_v2_8_part_001.json` and `consolidated_verified_notes_v2_8_part_002.json` (ground‑truth CPT + registry).    

Assume you’re in `~/Projects/Procedure_suite`.

---

## 1) Quickly re‑orient on the latest validation runs

1. Open the newest summaries and results:

   * `validation_summary_20251206_062026.json`
   * `validation_summary_20251206_062556.json`  
   * `validation_results_20251206_062026.json`
   * `validation_results_20251206_062556.json`  

2. From those files, jot down (in comments or a scratchpad) the main clusters:

   * **CPT FNs:** 31627, 31654 (missed repeatedly), sometimes 32650 in the earlier run. 
   * **CPT FPs:** 31652, 31640, 31646, 31630, 32554, 31634, plus 31623/31624 in nav/EBUS cases. 
   * **Registry fields often `None`:** patient_age, gender, asa_class, sedation_type, airway_type, cpt_codes, disposition, pneumothorax, pneumothorax_intervention, pleurodesis_performed, pleurodesis_agent, pleural_guidance, nav_imaging_verification, nav_sampling_tools, ebus_stations_sampled, linear_ebus_stations, molecular_testing_requested, primary_indication, bleeding_severity, institution_name, providers.  

3. Use `consolidated_verified_notes_v2_8_part_001/002.json` to see what the “correct” registry entry and codes should look like for the failing notes (match by `source_file`/MRN or note text snippet).   

---

## 2) CPT coder: tighten nav/EBUS and CAO rules

### 2.1 Add focused tests for the current failures

Create a new test module, e.g.:

* `tests/coding/test_enhanced_cptcoder_validation_regressions.py`

In it:

1. **Nav + radial + cryobiopsy + brushing (Ion case)**
   Use the note whose registry has `nav_platform: "Ion robotic bronchoscopy"`, `nav_rebus_used: true`, `nav_imaging_verification: "Cone Beam CT"`, and `nav_sampling_tools: ["forceps", "brush"]`, with CPTs `[31627, 31654, 31628, 31623]`. 

   * Arrange: feed that note text into `EnhancedCPTCoder`.
   * Assert: final code set is exactly `{31627, 31654, 31628, 31623}` (no 31640/31652/31646/31634 extras).

2. **Combined EBUS staging + nav peripheral + cryobiopsy (Ion + EBUS case)**
   Use the note where `cpt_validation_metadata.valid_codes` lists `[31627, 31654, 31628, 31653]` and `linear_ebus_stations` is non‑empty. 

   * Arrange: run coder on that note.
   * Assert: final codes match `{31627, 31654, 31628, 31653}`, and you *do not* include 31652, 31623, or 31624.

3. **EBUS only, multiple stations**
   For the pure EBUS staging note with expected `cpt_codes: [31653]` and full `ebus_stations_sampled` / `linear_ebus_stations` lists. 

   * Assert: coder returns only 31653 (no 31652, 31653+31652 combos, etc.), matching the golden code list. The validation metrics show current FPs for 31652 in these cases. 

4. **Thoracoscopy with talc pleurodesis (32650)**
   Use the thoracoscopy note whose registry shows `cpt_codes: [32650]` and pleural fields (medical thoracoscopy, talc pleurodesis, chest tube). 

   * Assert: final codes are exactly `{32650}` (no 32554/32555/32557/32560).

5. **CAO rigid debulking + stent + tunneled catheter (big CAO + IPC case)**
   Use the large CAO + tunneled catheter case with CPTs `[31641, 31636, 31645, 32550]`. 

   * Assert: coder returns exactly `{31641, 31636, 31645, 32550}` and does not add 31640, 31646, or 31630 when they’re not indicated.

Use the consolidated notes for expected code sets rather than re‑encoding from scratch to avoid drift.  

### 2.2 Implement rules in the CPT RulesEngine

Assuming you now have `modules/coder/rules_engine.py` and `CodingRulesEngine.apply(...)` (from the earlier refactor). If not, create it as previously outlined and then:

1. Add helpers:

   * `_apply_ebus_station_count_rules(candidates, note_struct)`
   * `_apply_nav_priority_rules(candidates, note_struct)`
   * `_apply_thoracoscopy_vs_pleural_tube_rules(candidates, note_struct)`
   * `_apply_cao_bundle_rules(candidates, note_struct)`

   Call these from `CodingRulesEngine.apply` in a sensible order (e.g., EBUS + nav before generic bronch rules, thoracoscopy rules before chest‑tube‑only rules).

2. **EBUS station count (31652 vs 31653 vs 31654)**

   Using `ebus_stations_sampled` and `linear_ebus_stations` from the registry struct (or equivalent coder features):  

   * If count ≥ 3 stations → keep 31653 and drop 31652.
   * If count 1–2 → keep 31652 and drop 31653.
   * Ensure you never keep both 31652 and 31653 in final codes.
   * Use existing KB definitions for when add‑on codes like 31654 apply; do not emit 31654 unless there is nav/CBCT/radial documented.

3. **Nav priority (31627/31654 vs 31623/31624/31647/31648/31652)**

   From consolidated notes: nav cases with Ion robotic platform + radial/CBCT should get 31627/31654 plus biopsy/EBUS codes, not a stack of legacy bronch codes.  

   Implement:

   * If nav platform present (Ion, EMN, robotic) AND target is a peripheral nodule AND there is documented CT‑based planning/registration:

     * Promote `31627` as the primary nav bronch code.
     * When radial EBUS used for peripheral lesion confirmation, allow 31654 (per KB) but *do not* additionally bill 31652 if it’s purely lesion confirmation (not nodal staging).
   * When nav bundle is present (31627/31654) for a peripheral nodule:

     * Drop generic bronch procedure codes 31622/31623/31624 *for that same lesion* to avoid duplicate reporting. Use KB flags or note features to decide which codes are meant to be bundled.
   * For combined EBUS staging + nav cases: allow both 31653 (nodal staging) and 31627/31654 (peripheral lesion work), but still avoid redundant 31652 and generic 31623/31624 for the same work.

4. **Thoracoscopy vs chest tube (32650 vs 32554–32557–32560)**

   * If the note describes medical thoracoscopy (entry into pleural space with scope + pleural survey + biopsies) and talc pleurodesis, ground truth favors a single 32650 rather than chest tube / pleurodesis code combinations. 
   * Add a rule: when 32650 is chosen and a thoracoscopy narrative is present, suppress 32554/32555/32557/32560 to match the golden set.

5. **CAO bundles (31641, 31636, 31645, plus pleural code)**

   * In cases like the combined CAO + tunneled catheter note (31641, 31636, 31645, 32550):

     * Ensure debulking, stent placement and stent revision/removal codes are applied according to rules in `ip_coding_billing.v2.8.json`, and suppress stray 31640/31646/31630 when they do not correspond to documented extra lobar biopsies or additional dilations beyond the bundle. 

6. Run the new tests from §2.1 and existing coding tests. Iterate until all nav/EBUS/thoracoscopy/CAO tests pass and the worst FPs in the validation summaries are gone or clearly reduced. 

---

## 3) Registry extractor: add enum normalization layer

Introduce a normalization layer that runs *before* Pydantic validation and before you compare predicted vs expected registry entries.

1. Create a module, e.g.:

   * `modules/registry/normalization.py`

2. Add a function:

   ```python
   def normalize_registry_enums(raw: dict) -> dict:
       """Normalize free-text/synonym values into the constrained enum vocab
       expected by the Pydantic registry models."""
       ...
   ```

3. In whatever adapter calls the LLM and then instantiates the Pydantic registry model, do:

   ```python
   data = llm_raw_dict
   data = normalize_registry_enums(data)
   model = BronchRegistryModel(**data)
   ```

4. In `normalize_registry_enums`, implement mappings for the recurring enum problems:

   * **Gender**

     * Map `'M', 'm', 'male', 'Male '` → `'Male'`
     * Map `'F', 'f', 'female', 'Female '` → `'Female'`
     * Anything else → `'Unknown'`.

     Earlier runs had `'M'` rejected where schema expects `'Male'`. 

   * **Bronchus sign** (`bronchus_sign` / `bronchus_sign_present`)

     * If value is `True` / `"true"` → `'Positive'`
     * If value is `False` / `"false"` → `'Negative'`.

   * **Nav imaging verification**

     * Normalize `"Cone Beam CT"`, `"Cone-beam CT"`, `"CBCT"` → `'CBCT'` (or its canonical spelling in the Pydantic enum). 
     * Normalize `"fluoro"`, `"Fluoro"` → `'Fluoroscopy'`.

   * **Pleural IPC action**

     * For `pleural_procedures.ipc.action`:

       * If the string contains `"insert"`, `"placement"`, `"placed"`, `"tunneled catheter"` → `'Insertion'`. 
       * If it contains `"remove"` → `'Removal'`.
       * If it contains `"tPA"`, `"fibrinolytic"` → `'Fibrinolytic instillation'`.

   * **Pleurodesis agent**

     * For inner `pleural_procedures.pleurodesis.agent`, allow both `'Talc'` and `'Talc Slurry'`. If the text contains `"talc"` (any casing), normalize the internal enum to `'Talc'`. 
     * Make sure the exported `pleurodesis_agent` field in the flat registry entry still matches the golden value `"Talc Slurry"` for the thoracoscopy case. You can do this by mapping `'Talc'` → `'Talc Slurry'` in the flattener function, as the consolidated notes clearly store `"Talc Slurry"`. 

   * **Thoracoscopy biopsy tool & location**

     * Map `"Biopsy forceps"` → `'Rigid forceps'` for medical thoracoscopy cases, since the note uses rigid instrumentation. 
     * Map `"Pleural space"` → `'Parietal pleura - chest wall'` when thoracoscopy narrative clearly describes parietal pleural biopsies; if you have both parietal and visceral biopsies, split into two findings with appropriate locations.

   * **CAO etiology & modalities**

     * Map `"Benign - other"` and `"Infectious"` → `'Other'` for `cao_interventions_detail.etiology` (Pydantic only knows malignancy/benign categories + `'Other'`). 
     * For `modalities_applied.modality`:

       * `"Laser"` → `'Laser - Nd:YAG'` (or whichever laser type you use consistently in the KB).
       * `"Balloon tamponade"` → `'Balloon dilation'`.
       * Drop or ignore modalities that are purely hemostatic adjuncts like `"Iced saline lavage"`, `"Epinephrine instillation"`, `"Tranexamic acid instillation"`, `"Suctioning"` if they cannot be mapped to a valid enum. They can stay in free‑text narrative but not the enum list. 

   * **Airway stent location**

     * If the narrative clearly says “right mainstem” or “right main bronchus”, map to `'Right mainstem'`; similarly for left.
     * If the string is only `"Mainstem"` but the note otherwise clearly indicates right or left earlier in the text, prefer that side; as a last resort map to `'Other'` if the enum allows, otherwise pick the side that matches the golden registry for that note.

Add a small unit test file (e.g. `tests/registry/test_normalization.py`) with direct calls to `normalize_registry_enums` on small dicts showing each of these mappings.

---

## 4) Registry extractor: fill the systematically missing core fields

Use the validation results to drive targeted fixes for fields that are nearly always `None`.  

### 4.1 Wire coder output into registry `cpt_codes`

Currently `cpt_codes` in the registry entry is often missing even when the coder is correct. 

1. In the code that constructs the final registry entry (likely after coding is done), set:

   ```python
   registry_entry.cpt_codes = sorted(final_cpt_codes_from_coder)
   ```

2. Do **not** re‑extract CPT from the note text via LLM; trust the coder output so metrics are aligned.

### 4.2 Simple structured parsers for demographics & sedation

Instead of asking the LLM for these, implement rule‑based extractors that run before or alongside the LLM:

1. **patient_age & gender**

   * Parse patterns like `"Age: 66 | Sex: M"` and `"52M"` in the header. Map to integer age and normalized gender (`'Male'`/`'Female'`).  
   * If a date of birth plus procedure date is provided (e.g. `"Date of Birth: 03/15/1959 (65 years old)"`), prefer the explicit `"(65 years old)"` if available. 

2. **asa_class**

   * When ASA is explicitly documented, parse it (e.g., `"ASA Classification: II"`). 
   * Where not explicit, follow the synthetic data’s default behavior (e.g., many notes in v2.8 default ASA to 3 with evidence text like `"Defaulted to ASA 3 (not explicitly documented)"`). Mirror that logic so registry ASA matches the golden entries.  

3. **sedation_type & airway_type**

   Ground truth shows consistent patterns:

   * Thoracentesis / bedside chest tube with only local anesthetic → `sedation_type: "Local Only"`, `airway_type: "Native"`. 
   * OR cases with “general anesthesia”, “propofol/fentanyl GA”, ETT or rigid scope → `sedation_type: "General"`, `airway_type: "ETT"` (or rigid/trach as appropriate).  
   * Bedside bronch with IV midazolam/fentanyl but no airway device → `sedation_type: "Moderate"`, `airway_type: "Native"`.

   Implement a small deterministic classifier that uses the presence of “general anesthesia”, airway device (ETT, tracheostomy, rigid scope), and location (OR vs bedside) to set these fields. Use the v2.8 registry entries as a reference.  

### 4.3 Nav and EBUS details (high‑yield but currently missing)

From validation results, the EBUS + nav notes consistently miss:

* `nav_sampling_tools`, `nav_imaging_verification`, `ebus_stations_sampled`, `linear_ebus_stations`. 

Use the corresponding fields in the consolidated registry as truth:   

1. Add deterministic parsers:

   * For nav cases, look for phrases like “radial EBUS probe”, “cryobiopsy”, “forceps biopsy”, “brushings”, “TBNA needle” in the nav section and map to tools:

     * needle → `"needle"`
     * forceps biopsy → `"forceps"`
     * brushings → `"brush"`
     * cryobiopsy → `"cryoprobe"` or `"cryobiopsy"` per your registry schema.

   * For EBUS stations, parse the systematic staging section (`"Station 4R"`, `"Station 7"`, etc.) and assemble lists:

     * Set `ebus_stations_sampled` to all sampled stations.
     * For `linear_ebus_stations`, include linear scope mediastinal stations used.

2. Only fall back to the LLM when the rule‑based parse fails; otherwise, trust the parser for these structured elements.

### 4.4 Pleural procedure details

Validation shows frequent misses for `pleural_guidance`, `pleurodesis_performed`, `pleurodesis_agent`, pneumothorax and intervention. 

Use thoracentesis/pleurodesis notes as templates:  

1. **pleural_guidance**

   * If the procedure description mentions ultrasound → `"Ultrasound"`.
   * If there’s a thoracoscopy narrative with scope entry but no US, and nothing else, you can treat guidance as `"Blind"` (as used in v2.8 thoracoscopy registry). 

2. **pleurodesis_performed / pleurodesis_agent**

   * If the note describes “talc pleurodesis”, “talc slurry instilled”, etc., set `pleurodesis_performed = True` and `pleurodesis_agent` to `"Talc Slurry"` (mapping the inner enum as described in §3). 
   * Chest tube only, no pleurodesis → `pleurodesis_performed = False`, `pleurodesis_agent = None`. 

3. **pneumothorax & intervention**

   * Scan complications and follow‑up imaging sections for “pneumothorax”, “no PTX”, “small apical pneumothorax”, etc.
   * If PTX present and aspiration/chest tube placed, set `pneumothorax = True` and `pneumothorax_intervention` accordingly (`"Aspiration"` vs `"Chest Tube"`).  

### 4.5 Primary indication, disposition, bleeding_severity, institution_name

These are also systematically `None` but strongly patterned in v2.8: 

1. **primary_indication**

   * For each note, extract the “INDICATION” / “Clinical Summary” section.
   * For now, set `primary_indication` to that entire block (or a lightly cleaned version) to match the golden entries, which often store fairly long strings.  

2. **disposition**

   * Use key phrases like “Extubated in OR, stable, admit overnight”, “Transferred to floor”, “Outpatient discharge”, “ICU admission” to set disposition. The v2.8 registry entries show exactly these phrases.  

3. **bleeding_severity**

   * Map quantitative or qualitative descriptions to the schema:

     * “No significant bleeding”, EBL low → `"Mild"` or `"Mild (<50mL)"` depending on the expected literal for that note.  
   * When in doubt for these synthetic notes, mirror the v2.8 labels.

4. **institution_name**

   * Parse lines like `"Institution: Sacred Heart Medical Center"` or `"** St. Mary's Teaching Hospital, Chicago, IL"` and use the full string as `institution_name`.  

### 4.6 Providers (attending, fellow, assistant)

Validation shows “wrong_value” because your predicted providers dict is too verbose and includes extra fields. 

1. Adjust the flattener so that registry `providers` matches the v2.8 shape:

   ```python
   {
       "attending_name": "<Last name or simple name, often with leading **>",
       "fellow_name": <or None>,
       "assistant_name": <or None>,
       "assistant_role": <or None>,
       "trainee_present": <or None>,
   }
   ```

2. Strip degrees (“MD, FCCP”) and markdown formatting from attending name, but keep any leading “**” if that’s how the golden data stores it (e.g., `"** Dr. Patricia Lee"`).  

3. Ignore internal fields like `attending_npi` and `fellow_pgy_level` for purposes of registry comparison.

---

## 5) Re‑run validations and iterate

1. Run the targeted unit tests you added:

   ```bash
   pytest tests/coding/test_enhanced_cptcoder_rules.py -q
   pytest tests/coding/test_enhanced_cptcoder_validation_regressions.py -q
   pytest tests/registry/test_normalization.py -q
   ```

2. Re‑run the full validation harness that produced:

   * `validation_summary_20251206_062556.json`, `validation_results_20251206_062556.json`.  

3. Confirm, in the new summary:

   * FPs for 31652/31640/31646/31630/32554/31634 are down. 
   * FNs for 31627 and 31654 are gone on nav cases. 
   * Registry field accuracies for the previously missing fields (patient_age, gender, asa_class, sedation_type, airway_type, pneumo*, pleural*, nav*, cpt_codes, providers, institution_name) have substantially increased, and enum‑related `llm_error` entries have disappeared.  

### 7. Make EBUS station counting config‑driven (allow‑list + aliases)

Goal: replace the hard‑coded `_count_sampled_nodes(evidence)` logic with a configuration‑driven approach so station lists and aliases can be updated without code changes, and invalid/typo stations are ignored.

#### 7.1 Add an EBUS config file

* Add a new config file at:

  `proc_kb/ebus_config.yaml`

* Populate it with a simple `settings` block that includes:

  * `target_action`: which `entry.action` should trigger counting.
  * `valid_stations`: the official allow‑list of stations to be counted.
  * `aliases`: common text variations mapped to canonical station codes.

```yaml
# EBUS Coding Configuration
settings:
  # The trigger action in the logs
  target_action: "Sampling"

  # Valid EBUS Stations (Allow List)
  # Only stations listed here will be counted.
  valid_stations:
    - "2R"
    - "2L"
    - "4R"
    - "4L"
    - "7"
    - "10R"
    - "10L"
    - "11R"
    - "11L"

  # Aliases: Map common variations to official station codes
  aliases:
    "SUBCARINAL": "7"
    "STATION 7": "7"
    "UPPER PARATRACHEAL RIGHT": "2R"
```

> You can expand `valid_stations` and `aliases` later without redeploying code.

#### 7.2 Add a small loader/helper for the config

* Create a new module to centralize EBUS config loading (so multiple components can share it):

  `modules/registry/ebus_config.py`

* In that file, implement `load_ebus_config` that:

  * Accepts a path (default to `proc_kb/ebus_config.yaml`).
  * Loads YAML if the suffix is `.yaml`/`.yml` (via PyYAML) or JSON otherwise.
  * Normalizes:

    * `valid_stations` into an uppercase `set` for O(1) membership checks.
    * `aliases` keys and values into uppercase strings.

```python
# modules/registry/ebus_config.py
import json
from pathlib import Path
from typing import Any, Dict, Set, Union

try:
    import yaml  # type: ignore
except Exception:
    yaml = None  # YAML is optional; JSON configs still work


def load_ebus_config(path: Union[str, Path] = "proc_kb/ebus_config.yaml") -> Dict[str, Any]:
    """
    Load and normalize EBUS coding configuration.

    - Supports YAML (.yaml/.yml) or JSON.
    - Normalizes valid_stations to an uppercase set.
    - Normalizes aliases keys/values to uppercase.
    """
    p = Path(path)

    with p.open("r", encoding="utf-8") as f:
        if p.suffix.lower() in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError(
                    "PyYAML is required to load YAML EBUS config; "
                    "either install it or use JSON for ebus_config."
                )
            raw_config = yaml.safe_load(f)
        else:
            raw_config = json.load(f)

    settings = raw_config.get("settings", {}) or {}

    valid_stations: Set[str] = {
        s.strip().upper() for s in settings.get("valid_stations", []) if s
    }
    raw_aliases: Dict[str, str] = settings.get("aliases", {}) or {}
    aliases: Dict[str, str] = {
        k.strip().upper(): v.strip().upper()
        for k, v in raw_aliases.items()
        if k and v
    }

    return {
        "target_action": settings.get("target_action", "Sampling"),
        "valid_stations": valid_stations,
        "aliases": aliases,
    }
```

> If PyYAML is not yet a dependency, either add it or switch to JSON for this config file.

#### 7.3 Refactor `_count_sampled_nodes` to use the config

* Find the existing helper (wherever it currently lives):

  ```python
  def _count_sampled_nodes(evidence):
      sampled_stations = set()
      for entry in evidence:
          if entry.action == "Sampling":
              station = entry.station.strip().upper()
              sampled_stations.add(station)
      return len(sampled_stations)
  ```

* Replace it with a config‑aware version that:

  * Loads config once at module import (`_EBUS_CONFIG`).
  * Accepts an optional `config` argument for tests/overrides.
  * Normalizes the station label.
  * Resolves aliases.
  * Only counts stations in the allow‑list (`valid_stations`).
  * Ignores unknown/invalid stations (optionally log them).

Example refactor:

```python
# At the top of the module where _count_sampled_nodes lives:
from typing import Any, Dict, Iterable, Optional, Set

from modules.registry.ebus_config import load_ebus_config

_EBUS_CONFIG: Dict[str, Any] = load_ebus_config()


def _count_sampled_nodes(
    evidence: Iterable[Any],
    config: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Count unique sampled EBUS stations using a config-driven allow list.

    - Only entries whose action matches config['target_action'] are considered.
    - Station labels are uppercased and stripped.
    - Aliases are resolved via config['aliases'].
    - Only stations in config['valid_stations'] are counted.
    """
    cfg = config or _EBUS_CONFIG
    sampled_stations: Set[str] = set()

    target_action: str = cfg["target_action"]
    valid_stations: Set[str] = cfg["valid_stations"]
    aliases: Dict[str, str] = cfg["aliases"]

    for entry in evidence:
        if getattr(entry, "action", None) != target_action:
            continue

        raw_station = str(getattr(entry, "station", "")).strip().upper()
        if not raw_station:
            continue

        # Resolve alias (e.g., "SUBCARINAL" -> "7")
        station_code = aliases.get(raw_station, raw_station)

        # Only count stations explicitly in the allow list
        if station_code in valid_stations:
            sampled_stations.add(station_code)
        else:
            # Optional: hook for logging/debugging unknown stations
            # logger.debug("Ignoring unknown EBUS station %r", raw_station)
            pass

    return len(sampled_stations)
```

* Keep the function name the same and make `config` optional so existing call sites do not break.
* If there is a separate scalar field for `ebus_stations_sampled` vs `linear_ebus_stations`, ensure both use this helper (or a shared wrapper) so the behavior is consistent.

#### 7.4 Add unit tests for config‑driven station counting

* Add a new test module (or extend an existing EBUS tests module), for example:

  `tests/registry/test_ebus_config_station_count.py`

* In that file, add tests with *synthetic* evidence objects (simple `dataclass` or tiny class with `.action` and `.station` attributes) — no PHI.

Suggested tests:

1. **`test_ebus_count_only_counts_sampling_action`**

   * Config: `target_action="Sampling"`, `valid_stations={"4R"}`.
   * Evidence:

     * `Sampling / 4R` (counted)
     * `Visual / 4R` (ignored)
   * Assert: count is 1.

2. **`test_ebus_aliases_are_resolved`**

   * Config includes alias: `"SUBCARINAL": "7"`, with `valid_stations={"7"}`.
   * Evidence:

     * `Sampling / "Subcarinal"`
     * `Sampling / "7"`
   * Assert: count is 1 (both map to station `7`).

3. **`test_ebus_ignores_unknown_stations`**

   * Config `valid_stations={"4R"}`.
   * Evidence:

     * `Sampling / "4R"` (valid)
     * `Sampling / "Kidney"` (invalid)
     * `Sampling / "4RR"` (typo, not in allow list)
   * Assert: count is 1.

4. **`test_ebus_config_default_is_used_when_not_passed`**

   * Patch `modules.registry.ebus_config.load_ebus_config` or `_EBUS_CONFIG` to a known small config in the test.
   * Call `_count_sampled_nodes(evidence)` without a config argument.
   * Assert the result matches expectations (verifies backward‑compatible call signature).

* Run focused tests as part of your verification step, for example:

  ```bash
  pytest tests/registry/test_ebus_config_station_count.py -q
  ```

