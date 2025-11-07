from src.networking.models import Contact
from src.networking.scoring import calculate_score, rank_contacts


def test_calculate_score_matches_formula():
    contact = Contact(
        name="Ada Lovelace",
        email="ada@example.com",
        relationship_strength=4,
        overlap_skills=3,
        mutuals_count=2,
        recent_activity=1,
        cold_days_since_last_touch=200,
    )

    score = calculate_score(contact)
    # 3*4 + 2*3 + 2*2 + 1*1 - 1 = 12 + 6 + 4 + 1 - 1 = 22
    assert score == 22


def test_rank_contacts_sorts_descending():
    contacts = [
        Contact(name="A", email="a@example.com", relationship_strength=5),
        Contact(name="B", email="b@example.com", relationship_strength=2),
    ]

    ranked = rank_contacts(contacts)
    assert ranked[0].name == "A"
    assert ranked[0].score > ranked[1].score
