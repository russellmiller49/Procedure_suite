#!/usr/bin/env python3
"""
Demonstration of CMS RVU Parser
Shows how to load, query, and calculate payments for interventional pulmonology procedures
"""

import sys
from pathlib import Path
from decimal import Decimal
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from cms_rvu_parser import CMSRVUParser, GPCIRecord


def load_gpci_data(file_path: Path) -> dict:
    """Load GPCI data from CSV"""
    gpci_dict = {}
    # Force locality_code to be read as string to preserve leading zeros
    df = pd.read_csv(file_path, dtype={'locality_code': str})
    
    for _, row in df.iterrows():
        code = str(row['locality_code']).strip()
        # Pad 2-digit codes with leading zero if needed, leave 5-digit codes as-is
        if len(code) <= 2:
            code = code.zfill(2)
        gpci_dict[code] = GPCIRecord(
            locality_code=code,
            locality_name=row['locality_name'],
            work_gpci=Decimal(str(row['work_gpci'])),
            pe_gpci=Decimal(str(row['pe_gpci'])),
            mp_gpci=Decimal(str(row['mp_gpci']))
        )
    
    return gpci_dict


def format_currency(amount: float) -> str:
    """Format as currency"""
    return f"${amount:,.2f}"


def print_separator(char='=', length=80):
    """Print a separator line"""
    print(char * length)


def main():
    """Main demonstration"""
    print_separator()
    print("CMS RVU PARSER DEMONSTRATION")
    print("Interventional Pulmonology Procedures - 2025 Medicare Fee Schedule")
    print_separator()
    
    # Initialize parser
    parser = CMSRVUParser()
    
    # Load sample data
    print("\n1. Loading RVU Data...")
    csv_file = Path(__file__).parent / 'sample_rvu_2025.csv'
    
    if not csv_file.exists():
        print(f"Error: Sample data file not found: {csv_file}")
        return
    
    count = parser.parse_csv_file(csv_file)
    print(f"   ✓ Loaded {count} CPT/HCPCS codes")
    
    # Load GPCI data
    print("\n2. Loading GPCI Data...")
    gpci_file = Path(__file__).parent / 'gpci_2025.csv'
    gpci_data = load_gpci_data(gpci_file)
    print(f"   ✓ Loaded {len(gpci_data)} geographic localities")
    
    # Example 1: Query specific bronchoscopy codes
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Common Diagnostic Bronchoscopy Procedures")
    print("=" * 80)
    
    diagnostic_codes = [
        '31622',  # Diagnostic bronchoscopy
        '31623',  # Bronchoscopy with brushing
        '31624',  # Bronchoscopy with BAL
        '31625',  # Bronchoscopy with biopsy
    ]
    
    for code in diagnostic_codes:
        record = parser.get_record(code)
        if record:
            print(f"\n{code}: {record.description}")
            print(f"  Work RVU:         {record.work_rvu:>8.2f}")
            print(f"  PE RVU (Non-Fac): {record.non_fac_pe_rvu:>8.2f}")
            print(f"  PE RVU (Facility):{record.fac_pe_rvu:>8.2f}")
            print(f"  MP RVU:           {record.mp_rvu:>8.2f}")
            print(f"  Total (Facility): {record.total_fac_rvu:>8.2f}")
    
    # Example 2: Advanced therapeutic procedures
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Advanced Therapeutic Bronchoscopy Procedures")
    print("=" * 80)
    
    therapeutic_codes = [
        ('31631', 'Tracheal stent placement'),
        ('31646', 'Bronchial valve placement'),
        ('31648', 'Tumor excision'),
        ('31660', 'Bronchial thermoplasty (first session)'),
    ]
    
    print(f"\n{'Code':<8} {'Description':<40} {'Work RVU':<10} {'Total RVU':<10}")
    print("-" * 80)
    
    for code, desc in therapeutic_codes:
        record = parser.get_record(code)
        if record:
            print(f"{code:<8} {desc:<40} {float(record.work_rvu):<10.2f} {float(record.total_fac_rvu):<10.2f}")
    
    # Example 3: Payment calculations for different localities
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Payment Calculations by Geographic Locality")
    print("=" * 80)
    
    # Calculate payment for EBUS with TBNA (31653) in different locations
    code = '31653'
    record = parser.get_record(code)
    
    if record:
        print(f"\nProcedure: {code} - {record.description}")
        print(f"Work RVU: {record.work_rvu}, PE RVU (Fac): {record.fac_pe_rvu}, MP RVU: {record.mp_rvu}")
        print(f"\nPayment Estimates by Location (Facility Setting):")
        print(f"{'Locality':<30} {'Work GPCI':<12} {'PE GPCI':<12} {'MP GPCI':<12} {'Payment':<15}")
        print("-" * 85)
        
        localities_to_show = [
            '00',      # National Average
            '05102',   # San Diego (your location!)
            '09',      # San Francisco
            '46',      # Manhattan
            '17',      # Florida
            '53',      # Ohio
        ]
        
        for loc_code in localities_to_show:
            if loc_code in gpci_data:
                gpci = gpci_data[loc_code]
                payment = parser.calculate_payment(
                    code,
                    setting='facility',
                    work_gpci=gpci.work_gpci,
                    pe_gpci=gpci.pe_gpci,
                    mp_gpci=gpci.mp_gpci
                )
                
                if payment:
                    print(f"{gpci.locality_name:<30} {float(gpci.work_gpci):<12.3f} "
                          f"{float(gpci.pe_gpci):<12.3f} {float(gpci.mp_gpci):<12.3f} "
                          f"{format_currency(payment['payment_amount']):<15}")
    
    # Example 4: Compare facility vs non-facility payments
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Facility vs Non-Facility Payment Comparison")
    print("=" * 80)
    
    # Use San Diego GPCI
    san_diego_gpci = gpci_data.get('05102')
    
    print(f"\nLocation: {san_diego_gpci.locality_name}")
    print(f"\n{'Code':<8} {'Description':<35} {'Facility':<15} {'Non-Facility':<15} {'Difference':<15}")
    print("-" * 95)
    
    compare_codes = ['31622', '31625', '31629', '31653']
    
    for code in compare_codes:
        fac_payment = parser.calculate_payment(
            code, 
            setting='facility',
            work_gpci=san_diego_gpci.work_gpci,
            pe_gpci=san_diego_gpci.pe_gpci,
            mp_gpci=san_diego_gpci.mp_gpci
        )
        
        nonfac_payment = parser.calculate_payment(
            code,
            setting='non-facility',
            work_gpci=san_diego_gpci.work_gpci,
            pe_gpci=san_diego_gpci.pe_gpci,
            mp_gpci=san_diego_gpci.mp_gpci
        )
        
        if fac_payment and nonfac_payment:
            diff = nonfac_payment['payment_amount'] - fac_payment['payment_amount']
            print(f"{code:<8} {fac_payment['description'][:35]:<35} "
                  f"{format_currency(fac_payment['payment_amount']):<15} "
                  f"{format_currency(nonfac_payment['payment_amount']):<15} "
                  f"{format_currency(diff):<15}")
    
    # Example 5: Calculate total RVUs for a complex procedure
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Multi-Procedure Case Calculation")
    print("=" * 80)
    
    print("\nScenario: Diagnostic bronchoscopy with EBUS-guided TBNA of multiple lesions")
    print("Codes: 31653 (first lesion) + 31654 (additional lesion)")
    
    codes_in_case = [
        ('31653', 1.0, 'First lesion (100%)'),
        ('31654', 0.5, 'Additional lesion (50% - multiple procedure discount)')
    ]
    
    total_work_rvu = Decimal('0')
    total_payment = 0.0
    
    print(f"\n{'Code':<8} {'Description':<35} {'Payment %':<12} {'Payment':<15}")
    print("-" * 75)
    
    for code, multiplier, desc in codes_in_case:
        payment = parser.calculate_payment(
            code,
            setting='facility',
            work_gpci=san_diego_gpci.work_gpci,
            pe_gpci=san_diego_gpci.pe_gpci,
            mp_gpci=san_diego_gpci.mp_gpci
        )
        
        if payment:
            adjusted_payment = payment['payment_amount'] * multiplier
            total_payment += adjusted_payment
            total_work_rvu += Decimal(str(payment['work_rvu'])) * Decimal(str(multiplier))
            
            print(f"{code:<8} {desc:<35} {multiplier*100:<11.0f}% "
                  f"{format_currency(adjusted_payment):<15}")
    
    print("-" * 75)
    print(f"{'Total:':<44} {format_currency(total_payment):<15}")
    print(f"Total Work RVUs: {float(total_work_rvu):.2f}")
    
    # Example 6: Provider productivity metrics
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Provider Productivity Analysis")
    print("=" * 80)
    
    print("\nSimulated monthly procedure volume:")
    
    monthly_cases = [
        ('31622', 10, 'Diagnostic bronchoscopy'),
        ('31625', 15, 'Bronchoscopy with biopsy'),
        ('31629', 8, 'TBNA mediastinal nodes'),
        ('31653', 12, 'EBUS with TBNA'),
        ('31631', 3, 'Stent placement'),
        ('31646', 2, 'Bronchial valve'),
    ]
    
    print(f"\n{'Code':<8} {'Procedure':<35} {'Volume':<10} {'Work RVU/ea':<12} {'Total wRVU':<12} {'Revenue':<15}")
    print("-" * 100)
    
    total_wrvu = Decimal('0')
    total_revenue = 0.0
    
    for code, volume, description in monthly_cases:
        record = parser.get_record(code)
        payment = parser.calculate_payment(
            code,
            setting='facility',
            work_gpci=san_diego_gpci.work_gpci,
            pe_gpci=san_diego_gpci.pe_gpci,
            mp_gpci=san_diego_gpci.mp_gpci
        )
        
        if record and payment:
            case_wrvu = record.work_rvu * volume
            case_revenue = payment['payment_amount'] * volume
            total_wrvu += case_wrvu
            total_revenue += case_revenue
            
            print(f"{code:<8} {description[:35]:<35} {volume:<10} "
                  f"{float(record.work_rvu):<12.2f} {float(case_wrvu):<12.2f} "
                  f"{format_currency(case_revenue):<15}")
    
    print("-" * 100)
    print(f"{'MONTHLY TOTALS:':<54} {float(total_wrvu):<12.2f} {format_currency(total_revenue):<15}")
    print(f"\nAnnualized Projections:")
    print(f"  Work RVUs: {float(total_wrvu * 12):,.2f}")
    print(f"  Revenue:   {format_currency(total_revenue * 12)}")
    
    # Example 7: Search functionality
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Search by Description")
    print("=" * 80)
    
    search_term = "bronchoscopy"
    results = parser.search_by_description(search_term)
    
    print(f"\nFound {len(results)} codes containing '{search_term}':")
    print(f"(Showing first 10)\n")
    
    for i, record in enumerate(results[:10]):
        print(f"{i+1}. {record.hcpcs_code}: {record.description}")
    
    # Example 8: Export to DataFrame
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Export Data")
    print("=" * 80)
    
    df = parser.to_dataframe()
    print(f"\nDataFrame created with {len(df)} records")
    print(f"Columns: {', '.join(df.columns[:8])}...")
    
    # Save bronchoscopy codes to CSV
    bronch_df = df[df['hcpcs_code'].str.startswith('316')]
    output_file = Path(__file__).parent / 'bronchoscopy_codes_2025.csv'
    bronch_df.to_csv(output_file, index=False)
    print(f"\nBronchoscopy codes exported to: {output_file}")
    
    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  • 2025 Conversion Factor: $32.35")
    print("  • Geographic adjustments can vary payment by 30-50%")
    print("  • Facility vs non-facility PE RVU differences significantly impact payment")
    print("  • Multiple procedure rules apply (50% for subsequent procedures)")
    print("  • Work RVUs are useful for productivity tracking")
    print("\nNext Steps:")
    print("  • Integrate with your proc_autocode module")
    print("  • Add real-time CMS data downloads")
    print("  • Implement modifier handling logic")
    print("  • Build API endpoints for RVU queries")
    print()


if __name__ == "__main__":
    main()
