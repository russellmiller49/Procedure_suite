from modules.coder.engine import CoderEngine

def test_stent_removal_and_cryo():
    coder = CoderEngine()
    note = """
    PROCEDURE PERFORMED: Rigid bronchoscopy, Silicone Y-stent removal
    ...
    The stent was subsequently removed en-bloc with the rigid bronchoscope without difficulty.
    ...
    At this point the cryotherapy probe was used to perform multiple 30 second freeze thaw cycles at the areas of residual granulation tissue within the left and right mainstems.
    """
    result = coder.run(note)
    codes = {c.cpt for c in result.codes}
    assert "31635" in codes
    assert "31641" in codes
    assert "31622" not in codes  # Diagnostic should be bundled
