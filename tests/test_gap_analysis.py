from src.analysis.gap_analysis import analyze_keywords
from src.ingest.resume_reader import read_resume
from src.nlp.embeddings import EmbeddingClient


def test_missing_keyword_detection(tmp_path):
    resume_path = tmp_path / "resume.txt"
    resume_path.write_text(
        "Engineer\nExperience:\n- Built APIs with Python and SQL\nSkills:\nPython, SQL"
    )
    resume = read_resume(resume_path)
    keywords = ["docker", "sql"]
    client = EmbeddingClient()
    matches = analyze_keywords(resume, keywords, client)
    categories = {match.keyword: match.category for match in matches}
    assert categories["docker"] == "missing"
    assert categories["sql"] != "missing"
