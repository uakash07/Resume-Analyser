import pandas as pd

def rank_candidates(results: list) -> pd.DataFrame:
    df = pd.DataFrame(results)

    df = df.sort_values(by="score", ascending=False)

    df = df.reset_index(drop=True)

    df.index = df.index + 1

    df.index.name = "Rank"

    df = df[["candidate_name", "score", "classification"]]

    df.columns = ["Candidate Name", "Score", "Classification"]

    return df
