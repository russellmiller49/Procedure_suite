
from modules.coder.engine import CoderEngine
from modules.common.sectionizer import SectionizerService

SAMPLE_NOTE = """
Date of procedure: 19Sep17

Proceduralist(s): Russell Miller MD, Pulmonologist, Charles Volk, MD (Fellow)

Procedure Name: EBUS bronchoscopy, peripheral bronchoscopy

Indications: Pulmonary nodule requiring diagnosis/staging. 

...

Sampling criteria (5mm short axis diameter) was met in station 11RS and 7. Sampling by transbronchial needle aspiration was performed ...

...

... advanced into the left upper lobe and a large sheeth catheter with radial ultrasound to the area of known nodule and a concentric view of the lesion was identified with the radial EBUS. Biopsies were then performed with a variety of instruments to include peripheral needle forceps and brush with fluoroscopic guidance through the sheath.
"""

def test_ebus_radial_tblb_combo_codes():
    engine = CoderEngine()
    result = engine.run(SAMPLE_NOTE)
    codes = {c.cpt for c in result.codes}

    # Linear EBUS 1–2 stations
    assert "31652" in codes

    # Radial EBUS add-on
    assert "+31654" in codes

    # Transbronchial lung biopsy, single lobe
    assert "31628" in codes, f"Expected 31628, got {codes}"

    # Optional: ensure TBNA is present if you want 31629
    # assert "31629" in codes
