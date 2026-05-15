def test_ranking_order():

    jobs = [
        {"title": "Backend Engineer", "score": 0.9},
        {"title": "Frontend Engineer", "score": 0.3},
    ]

    ranked = sorted(jobs, key=lambda x: x["score"], reverse=True)

    assert ranked[0]["title"] == "Backend Engineer"