from projections import project_offense


def sample_baselines():
    return {
        "pass_attempts": 30,
        "yards_per_attempt": 7,
        "td_rate": 0.05,
        "int_rate": 0.02,
        "rush_attempts": 5,
        "yards_per_rush": 4.5,
        "rush_td_rate": 0.03,
        "targets": 8,
        "catch_rate": 0.65,
        "yards_per_rec": 12,
        "rec_td_rate": 0.05,
    }


def test_shape_and_points():
    cat, pts, var = project_offense(sample_baselines(), proe=0.0, waf=1.0)
    assert pts > 0 and var > 0
    for key in ["PassYds", "RushYds", "Rec", "RecYds"]:
        assert key in cat


def test_proe_increases_targets():
    base = sample_baselines()
    cat_low, _, _ = project_offense(base, proe=0.0, waf=1.0)
    cat_high, _, _ = project_offense(base, proe=0.5, waf=1.0)
    assert cat_high["Rec"] > cat_low["Rec"]


def test_weather_sensitivity():
    base = sample_baselines()
    cat_good, _, _ = project_offense(base, proe=0.0, waf=1.0)
    cat_bad, _, _ = project_offense(base, proe=0.0, waf=0.5)
    assert cat_bad["PassYds"] < cat_good["PassYds"]
