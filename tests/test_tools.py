from agent.tools import get_candidate_profile, match_skills


def test_get_candidate_profile_has_expected_shape():
    profile = get_candidate_profile()
    assert "competences" in profile
    assert "projets" in profile
    assert len(profile["competences"]) > 0


def test_match_skills_finds_real_overlap():
    result = match_skills(["Python", "Docker", "FastAPI"])
    assert result["score_adequation"] == 1.0
    assert set(result["competences_correspondantes"]) == {"Python", "Docker", "FastAPI"}
    assert result["competences_manquantes"] == []


def test_match_skills_flags_missing_skills():
    result = match_skills(["Python", "COBOL", "Fortran"])
    assert "Python" in result["competences_correspondantes"]
    assert "COBOL" in result["competences_manquantes"]
    assert "Fortran" in result["competences_manquantes"]
    assert 0 < result["score_adequation"] < 1


def test_match_skills_is_case_and_accent_insensitive():
    result = match_skills(["PYTHON", "docker"])
    assert result["score_adequation"] == 1.0


def test_match_skills_handles_empty_list():
    result = match_skills([])
    assert result["competences_correspondantes"] == []
    assert result["competences_manquantes"] == []
