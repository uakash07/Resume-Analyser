import pandas as pd  # import pandas library for DataFrame creation and manipulation

def rank_candidates(results: list) -> pd.DataFrame:  # define function taking list of result dicts, returning sorted DataFrame
    """Create a ranked DataFrame of candidates sorted by match percentage."""  # docstring

    df = pd.DataFrame(results)  # create a pandas DataFrame from the list of candidate result dictionaries

    df = df.sort_values(by="match_percentage", ascending=False)  # sort rows by match_percentage column in descending order (highest first)

    df = df.reset_index(drop=True)  # reset the index after sorting, dropping the old index values

    df.index = df.index + 1  # shift index to start from 1 instead of 0 to represent rank numbers

    df.index.name = "Rank"  # name the index column "Rank" for display clarity

    df = df[["candidate_name", "match_percentage", "recommendation"]]  # keep only the three relevant columns for the ranking table

    df.columns = ["Candidate Name", "Match %", "Recommendation"]  # rename columns to user-friendly display names

    return df  # return the final sorted and formatted DataFrame
