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
    horizontal=True,
    key="mode_selector"
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
            placeholder="Paste the full job description here. The more detail you provide, the more accurate the analysis will be.",
            key="single_jd"
        )

    if job_description and len(job_description.strip()) < 50:
        st.warning("Your job description looks very short. For accurate analysis, paste the full job description including required skills, responsibilities, and experience level.")

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
                st.error("Could not extract text. This PDF may be scanned or image-based.")
            else:

                with st.spinner("Analyzing resume with AI -- this may take 10-15 seconds..."):
                    result = analyze_resume(resume_text, job_description)

                if "error" in result:
                    st.error(f"Analysis failed: {result['error']}")
                else:

                    st.markdown("---")
                    st.subheader("Analysis Results")

                    match_pct = result.get("match_percentage", 0)
                    recommendation = result.get("recommendation", "N/A")

                    metric_col, rec_col = st.columns([1, 2])

                    with metric_col:
                        st.metric(label="ATS Match Score", value=f"{match_pct}%")

                    with rec_col:
                        if "Strong" in recommendation:
                            st.success(f"Recommendation: {recommendation}")
                        elif "Moderate" in recommendation:
                            st.warning(f"Recommendation: {recommendation}")
                        else:
                            st.error(f"Recommendation: {recommendation}")

                    st.markdown("---")

                    # SKILLS SECTION
                    skills_col1, skills_col2, skills_col3 = st.columns(3)

                    with skills_col1:
                        matching_skills = result.get("matching_skills", [])
                        st.markdown(f"### Matching Skills ({len(matching_skills)})")
                        if matching_skills:
                            for skill in matching_skills:
                                st.success(skill)
                        else:
                            st.info("No matching skills found.")

                    with skills_col2:
                        partial_skills = result.get("partial_matching_skills", [])
                        st.markdown(f"### Partial Match ({len(partial_skills)})")
                        if partial_skills:
                            for skill in partial_skills:
                                st.warning(skill)
                        else:
                            st.info("No partial matches identified.")

                    with skills_col3:
                        missing_skills = result.get("missing_skills", [])
                        st.markdown(f"### Missing Skills ({len(missing_skills)})")
                        if missing_skills:
                            for skill in missing_skills:
                                st.error(skill)
                        else:
                            st.success("Your resume covers all required skills!")

                    st.markdown("---")

                    # STRENGTHS AND IMPROVEMENTS
                    str_col, imp_col = st.columns(2)

                    with str_col:
                        strengths = result.get("strengths", [])
                        st.markdown(f"### Strengths ({len(strengths)})")
                        for point in strengths:
                            st.markdown(f"- {point}")

                    with imp_col:
                        improvements = result.get("improvements", [])
                        st.markdown(f"### Areas for Improvement ({len(improvements)})")
                        for point in improvements:
                            st.markdown(f"- {point}")

                    st.markdown("---")

                    # AI SUGGESTIONS
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
            placeholder="Paste the full job description. More detail = more accurate ranking.",
            key="bulk_jd"
        )

    if bulk_jd and len(bulk_jd.strip()) < 50:
        st.warning("Job description looks very short. Paste the full description for accurate ranking.")

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
                        st.warning(f"Skipping {candidate_name}: could not extract text.")
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

            status_text.text("All resumes analyzed!")

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
                    if row.name <= 3:
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

                        detail_col1, detail_col2, detail_col3 = st.columns(3)

                        with detail_col1:
                            matching = r.get("matching_skills", [])
                            st.markdown(f"**Matching Skills ({len(matching)})**")
                            for skill in matching:
                                st.success(skill)

                        with detail_col2:
                            partial = r.get("partial_matching_skills", [])
                            st.markdown(f"**Partial Match ({len(partial)})**")
                            for skill in partial:
                                st.warning(skill)

                        with detail_col3:
                            missing = r.get("missing_skills", [])
                            st.markdown(f"**Missing Skills ({len(missing)})**")
                            for skill in missing:
                                st.error(skill)

                        st.markdown("**Areas for Improvement**")
                        for point in r.get("improvements", []):
                            st.markdown(f"- {point}")

                        st.markdown("**AI Suggestions**")
                        st.markdown(r.get("ai_suggestions", "N/A"))

            else:
                st.error("No resumes could be analyzed. Please check your PDFs and try again.")
