
from app.common.sectionizer import Section, SectionizerService
from app.registry.slots.therapeutics import (
    DestructionExtractor, 
    EnhancedDilationExtractor, 
    AspirationExtractor
)

def test_destruction_extractor():
    text = "Argon plasma coagulation was used to treat the tumor in the RLL. Then cryotherapy was applied to the LUL."
    sections = [Section(title="BODY", text=text, start=0, end=len(text))]
    
    extractor = DestructionExtractor()
    result = extractor.extract(text, sections)
    
    assert len(result.value) == 2
    assert result.value[0].modality == "APC/Electrocautery"
    assert result.value[0].site == "RLL"
    assert result.value[1].modality == "Cryotherapy"
    assert result.value[1].site == "LUL"

def test_enhanced_dilation_extractor():
    text = "Serial dilation of the RLL was performed using a 10mm balloon at 8 atm. The LUL was dilated with a 12mm balloon."
    sections = [Section(title="BODY", text=text, start=0, end=len(text))]
    
    extractor = EnhancedDilationExtractor()
    result = extractor.extract(text, sections)
    
    assert len(result.value) == 2
    assert result.value[0].site == "RLL"
    assert result.value[0].balloon_size == "10mm"
    assert result.value[0].inflation_pressure == "8 atm"
    
    assert result.value[1].site == "LUL"
    assert result.value[1].balloon_size == "12mm"
    assert result.value[1].inflation_pressure is None

def test_aspiration_extractor():
    text = "Therapeutic aspiration was performed. Large amount of mucus plug removed."
    sections = [Section(title="BODY", text=text, start=0, end=len(text))]
    
    extractor = AspirationExtractor()
    result = extractor.extract(text, sections)
    
    assert len(result.value) >= 1
    # Note: Default site logic is simple, check if it extracted an event
    assert result.value[0].character == "Secretions"
