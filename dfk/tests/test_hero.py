from pathlib import Path
import pytest

import pandas as pd

from dfk.apps.apibase import PROFESSIONS_MAP, EndpointType
from dfk.apps.hero import run_matching


PROFESSIONS = {'fishing', 'foraging', 'mining', 'gardening'}


@pytest.fixture
def endpoint() -> EndpointType:
    return EndpointType.APIV6


@pytest.fixture
def test_data() -> pd.DataFrame:
    '''
    This data should fulfill the following (for each profession):
        - test a profession match (w/ 1-2 aligned stat boosts)
        - test that a class mismatch excludes the sale
        - test that mismatches on BOTH stat boosts exclude the sale
    '''
    with open(f'{Path(__file__).parent}/data/test_v6.csv', 'r', encoding='utf-8') as f:
        df = pd.read_csv(f)

    # maintain type str to stay consistent with v5, even though v6 uses ints
    df.mainclass = df.mainclass.astype('string')
    df.subclass =  df.subclass.astype('string')

    return df


@pytest.fixture
def startedat_key(endpoint: EndpointType) -> str:
    if endpoint is EndpointType.APIV5:
        from dfk.apps.apiv5 import (
            MAINCLASS_KEY, PROFESSION_KEY, STATBOOST1_KEY, STATBOOST2_KEY, STARTEDAT_KEY
        )
    elif endpoint is EndpointType.APIV6:
        from dfk.apps.apiv6 import (
            MAINCLASS_KEY, PROFESSION_KEY, STATBOOST1_KEY, STATBOOST2_KEY, STARTEDAT_KEY
        )

    return STARTEDAT_KEY


def test_run_matching_profession_match(test_data: pd.DataFrame, startedat_key: str):
    match_df = run_matching(test_data, startedat_key)

    assert len(match_df) == len(PROFESSIONS)
    assert set(match_df.profession) == PROFESSIONS

    for _, row in match_df.iterrows():
        assert row.mainclass in PROFESSIONS_MAP[row.profession]['class']
        assert (row.statboost1 in PROFESSIONS_MAP[row.profession]['stats']) or (row.statboost2 in PROFESSIONS_MAP[row.profession]['stats'])
