from ranking.scoring import compute_resume_score

def compute_resume_score():

    resume_skills = {"skills": ["Python", "SQL"]}
    job_skills = {"skills": ["Python", "AWS"]}

    score = compute_resume_score(resume_skills, job_skills)

    assert score > 0