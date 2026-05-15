from resume.resume import build_user_profile

def test_profile_builder(sample_resume_text):

    profile = build_user_profile(sample_resume_text)
    print(profile)

    assert "Python" in profile["skills"]