from src.analysis.star import generate_star_bullets


def test_star_bullet_length_and_structure():
    bullets = generate_star_bullets(
        role="Data Scientist",
        company="Analytics Inc",
        requirement="Deliver predictive models for marketing impact",
        resume_line="Led A/B experiments improving conversion",
        n=2,
    )
    assert len(bullets) == 2
    for bullet in bullets:
        word_count = len(bullet.bullet.split())
        assert word_count <= 35
        assert "S:" in bullet.rationale
