import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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

                    score = result.get("score", 0)
                    classification = result.get("classification", "N/A")
                    domain = result.get("job_domain", "")

                    sc_col, cls_col, dm_col = st.columns(3)
                    with sc_col:
                        st.metric("ATS Score", f"{score}/100")
                    with cls_col:
                        if "Excellent" in classification:
                            st.success(f"Classification: {classification}")
                        elif "Strong" in classification:
                            st.success(f"Classification: {classification}")
                        elif "Potential" in classification:
                            st.warning(f"Classification: {classification}")
                        elif "Partial" in classification:
                            st.warning(f"Classification: {classification}")
                        else:
                            st.error(f"Classification: {classification}")
                    with dm_col:
                        if domain:
                            st.info(f"Domain: {domain}")

                    st.divider()

                    match_col, trans_col, miss_col = st.columns(3)

                    with match_col:
                        matched = result.get("matching_skills", [])
                        st.markdown(f"**Matching Skills ({len(matched)})**")
                        if matched:
                            for s in matched:
                                st.success(s)
                        else:
                            st.caption("None identified")

                    with trans_col:
                        transferable = result.get("transferable_skills", [])
                        st.markdown(f"**Transferable Skills ({len(transferable)})**")
                        if transferable:
                            for s in transferable:
                                st.warning(s)
                        else:
                            st.caption("None identified")

                    with miss_col:
                        missing = result.get("missing_critical_skills", [])
                        st.markdown(f"**Missing Critical Skills ({len(missing)})**")
                        if missing:
                            for s in missing:
                                st.error(s)
                        else:
                            st.caption("None identified")

                    st.divider()

                    breakdown = result.get("scoring_breakdown", {})
                    st.markdown("**Scoring Breakdown**")
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        st.metric("Technical Skills", f"{breakdown.get('technical_skills', 0)}/100")
                        st.metric("Domain Experience", f"{breakdown.get('domain_experience', 0)}/100")
                    with b2:
                        st.metric("Projects", f"{breakdown.get('projects', 0)}/100")
                        st.metric("Education", f"{breakdown.get('education', 0)}/100")
                    with b3:
                        st.metric("Certifications", f"{breakdown.get('certifications', 0)}/100")
                        st.metric("Soft Skills", f"{breakdown.get('soft_skills', 0)}/100")

                    st.divider()

                    st.markdown("**Analysis Visualizations**")

                    w1, w2 = st.columns(2)

                    with w1:
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=score,
                            domain=dict(x=[0, 1], y=[0, 1]),
                            number=dict(suffix="/100", font=dict(size=36)),
                            gauge=dict(
                                axis=dict(range=[0, 100], tickwidth=1, tickcolor="gray"),
                                bar=dict(color="#1f77b4", thickness=0.3),
                                steps=[
                                    dict(range=[0, 39], color="#ffcccc"),
                                    dict(range=[39, 59], color="#ffe6cc"),
                                    dict(range=[59, 74], color="#ffffcc"),
                                    dict(range=[74, 89], color="#ccffcc"),
                                    dict(range=[89, 100], color="#99ff99"),
                                ],
                                threshold=dict(
                                    line=dict(color="red", width=4),
                                    thickness=0.75,
                                    value=score
                                )
                            )
                        ))
                        fig.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig, use_container_width=True)

                    with w2:
                        categories = ["Technical\nSkills", "Domain\nExp.", "Projects", "Education", "Certifications", "Soft\nSkills"]
                        weights = [40, 25, 15, 10, 5, 5]
                        cat_scores = [
                            breakdown.get("technical_skills", 0),
                            breakdown.get("domain_experience", 0),
                            breakdown.get("projects", 0),
                            breakdown.get("education", 0),
                            breakdown.get("certifications", 0),
                            breakdown.get("soft_skills", 0),
                        ]
                        weighted_scores = [s * w / 100 for s, w in zip(cat_scores, weights)]

                        fig2 = go.Figure()
                        fig2.add_trace(go.Bar(
                            y=categories,
                            x=weighted_scores,
                            name="Weighted Contribution",
                            orientation="h",
                            marker=dict(color="#1f77b4"),
                            text=[f"{s:.1f}" for s in weighted_scores],
                            textposition="outside",
                        ))
                        fig2.add_trace(go.Bar(
                            y=categories,
                            x=[w / 100 * 100 for w in weights],
                            name="Max Possible",
                            orientation="h",
                            marker=dict(color="lightgray", opacity=0.4),
                            text=[f"max {w}%" for w in weights],
                            textposition="inside",
                        ))
                        fig2.update_layout(
                            barmode="overlay",
                            height=280,
                            margin=dict(l=20, r=20, t=20, b=20),
                            xaxis=dict(title="Points Contributed to Final Score", range=[0, 42]),
                            showlegend=False,
                        )
                        st.plotly_chart(fig2, use_container_width=True)

                    st.caption("Left: Overall ATS score with color-coded zones. Right: Each category's weighted contribution to the final score (gray = max possible, blue = actual).")

                    st.divider()

                    st.markdown("**Areas for Improvement**")
                    for p in result.get("improvements", []):
                        st.markdown(f"- {p}")

                    st.divider()
                    st.markdown("**Recruiter Summary**")
                    st.markdown(result.get("recruiter_summary", "No summary available."))

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
                        "score": r.get("score", 0),
                        "classification": r.get("classification", "N/A")
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
                    with st.expander(f"{r['candidate_name']} - Score: {r.get('score', 0)}/100"):
                        c1, c2, c3 = st.columns(3)

                        with c1:
                            m = r.get("matching_skills", [])
                            st.markdown(f"**Matching ({len(m)})**")
                            for s in m:
                                st.success(s)

                        with c2:
                            t = r.get("transferable_skills", [])
                            st.markdown(f"**Transferable ({len(t)})**")
                            for s in t:
                                st.warning(s)

                        with c3:
                            ms = r.get("missing_critical_skills", [])
                            st.markdown(f"**Missing Critical ({len(ms)})**")
                            for s in ms:
                                st.error(s)

                        st.markdown("**Improvements**")
                        for pt in r.get("improvements", []):
                            st.markdown(f"- {pt}")

                        st.markdown("**Recruiter Summary**")
                        st.markdown(r.get("recruiter_summary", "N/A"))

            else:
                st.error("No resumes could be analyzed. Check your PDFs and try again.")
