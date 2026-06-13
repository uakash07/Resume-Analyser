import streamlit as st
import pandas as pd
from modules import extract_text, analyze_resume, rank_candidates

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon=None,
    layout="wide"
)

st.title("AI Resume Analyzer")

st.markdown("---")

mode = st.radio(
    "Select Analysis Mode:",
    ["Single Resume Analysis", "Bulk Resume Ranking"],
    horizontal=True
)

st.markdown("---")

# MODE 1: SINGLE RESUME ANALYSIS

if mode == "Single Resume Analysis":

    st.subheader("Single Resume Analysis")

    col1, col2 = st.columns([1, 1])

    with col1:
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF)",
            type=["pdf"],
            key="single_uploader"
        )

    with col2:
        job_description = st.text_area(
            "Paste Job Description",
            height=200,
            placeholder="Paste the full job description here...",
            key="single_jd"
        )

    analyze_btn = st.button(
            "Analyze Resume",
        key="single_analyze",
        use_container_width=True
    )

    if analyze_btn:

        if not uploaded_file:
            st.error("Please upload a resume PDF before analyzing.")
        elif not job_description.strip():
            st.error("Please paste a job description before analyzing.")
        else:

            with st.spinner("Extracting text from PDF..."):
                resume_text = extract_text(uploaded_file)

            if not resume_text.strip():
                st.error("Could not extract text from the PDF. It may be a scanned/image-based PDF.")
            else:

                with st.spinner("Analyzing with AI..."):
                    result = analyze_resume(resume_text, job_description)

                if "error" in result:
                    st.error(f"Analysis failed: {result['error']}")
                else:

                    st.markdown("---")
                    st.subheader("Analysis Results")

                    # Match Percentage + Recommendation
                    match_pct = result.get("match_percentage", 0)

                    metric_col, rec_col = st.columns([1, 2])

                    with metric_col:
                        st.metric(
                            label="ATS Match Score",
                            value=f"{match_pct}%"
                        )

                    with rec_col:
                        recommendation = result.get("recommendation", "N/A")

                        if "Strong" in recommendation:
                            st.success(f"**Recommendation:** {recommendation}")
                        elif "Moderate" in recommendation:
                            st.warning(f"**Recommendation:** {recommendation}")
                        else:
                            st.error(f"**Recommendation:** {recommendation}")

                    st.markdown("---")

                    # Skills Section
                    skills_col1, skills_col2 = st.columns(2)

                    with skills_col1:
                        st.markdown("### Matching Skills")
                        matching_skills = result.get("matching_skills", [])

                        if matching_skills:
                            for skill in matching_skills:
                                st.success(f"{skill}")
                        else:
                            st.info("No matching skills identified.")

                    with skills_col2:
                        st.markdown("### Missing Skills")
                        missing_skills = result.get("missing_skills", [])

                        if missing_skills:
                            for skill in missing_skills:
                                st.error(f"{skill}")
                        else:
                            st.success("No missing skills - your resume covers all JD requirements!")

                    st.markdown("---")

                    # Strengths & Improvements
                    str_col, imp_col = st.columns(2)

                    with str_col:
                        st.markdown("### Strengths")
                        strengths = result.get("strengths", [])

                        for point in strengths:
                            st.markdown(f"- {point}")

                    with imp_col:
                        st.markdown("### Areas for Improvement")
                        improvements = result.get("improvements", [])

                        for point in improvements:
                            st.markdown(f"- {point}")

                    st.markdown("---")

                    # AI Suggestions (plain text, no colored box)
                    st.markdown("### AI-Powered Suggestions")
                    ai_suggestions = result.get("ai_suggestions", "No suggestions available.")
                    st.markdown(ai_suggestions)

# MODE 2: BULK RESUME RANKING

elif mode == "Bulk Resume Ranking":

    st.subheader("Bulk Resume Ranking")

    bulk_col1, bulk_col2 = st.columns([1, 1])

    with bulk_col1:
        uploaded_files = st.file_uploader(
            "Upload Multiple Resumes (PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            key="bulk_uploader"
        )

    with bulk_col2:
        bulk_jd = st.text_area(
            "Paste Job Description",
            height=200,
            placeholder="Paste the full job description here...",
            key="bulk_jd"
        )

    analyze_all_btn = st.button(
            "Analyze All Resumes",
        key="bulk_analyze",
        use_container_width=True
    )

    if analyze_all_btn:

        if not uploaded_files:
            st.error("Please upload at least one resume PDF.")
        elif not bulk_jd.strip():
            st.error("Please paste a job description before analyzing.")
        else:

            all_results = []

            progress_bar = st.progress(0)

            total_files = len(uploaded_files)

            status_text = st.empty()

            for idx, pdf_file in enumerate(uploaded_files):

                candidate_name = pdf_file.name.replace(".pdf", "").replace("_", " ").replace("-", " ")

                status_text.text(f"Analyzing {candidate_name} ({idx + 1}/{total_files})...")

                try:

                    resume_text = extract_text(pdf_file)

                    if not resume_text.strip():
                        st.warning(f"Skipping {candidate_name}: Could not extract text (may be scanned PDF).")
                        progress_bar.progress((idx + 1) / total_files)
                        continue

                    with st.spinner(f"Analyzing {candidate_name}..."):
                        result = analyze_resume(resume_text, bulk_jd)

                    if "error" in result:
                        st.warning(f"Skipping {candidate_name}: {result['error']}")
                        progress_bar.progress((idx + 1) / total_files)
                        continue

                    result["candidate_name"] = candidate_name

                    all_results.append(result)

                except Exception as e:
                    st.warning(f"Error processing {candidate_name}: {str(e)}")

                progress_bar.progress((idx + 1) / total_files)

            status_text.text("Analysis complete!")

            if all_results:

                ranking_data = [
                    {
                        "candidate_name": r["candidate_name"],
                        "match_percentage": r.get("match_percentage", 0),
                        "recommendation": r.get("recommendation", "N/A")
                    }
                    for r in all_results
                ]

                ranked_df = rank_candidates(ranking_data)

                st.markdown("---")
                st.subheader(f"Candidate Rankings ({len(ranked_df)} candidates)")

                def highlight_top3(row):
                    """Return green background style for top 3 ranked rows."""
                    rank = row.name
                    if rank <= 3:
                        return ["background-color: #d4edda; color: #155724"] * len(row)
                    return [""] * len(row)

                styled_df = ranked_df.style.apply(highlight_top3, axis=1)

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    height=min(400, 50 + len(ranked_df) * 40)
                )

                st.markdown("---")

                st.subheader("Detailed Results")

                for r in all_results:

                    with st.expander(f"{r['candidate_name']} - {r.get('match_percentage', 0)}% Match"):

                        detail_col1, detail_col2 = st.columns(2)

                        with detail_col1:
                            st.markdown("**Matching Skills**")
                            for skill in r.get("matching_skills", []):
                                st.success(f"{skill}")

                        with detail_col2:
                            st.markdown("**Missing Skills**")
                            for skill in r.get("missing_skills", []):
                                st.error(f"{skill}")

                        st.markdown("**AI Suggestions:**")
                        st.markdown(r.get("ai_suggestions", "N/A"))

            else:
                st.error("No resumes could be analyzed successfully. Please check your PDFs and try again.")
