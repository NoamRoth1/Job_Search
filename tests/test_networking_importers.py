import pytest

from src.networking.importers import CSVImportError, parse_contacts_csv


def test_parse_contacts_csv_assigns_scores():
    csv_text = """name,email,company,role,relationship,notes,relationship_strength,overlap_skills,mutuals_count,recent_activity,cold_days_since_last_touch\n"""
    csv_text += "Ada Lovelace,ada@example.com,Analytical Engines,Advisor,Peer,Met at hackathon,4,3,1,2,30\n"

    contacts = parse_contacts_csv(csv_text)
    assert len(contacts) == 1
    contact = contacts[0]
    assert contact.relationship_strength == 4
    assert contact.mutuals_count == 1


def test_parse_contacts_csv_validates_required_columns():
    csv_text = "name,email\nAda,ada@example.com\n"
    with pytest.raises(CSVImportError):
        parse_contacts_csv(csv_text)
