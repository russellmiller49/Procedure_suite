#!/usr/bin/env python3
"""
Generate synthetic PHI training data for the DistilBERT NER model.

This script creates balanced training examples with:
- Patient names (various formats)
- Phone numbers (various formats)
- Dates (various formats)
- Emails, SSNs, MRNs, addresses

Output: JSONL file with WordPiece tokens and BIO tags aligned for training.
"""

import argparse
import json
import random
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer

# Sample data pools
FIRST_NAMES = [
    "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa",
    "William", "Jennifer", "James", "Maria", "Thomas", "Susan", "Charles",
    "Margaret", "Joseph", "Elizabeth", "Daniel", "Patricia", "Richard", "Linda",
    "Mark", "Barbara", "Steven", "Nancy", "Paul", "Karen", "Andrew", "Betty",
    "Kevin", "Dorothy", "Brian", "Sandra", "George", "Ashley", "Edward", "Kimberly",
    "Ronald", "Donna", "Timothy", "Carol", "Jason", "Michelle", "Jeffrey", "Amanda",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
]

STREET_NAMES = [
    "Main", "Oak", "Maple", "Cedar", "Pine", "Elm", "Park", "Lake", "Hill", "River",
    "Washington", "Lincoln", "Jefferson", "Madison", "Jackson", "Franklin", "Adams",
]

STREET_TYPES = ["St", "Ave", "Blvd", "Dr", "Ln", "Rd", "Way", "Ct", "Pl"]

CITIES = [
    "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
    "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville",
    "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", "Seattle",
    "Denver", "Boston", "Nashville", "Baltimore", "Oklahoma City", "Portland",
]

STATES = ["NY", "CA", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI", "NJ", "VA", "WA", "AZ", "MA", "TN", "IN", "MO", "MD", "WI"]

STATE_NAMES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa",
    "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan",
    "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
    "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota",
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia",
    "Wisconsin", "Wyoming",
]

FACILITY_BASES = [
    "Naval Medical Center", "Medical Center", "University Medical Center",
    "General Hospital", "Regional Hospital", "Memorial Hospital", "Community Hospital",
    "Children's Hospital", "University Hospital", "County Medical Center",
    "VA Medical Center", "Health Center", "Health System", "Cancer Center",
    "Pulmonary Institute", "Medical Clinic", "Specialty Clinic",
    "University of",
]

# Medical procedure context templates
PROCEDURE_TEMPLATES = [
    "Patient: {patient}. DOB: {date}. Phone: {phone}.",
    "PATIENT: {patient}\nDOB: {date}\nCONTACT: {phone}",
    "Name: {patient}, Date of Birth: {date}, Telephone: {phone}",
    "Pt {patient} (DOB {date}) contacted at {phone}.",
    "OPERATIVE REPORT\nPatient Name: {patient}\nDate of Procedure: {date}\nContact Number: {phone}",
    "Pre-procedure checklist completed for {patient}, DOB {date}. Callback: {phone}.",
    "Consent obtained from {patient} on {date}. Emergency contact: {phone}.",
    "Patient {patient} scheduled for bronchoscopy on {date}. Phone: {phone}.",
    "PROCEDURE NOTE\nPatient: {patient}\nProcedure Date: {date}\nPhone: {phone}\nIndication: Lung nodule evaluation",
    "{patient} presented on {date} for diagnostic bronchoscopy. Contact: {phone}.",
    "Follow-up call to {patient} at {phone} scheduled for {date}.",
    "Medical Record for {patient}\nBirth Date: {date}\nPhone Number: {phone}",
    "Admission date: {date}\nPatient: {patient}\nContact phone: {phone}",
    "Email confirmation sent to {email} for {patient}, appointment {date}.",
    "SSN ending in {ssn_last4} verified for {patient}. DOB: {date}.",
    "MRN: {mrn} - {patient}, DOB {date}, Phone {phone}",
    "Address: {address}\nPatient: {patient}\nDOB: {date}",
    "Facility: {facility}\nPatient: {patient}\nDOB: {date}",
    "Procedure performed at {facility} on {date}. Patient: {patient}.",
    "Transferred to {facility}. Patient {patient} scheduled for bronchoscopy on {date}.",
    "Operative location: {facility}\nMRN: {mrn}\nPatient: {patient}",
]

# Templates with just names
NAME_TEMPLATES = [
    "Attending physician: Dr. {patient}",
    "Resident: {patient}",
    "Procedure performed by {patient}",
    "Nurse: {patient}",
    "Patient {patient} arrived for procedure.",
    "Consent signed by {patient}.",
    "Family member {patient} was notified.",
    "Emergency contact: {patient}",
]

# Templates with just dates
DATE_TEMPLATES = [
    "Procedure scheduled for {date}.",
    "Follow-up appointment: {date}",
    "Last seen on {date}.",
    "Results received {date}.",
    "Biopsy performed {date}.",
    "CT scan dated {date}.",
    "Lab work from {date}.",
    "Discharge date: {date}",
]

# Templates with just phones
PHONE_TEMPLATES = [
    "Call back at {phone}.",
    "Contact number: {phone}",
    "Phone: {phone}",
    "Telephone: {phone}",
    "Fax: {phone}",
    "Callback requested: {phone}",
]


def generate_name(format_type: str = "full") -> str:
    """Generate a random name in various formats."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    formats = {
        "full": f"{first} {last}",
        "last_first": f"{last}, {first}",
        "initial": f"{first[0]}. {last}",
        "last_initial": f"{last}, {first[0]}.",
        "first_only": first,
        "last_only": last,
    }
    return formats.get(format_type, formats["full"])


def generate_date(format_type: str = "slash") -> str:
    """Generate a random date in various formats."""
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    year = random.randint(1940, 2024)

    formats = {
        "slash": f"{month:02d}/{day:02d}/{year}",
        "slash_short": f"{month}/{day}/{year % 100:02d}",
        "dash": f"{year}-{month:02d}-{day:02d}",
        "long": f"{['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month-1]} {day}, {year}",
        "short_month": f"{['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month-1]} {day}, {year}",
        "dot": f"{month:02d}.{day:02d}.{year}",
    }
    return formats.get(format_type, formats["slash"])


def generate_phone(format_type: str = "dash") -> str:
    """Generate a random phone number in various formats."""
    area = random.randint(200, 999)
    prefix = random.randint(200, 999)
    line = random.randint(1000, 9999)

    formats = {
        "dash": f"{area}-{prefix}-{line}",
        "dot": f"{area}.{prefix}.{line}",
        "paren": f"({area}) {prefix}-{line}",
        "plain": f"{area}{prefix}{line}",
        "space": f"{area} {prefix} {line}",
    }
    return formats.get(format_type, formats["dash"])


def generate_email() -> str:
    """Generate a random email address."""
    first = random.choice(FIRST_NAMES).lower()
    last = random.choice(LAST_NAMES).lower()
    domain = random.choice(["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "email.com"])
    formats = [
        f"{first}.{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{first[0]}{last}@{domain}",
        f"{last}.{first}@{domain}",
    ]
    return random.choice(formats)


def generate_ssn_last4() -> str:
    """Generate last 4 digits of SSN."""
    return f"{random.randint(1000, 9999)}"


def generate_mrn() -> str:
    """Generate a medical record number."""
    formats = [
        f"{random.randint(100000, 999999)}",
        f"MRN{random.randint(10000, 99999)}",
        f"{random.choice(['A', 'B', 'C', 'M', 'P'])}{random.randint(100000, 999999)}",
    ]
    return random.choice(formats)


def generate_address() -> str:
    """Generate a random address."""
    number = random.randint(100, 9999)
    street = random.choice(STREET_NAMES)
    street_type = random.choice(STREET_TYPES)
    city = random.choice(CITIES)
    state = random.choice(STATES)
    zip_code = random.randint(10000, 99999)

    formats = [
        f"{number} {street} {street_type}",
        f"{number} {street} {street_type}, {city}, {state}",
        f"{number} {street} {street_type}, {city}, {state} {zip_code}",
    ]
    return random.choice(formats)


def generate_facility_name() -> str:
    """Generate a facility name with city/state suffix at the end."""
    base = random.choice(FACILITY_BASES)
    city = random.choice(CITIES)
    state = random.choice(STATE_NAMES)
    suffix_style = random.choice(["city", "city_state", "state"])

    if base.lower().endswith("of"):
        return f"{base} {state}"

    if suffix_style == "city":
        return f"{base} {city}"
    if suffix_style == "city_state":
        return f"{base} {city} {state}"
    return f"{base} {state}"


def tokenize_and_tag(
    text: str,
    tokenizer: Any,
    entities: list[dict],
) -> tuple[list[str], list[str]]:
    """
    Tokenize text and align BIO tags to tokens.

    Args:
        text: The raw text
        tokenizer: HuggingFace tokenizer
        entities: List of dicts with 'start', 'end', 'label' keys

    Returns:
        Tuple of (tokens, ner_tags)
    """
    # Tokenize with offset mapping
    encoding = tokenizer(
        text,
        return_offsets_mapping=True,
        add_special_tokens=False,
    )

    tokens = tokenizer.convert_ids_to_tokens(encoding["input_ids"])
    offsets = encoding["offset_mapping"]

    # Initialize all tags as O
    ner_tags = ["O"] * len(tokens)

    # Sort entities by start position
    sorted_entities = sorted(entities, key=lambda e: e["start"])

    # Assign BIO tags based on character offsets
    for entity in sorted_entities:
        ent_start = entity["start"]
        ent_end = entity["end"]
        label = entity["label"]
        is_first = True

        for i, (tok_start, tok_end) in enumerate(offsets):
            # Skip special tokens (offset 0,0)
            if tok_start == tok_end:
                continue

            # Check if token overlaps with entity
            if tok_start >= ent_start and tok_end <= ent_end:
                if is_first:
                    ner_tags[i] = f"B-{label}"
                    is_first = False
                else:
                    ner_tags[i] = f"I-{label}"
            elif tok_start < ent_end and tok_end > ent_start:
                # Partial overlap
                if is_first:
                    ner_tags[i] = f"B-{label}"
                    is_first = False
                else:
                    ner_tags[i] = f"I-{label}"

    return tokens, ner_tags


def generate_example(
    tokenizer: Any,
    template_type: str = "mixed",
) -> dict:
    """Generate a single training example."""

    entities = []

    if template_type == "mixed":
        template = random.choice(PROCEDURE_TEMPLATES)

        # Generate all PHI values
        name_format = random.choice(["full", "last_first", "initial"])
        date_format = random.choice(["slash", "slash_short", "dash", "long", "short_month"])
        phone_format = random.choice(["dash", "dot", "paren"])

        patient = generate_name(name_format)
        date = generate_date(date_format)
        phone = generate_phone(phone_format)
        email = generate_email()
        ssn_last4 = generate_ssn_last4()
        mrn = generate_mrn()
        address = generate_address()
        facility = generate_facility_name()

        # Build text with placeholders
        text = template.format(
            patient=patient,
            date=date,
            phone=phone,
            email=email,
            ssn_last4=ssn_last4,
            mrn=mrn,
            address=address,
            facility=facility,
        )

        # Find entity positions
        if "{patient}" in template:
            start = text.find(patient)
            if start >= 0:
                entities.append({"start": start, "end": start + len(patient), "label": "PATIENT"})

        if "{date}" in template:
            start = text.find(date)
            if start >= 0:
                entities.append({"start": start, "end": start + len(date), "label": "DATE"})

        if "{phone}" in template:
            start = text.find(phone)
            if start >= 0:
                entities.append({"start": start, "end": start + len(phone), "label": "CONTACT"})

        if "{email}" in template:
            start = text.find(email)
            if start >= 0:
                entities.append({"start": start, "end": start + len(email), "label": "CONTACT"})

        if "{ssn_last4}" in template:
            start = text.find(ssn_last4)
            if start >= 0:
                entities.append({"start": start, "end": start + len(ssn_last4), "label": "ID"})

        if "{mrn}" in template:
            start = text.find(mrn)
            if start >= 0:
                entities.append({"start": start, "end": start + len(mrn), "label": "ID"})

        if "{address}" in template:
            start = text.find(address)
            if start >= 0:
                entities.append({"start": start, "end": start + len(address), "label": "GEO"})

        if "{facility}" in template:
            start = text.find(facility)
            if start >= 0:
                entities.append({"start": start, "end": start + len(facility), "label": "GEO"})

    elif template_type == "name":
        template = random.choice(NAME_TEMPLATES)
        name_format = random.choice(["full", "last_first", "initial", "first_only", "last_only"])
        patient = generate_name(name_format)
        text = template.format(patient=patient)
        start = text.find(patient)
        if start >= 0:
            entities.append({"start": start, "end": start + len(patient), "label": "PATIENT"})

    elif template_type == "date":
        template = random.choice(DATE_TEMPLATES)
        date_format = random.choice(["slash", "slash_short", "dash", "long", "short_month", "dot"])
        date = generate_date(date_format)
        text = template.format(date=date)
        start = text.find(date)
        if start >= 0:
            entities.append({"start": start, "end": start + len(date), "label": "DATE"})

    elif template_type == "phone":
        template = random.choice(PHONE_TEMPLATES)
        phone_format = random.choice(["dash", "dot", "paren", "plain", "space"])
        phone = generate_phone(phone_format)
        text = template.format(phone=phone)
        start = text.find(phone)
        if start >= 0:
            entities.append({"start": start, "end": start + len(phone), "label": "CONTACT"})

    else:
        raise ValueError(f"Unknown template type: {template_type}")

    # Tokenize and tag
    tokens, ner_tags = tokenize_and_tag(text, tokenizer, entities)

    return {
        "text": text,
        "tokens": tokens,
        "ner_tags": ner_tags,
        "entities": entities,
        "origin": "synthetic-phi",
    }


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic PHI training data")
    parser.add_argument("--output", "-o", default="data/ml_training/synthetic_phi_data.jsonl",
                        help="Output JSONL file path")
    parser.add_argument("--count", "-n", type=int, default=2000,
                        help="Number of examples to generate")
    parser.add_argument("--tokenizer", default="distilbert-base-uncased",
                        help="Tokenizer to use for WordPiece tokenization")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    random.seed(args.seed)

    print(f"Loading tokenizer: {args.tokenizer}")
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, use_fast=True)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate balanced examples
    # 40% mixed (all PHI types), 20% names, 20% dates, 20% phones
    type_distribution = {
        "mixed": int(args.count * 0.4),
        "name": int(args.count * 0.2),
        "date": int(args.count * 0.2),
        "phone": int(args.count * 0.2),
    }

    examples = []

    for template_type, count in type_distribution.items():
        print(f"Generating {count} {template_type} examples...")
        for i in range(count):
            try:
                example = generate_example(tokenizer, template_type)
                example["id"] = f"synthetic_{template_type}_{i}"
                examples.append(example)
            except Exception as e:
                print(f"Error generating example: {e}")
                continue

    # Shuffle examples
    random.shuffle(examples)

    # Write to JSONL
    print(f"Writing {len(examples)} examples to {output_path}")
    with open(output_path, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    # Print statistics
    entity_counts = {"PATIENT": 0, "DATE": 0, "CONTACT": 0, "ID": 0, "GEO": 0}
    for ex in examples:
        for tag in ex["ner_tags"]:
            if tag.startswith("B-"):
                label = tag[2:]
                if label in entity_counts:
                    entity_counts[label] += 1

    print("\nEntity counts:")
    for label, count in sorted(entity_counts.items()):
        print(f"  {label}: {count}")

    print(f"\nDone! Generated {len(examples)} examples.")


if __name__ == "__main__":
    main()
