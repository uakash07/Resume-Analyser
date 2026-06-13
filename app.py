import streamlit as st  # import Streamlit for building the web UI
import pandas as pd  # import pandas for DataFrame handling
from modules import extract_text, analyze_resume, rank_candidates  # import all core module functions

st.set_page_config(  # configure page settings
    page_title="AI Resume Analyzer",  # browser tab title
    page_icon="📄",  # browser tab favicon
    layout="wide"  # full-width layout
)

st.title("📄 AI Resume Analyzer")  # main heading

st.markdown("---")  # top divider

mode = st.radio(  # mode selector radio buttons
    "Select Analysis Mode:",
    ["Single Resume Analysis", "Bulk Resume Ranking"],
    horizontal=True,
    key="mode_selector"
)

st.markdown("---")  # divider below mode selector

# ─────────────────────────────────────────────────────────────
# MODE 1: SINGLE RESUME ANALYSIS
# ─────────────────────────────────────────────────────────────

if mode == "Single Resume Analysis":  # single resume mode

    st.subheader("🔍 Single Resume Analysis")  # section heading

    col1, col2 = st.columns([1, 1])  # two equal-width side-by-side columns

    with col1:  # left column: PDF uploader
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF)",
            type=["pdf"],
            key="single_uploader"
        )

    with col2:  # right column: job description input
        job_description = st.text_area(
            "Paste Job Description",
            height=200,
            placeholder="Paste the full job description here. The more detail you provide, the more accurate and precise the analysis will be.",
            key="single_jd"
        )

    # warning shown when JD is too short to be useful
    if job_description and len(job_description.strip()) < 50:  # check if JD is suspiciously short
        st.warning("⚠️ Your job description looks very short. For accurate analysis, paste the full job description including required skills, responsibilities, and experience level.")

    analyze_btn = st.button(  # analyze trigger button
        "🚀 Analyze Resume",
        key="single_analyze",
        use_container_width=True
    )

    if analyze_btn:  # when button is clicked

        if not uploaded_file:  # no file uploaded
            st.error("⚠️ Please upload a resume PDF before analyzing.")
        elif not job_description.strip():  # no job description entered
            st.error("⚠️ Please paste a job description before analyzing.")
        else:  # both inputs present, proceed

            with st.spinner("📖 Extracting text from PDF..."):  # spinner while reading PDF
                resume_text = extract_text(uploaded_file)  # extract all text from PDF pages

            if not resume_text.strip():  # empty = scanned/image PDF
                st.error("❌ Could not extract text. This PDF may be scanned or image-based.")
            else:

                with st.spinner("🤖 Analyzing resume with AI — this may take 10–15 seconds..."):  # spinner while AI runs
                    result = analyze_resume(resume_text, job_description)  # run AI analysis

                if "error" in result:  # AI returned an error dict
                    st.error(f"❌ Analysis failed: {result['error']}")
                else:  # analysis succeeded, render all result sections

                    st.markdown("---")
                    st.subheader("📊 Analysis Results")  # results section header

                    match_pct = result.get("match_percentage", 0)  # get match score
                    recommendation = result.get("recommendation", "N/A")  # get recommendation label

                    metric_col, rec_col = st.columns([1, 2])  # columns for score and recommendation

                    with metric_col:  # left: big numeric score
                        st.metric(label="ATS Match Score", value=f"{match_pct}%")

                    with rec_col:  # right: color-coded recommendation badge
                        if "Strong" in recommendation:
                            st.success(f"✅ **Recommendation:** {recommendation}")
                        elif "Moderate" in recommendation:
                            st.warning(f"⚠️ **Recommendation:** {recommendation}")
                        else:
                            st.error(f"❌ **Recommendation:** {recommendation}")

                    st.markdown("---")

                    # ── SKILLS SECTION ───────────────────────────────────────
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

                    # ── STRENGTHS & IMPROVEMENTS ──────────────────────────────
                    str_col, imp_col = st.columns(2)  # two-column layout

                    with str_col:  # strengths column
                        strengths = result.get("strengths", [])
                        st.markdown(f"### 💪 Strengths ({len(strengths)})")
                        for point in strengths:
                            st.markdown(f"- {point}")  # bullet point per strength

                    with imp_col:  # improvements column
                        improvements = result.get("improvements", [])
                        st.markdown(f"### 🔧 Areas for Improvement ({len(improvements)})")
                        for point in improvements:
                            st.markdown(f"- {point}")  # bullet point per improvement

                    st.markdown("---")

                    # ── AI SUGGESTIONS ────────────────────────────────────────
                    # plain text only — no blue info box as requested
                    st.markdown("### 🧠 AI-Powered Suggestions")
                    ai_suggestions = result.get("ai_suggestions", "No suggestions available.")
                    st.markdown(ai_suggestions)  # render as plain markdown text, no colored container

# ─────────────────────────────────────────────────────────────
# MODE 2: BULK RESUME RANKING
# ─────────────────────────────────────────────────────────────

elif mode == "Bulk Resume Ranking":  # bulk ranking mode

    st.subheader("📋 Bulk Resume Ranking")  # section heading

    bulk_col1, bulk_col2 = st.columns([1, 1])  # two-column layout

    with bulk_col1:  # multi-file uploader
        uploaded_files = st.file_uploader(
            "Upload Multiple Resumes (PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            key="bulk_uploader"
        )

    with bulk_col2:  # job description input
        bulk_jd = st.text_area(
            "Paste Job Description",
            height=200,
            placeholder="Paste the full job description. More detail = more accurate ranking.",
            key="bulk_jd"
        )

    # warning if JD is too short
    if bulk_jd and len(bulk_jd.strip()) < 50:
        st.warning("⚠️ Job description looks very short. Paste the full description for accurate ranking.")

    analyze_all_btn = st.button(  # bulk analyze button
        "🚀 Analyze All Resumes",
        key="bulk_analyze",
        use_container_width=True
    )

    if analyze_all_btn:  # when bulk analyze button is clicked

        if not uploaded_files:
            st.error("⚠️ Please upload at least one resume PDF.")
        elif not bulk_jd.strip():
            st.error("⚠️ Please paste a job description before analyzing.")
        else:

            all_results = []  # list to collect all successful results
            progress_bar = st.progress(0)  # progress bar starts at 0
            total_files = len(uploaded_files)  # count total uploaded files
            status_text = st.empty()  # dynamic status text placeholder

            for idx, pdf_file in enumerate(uploaded_files):  # loop through each PDF

                candidate_name = pdf_file.name.replace(".pdf", "").replace("_", " ").replace("-", " ")  # clean filename as candidate name

                status_text.text(f"⏳ Analyzing {candidate_name} ({idx + 1}/{total_files})...")

                try:
                    resume_text = extract_text(pdf_file)  # extract resume text

                    if not resume_text.strip():  # unreadable PDF
                        st.warning(f"⚠️ Skipping {candidate_name}: could not extract text.")
                        progress_bar.progress((idx + 1) / total_files)
                        continue  # skip to next file

                    with st.spinner(f"🤖 Analyzing {candidate_name}..."):
                        result = analyze_resume(resume_text, bulk_jd)  # AI analysis for this candidate

                    if "error" in result:  # analysis failed for this candidate
                        st.warning(f"⚠️ Skipping {candidate_name}: {result['error']}")
                        progress_bar.progress((idx + 1) / total_files)
                        continue

                    result["candidate_name"] = candidate_name  # attach name to result
                    all_results.append(result)  # add to results collection

                except Exception as e:
                    st.warning(f"⚠️ Error processing {candidate_name}: {str(e)}")

                progress_bar.progress((idx + 1) / total_files)  # advance progress bar

            status_text.text("✅ All resumes analyzed!")  # final status

            if all_results:  # at least one successful result

                ranking_data = [  # build minimal dicts for ranking function
                    {
                        "candidate_name": r["candidate_name"],
                        "match_percentage": r.get("match_percentage", 0),
                        "recommendation": r.get("recommendation", "N/A")
                    }
                    for r in all_results
                ]

                ranked_df = rank_candidates(ranking_data)  # sort into ranked DataFrame

                st.markdown("---")
                st.subheader(f"🏆 Candidate Rankings ({len(ranked_df)} candidates)")

                def highlight_top3(row):  # row styling function
                    if row.name <= 3:  # top 3 get green background
                        return ["background-color: #d4edda; color: #155724"] * len(row)
                    return [""] * len(row)

                styled_df = ranked_df.style.apply(highlight_top3, axis=1)  # apply row highlighting

                st.dataframe(  # render styled ranked table
                    styled_df,
                    use_container_width=True,
                    height=min(400, 50 + len(ranked_df) * 40)
                )

                st.markdown("---")
                st.subheader("📋 Detailed Results")  # expandable per-candidate details

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

                        st.markdown("**🧠 AI Suggestions**")
                        st.markdown(r.get("ai_suggestions", "N/A"))  # plain text, no colored box

            else:  # no results at all
                st.error("❌ No resumes could be analyzed. Please check your PDFs and try again.")
