from modules.pdf_reader import extract_text  # import extract_text function from pdf_reader module
from modules.analyzer import analyze_resume  # import analyze_resume function from analyzer module
from modules.ranker import rank_candidates  # import rank_candidates function from ranker module
__all__ = ["extract_text", "analyze_resume", "rank_candidates"]  # declare public API of this package
