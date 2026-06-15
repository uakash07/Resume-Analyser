import streamlit as st
import pandas as pd
from modules import extract_text, analyze_resume, rank_candidates

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon=None,
    layout="wide"
)

st.markdown(
    "<h1 style='text-align: center;'>AI Resume Analyzer</h1>"
    "<p style='text-align: center; color: gray;'>Upload a resume, paste a job description, and get an instant ATS-style analysis.</p>",
    unsafe_allow_html=True
)

st.divider()

mode = st.segmented_control(
    "Select Mode",
    ["Single Resume", "Bulk Ranking"],
    default="Single Resume",
    key="mode_selector"
)

st.divider()

# ── SINGLE RESUME MODE ──

if mode == "Single Resume":

    st.subheader("Single Resume Analysis")

    upload_col, jd_col = st.columns(2)

    with upload_col:
        resume_file = st.file_uploader(
            "Upload Resume (PDF)",
            type=["pdf"],
            key="single_uploader"
        )

    with jd_col:
        job_desc = st.text_area(
            "Job Description",
            height=250,
            placeholder="Paste the full job description here including required skills, responsibilities, and experience level.",
            key="single_jd"
        )

    analyze = st.button(
        "Analyze Resume",
        type="primary",
        use_container_width=True,
        key="single_btn"
    )

    if analyze:
        if resume_file is None:
            st.error("Please upload a resume PDF.")
        elif not job_desc.strip():
            st.error("Please enter a job description.")
        else:
            with st.status("Extracting text from PDF...", expanded=False) as status:
                resume_text = extract_text(resume_file)

                if not resume_text.strip():
                    status.update(label="Extraction failed", state="error")
                    st.error("Could not extract text. The PDF may be scanned or image-based.")
                else:
                    status.update(label="Text extracted successfully", state="complete")

            if resume_text.strip():
                with st.status("Analyzing with AI...", expanded=False) as status:
                    result = analyze_resume(resume_text, job_desc)
                    if "error" in result:
                        status.update(label="Analysis failed", state="error")
                        st.error(f"Analysis failed: {result['error']}")
                    else:
                        status.update(label="Analysis complete", state="complete")

                if "error" not in result:
                    st.divider()
                    st.subheader("Results")

                    score = result.get("match_percentage", 0)
                    rec = result.get("recommendation", "N/A")

                    sc_col, rec_col = st.columns([1, 2])
                    with sc_col:
                        st.metric("ATS Match Score", f"{score}%")
                    with rec_col:
                        if "Strong" in rec:
                            st.success(f"Recommendation: {rec}")
                        elif "Moderate" in rec:
                            st.warning(f"Recommendation: {rec}")
                        else:
                            st.error(f"Recommendation: {rec}")

                    st.divider()

                    match_col, partial_col, miss_col = st.columns(3)

                    with match_col:
                        matched = result.get("matching_skills", [])
                        st.markdown(f"**Matching Skills ({len(matched)})**")
                        if matched:
                            for s in matched:
                                st.success(s)
                        else:
                            st.caption("None identified")

                    with partial_col:
                        partial = result.get("partial_matching_skills", [])
                        st.markdown(f"**Partial Match ({len(partial)})**")
                        if partial:
                            for s in partial:
                                st.warning(s)
                        else:
                            st.caption("None identified")

                    with miss_col:
                        missing = result.get("missing_skills", [])
                        st.markdown(f"**Missing Skills ({len(missing)})**")
                        if missing:
                            for s in missing:
                                st.error(s)
                        else:
                            st.caption("None identified")

                    st.divider()

                    str_col, imp_col = st.columns(2)

                    with str_col:
                        st.markdown("**Strengths**")
                        for p in result.get("strengths", []):
                            st.markdown(f"- {p}")

                    with imp_col:
                        st.markdown("**Areas for Improvement**")
                        for p in result.get("improvements", []):
                            st.markdown(f"- {p}")

                    st.divider()
                    st.markdown("**AI Suggestions**")
                    st.markdown(result.get("ai_suggestions", "No suggestions available."))

# ── BULK RANKING MODE ──

elif mode == "Bulk Ranking":

    st.subheader("Bulk Resume Ranking")

    bc1, bc2 = st.columns(2)

    with bc1:
        files = st.file_uploader(
            "Upload Multiple Resumes (PDF)",
            type=["pdf"],
            accept_multiple_files=True,
            key="bulk_uploader"
        )

    with bc2:
        bulk_jd = st.text_area(
            "Job Description",
            height=250,
            placeholder="Paste the job description for ranking candidates against.",
            key="bulk_jd"
        )

    analyze_all = st.button(
        "Analyze All Resumes",
        type="primary",
        use_container_width=True,
        key="bulk_btn"
    )

    if analyze_all:
        if not files:
            st.error("Please upload at least one resume PDF.")
        elif not bulk_jd.strip():
            st.error("Please enter a job description.")
        else:
            all_results = []
            bar = st.progress(0, text="Starting...")
            total = len(files)

            for i, f in enumerate(files):
                name = f.name.replace(".pdf", "").replace("_", " ").replace("-", " ")
                bar.progress((i) / total, text=f"Processing {name} ({i+1}/{total})...")

                try:
                    text = extract_text(f)
                    if not text.strip():
                        st.warning(f"Skipped {name}: could not extract text.")
                        bar.progress((i + 1) / total, text=f"Skipped {name}")
                        continue

                    r = analyze_resume(text, bulk_jd)
                    if "error" in r:
                        st.warning(f"Skipped {name}: {r['error']}")
                        bar.progress((i + 1) / total, text=f"Skipped {name}")
                        continue

                    r["candidate_name"] = name
                    all_results.append(r)

                except Exception as e:
                    st.warning(f"Error on {name}: {e}")

                bar.progress((i + 1) / total, text=f"Done ({i+1}/{total})")

            bar.progress(1.0, text="All done!")

            if all_results:
                data = [
                    {
                        "candidate_name": r["candidate_name"],
                        "match_percentage": r.get("match_percentage", 0),
                        "recommendation": r.get("recommendation", "N/A")
                    }
                    for r in all_results
                ]
                df = rank_candidates(data)

                st.divider()
                st.subheader(f"Candidate Rankings ({len(df)} candidates)")

                def highlight_top3(row):
                    if row.name <= 3:
                        return ["background-color: #d4edda; color: #155724"] * len(row)
                    return [""] * len(row)

                st.dataframe(
                    df.style.apply(highlight_top3, axis=1),
                    use_container_width=True,
                    height=min(400, 50 + len(df) * 40)
                )

                st.divider()
                st.subheader("Detailed Results")

                for r in all_results:
                    with st.expander(f"{r['candidate_name']} - {r.get('match_percentage', 0)}% Match"):
                        c1, c2, c3 = st.columns(3)

                        with c1:
                            m = r.get("matching_skills", [])
                            st.markdown(f"**Matching ({len(m)})**")
                            for s in m:
                                st.success(s)

                        with c2:
                            p = r.get("partial_matching_skills", [])
                            st.markdown(f"**Partial ({len(p)})**")
                            for s in p:
                                st.warning(s)

                        with c3:
                            ms = r.get("missing_skills", [])
                            st.markdown(f"**Missing ({len(ms)})**")
                            for s in ms:
                                st.error(s)

                        st.markdown("**Improvements**")
                        for pt in r.get("improvements", []):
                            st.markdown(f"- {pt}")

                        st.markdown("**AI Suggestions**")
                        st.markdown(r.get("ai_suggestions", "N/A"))

            else:
                st.error("No resumes could be analyzed. Check your PDFs and try again.")
