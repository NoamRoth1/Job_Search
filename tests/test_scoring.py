from src.analysis.gap_analysis import analyze_keywords
from src.analysis.match_scoring import score_resume
from src.ingest.job_reader import read_job
from src.ingest.resume_reader import read_resume
from src.nlp.embeddings import EmbeddingClient


def test_ats_score_improves_with_more_keywords(tmp_path):
    resume_path = tmp_path / "resume.txt"
    resume_path.write_text(
        "Engineer\nExperience:\n- Built dashboards\nSkills:\nSQL"
    )
    job_path = tmp_path / "job.txt"
    job_path.write_text(
        "Data Engineer\nCompany\nResponsibilities:\n- Manage ETL pipelines\nQualifications:\n- Experience with SQL and Docker"
    )

    resume = read_resume(resume_path)
    job = read_job(job_path)
    keywords = ["sql", "docker"]
    client = EmbeddingClient()
    matches = analyze_keywords(resume, keywords, client)
    base_score = score_resume(resume, job, matches)

    improved_matches = matches.copy()
    improved_matches[1].category = "present"
    improved_matches[1].similarity = 0.9
    better_score = score_resume(resume, job, improved_matches)

    assert better_score.total >= base_score.total
