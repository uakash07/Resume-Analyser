import streamlit as st  # import Streamlit for building the web interface
import pandas as pd  # import pandas for DataFrame display and styling
from modules import extract_text, analyze_resume, rank_candidates  # import all three core functions from modules package

st.set_page_config(  # configure Streamlit page settings
    page_title="AI RESUME ANALYZER",  # set the browser tab title
    page_icon="",  # set the browser tab icon to document emoji
    layout="wide"  # use wide layout to utilize full screen width
)

st.title("AI Resume Analyzer")  # render the main page title at the top

st.markdown("---")  # render a horizontal divider line below the title

mode = st.radio(  # create a radio button widget for mode selection
    "Select Analysis Mode:",  # label shown above the radio buttons
    ["Single Resume Analysis", "Bulk Resume Ranking"],  # two available mode options
    horizontal=True  # display radio buttons side by side horizontally
)

st.markdown("---")  # render another horizontal divider below the mode selector

# ─────────────────────────────────────────────────────────────
# MODE 1: SINGLE RESUME ANALYSIS
# ─────────────────────────────────────────────────────────────

if mode == "Single Resume Analysis":  # check if user selected single resume mode

    st.subheader("🔍 Single Resume Analysis")  # render sub-heading for this mode

    col1, col2 = st.columns([1, 1])  # create two equal-width columns for layout

    with col1:  # enter the left column context
        uploaded_file = st.file_uploader(  # render a file upload widget
            "Upload Resume (PDF)",  # label for the uploader
            type=["pdf"],  # restrict uploads to PDF files only
            key="single_uploader"  # unique key to identify this widget
        )

    with col2:  # enter the right column context
        job_description = st.text_area(  # render a multi-line text input widget
            "Paste Job Description",  # label for the text area
            height=200,  # set height of the text area in pixels
            placeholder="Paste the job description here...",  # hint text shown when empty
            key="single_jd"  # unique key to identify this widget
        )

    analyze_btn = st.button(  # render the analyze button
        "🚀 Analyze Resume",  # button label text
        key="single_analyze",  # unique key for this button
        use_container_width=True  # stretch button to full container width
    )

    if analyze_btn:  # check if the analyze button was clicked

        if not uploaded_file:  # validate that a PDF was uploaded
            st.error("⚠️ Please upload a resume PDF before analyzing.")  # show error if no file uploaded
        elif not job_description.strip():  # validate that job description is not empty
            st.error("⚠️ Please paste a job description before analyzing.")  # show error if JD is empty
        else:  # both inputs are valid, proceed with analysis

            with st.spinner("📖 Extracting text from PDF..."):  # show spinner while reading PDF
                resume_text = extract_text(uploaded_file)  # call pdf_reader to extract text from uploaded PDF

            if not resume_text.strip():  # check if extracted text is empty (e.g., scanned image PDF)
                st.error("❌ Could not extract text from the PDF. It may be a scanned/image-based PDF.")  # show error for image PDFs
            else:  # text extraction succeeded

                with st.spinner("Analyzing resume..."):  # show spinner while calling Gemini API
                    result = analyze_resume(resume_text, job_description)  # call analyzer to get structured analysis dict

                if "error" in result:  # check if the analysis returned an error
                    st.error(f"❌ Analysis failed: {result['error']}")  # display the error message to user
                else:  # analysis succeeded, display results

                    st.markdown("---")  # render divider before results section
                    st.subheader("📊 Analysis Results")  # render results section heading

                    # ── Match Percentage Metric ──
                    match_pct = result.get("match_percentage", 0)  # safely get match percentage with default 0

                    metric_col, rec_col = st.columns([1, 2])  # create columns for metric and recommendation

                    with metric_col:  # enter metric column
                        st.metric(  # render a big metric display widget
                            label="ATS Match Score",  # label above the number
                            value=f"{match_pct}%"  # display percentage with % sign
                        )

                    with rec_col:  # enter recommendation column
                        recommendation = result.get("recommendation", "N/A")  # safely get recommendation string

                        if "Strong" in recommendation:  # check if recommendation is Strong Match
                            st.success(f"✅ **Recommendation:** {recommendation}")  # show green success box
                        elif "Moderate" in recommendation:  # check if recommendation is Moderate Match
                            st.warning(f"⚠️ **Recommendation:** {recommendation}")  # show yellow warning box
                        else:  # recommendation is Weak Match
                            st.error(f"❌ **Recommendation:** {recommendation}")  # show red error box

                    st.markdown("---")  # render divider between sections

                    # ── Skills Section ──
                    skills_col1, skills_col2 = st.columns(2)  # create two columns for matching vs missing skills

                    with skills_col1:  # enter matching skills column
                        st.markdown("### ✅ Matching Skills")  # render matching skills heading
                        matching_skills = result.get("matching_skills", [])  # safely get list of matching skills

                        if matching_skills:  # check if there are any matching skills to display
                            for skill in matching_skills:  # loop through each matching skill
                                st.success(f"✔ {skill}")  # display each skill as a green success badge
                        else:  # no matching skills found
                            st.info("No matching skills identified.")  # show neutral info message

                    with skills_col2:  # enter missing skills column
                        st.markdown("### ❌ Missing Skills")  # render missing skills heading
                        missing_skills = result.get("missing_skills", [])  # safely get list of missing skills

                        if missing_skills:  # check if there are any missing skills to display
                            for skill in missing_skills:  # loop through each missing skill
                                st.error(f"✘ {skill}")  # display each skill as a red error badge
                        else:  # no missing skills found
                            st.info("No missing skills identified.")  # show neutral info message

                    st.markdown("---")  # render divider between sections

                    # ── Strengths & Improvements ──
                    str_col, imp_col = st.columns(2)  # create two columns for strengths and improvements

                    with str_col:  # enter strengths column
                        st.markdown("### 💪 Strengths")  # render strengths section heading
                        strengths = result.get("strengths", [])  # safely get strengths list

                        for point in strengths:  # loop through each strength point
                            st.markdown(f"- {point}")  # render each strength as a bullet point

                    with imp_col:  # enter improvements column
                        st.markdown("### 🔧 Areas for Improvement")  # render improvements section heading
                        improvements = result.get("improvements", [])  # safely get improvements list

                        for point in improvements:  # loop through each improvement point
                            st.markdown(f"- {point}")  # render each improvement as a bullet point

                    st.markdown("---")  # render divider before AI suggestions

                    # ── AI Suggestions ──
                    st.markdown("### 🧠 AI-Powered Suggestions")  # render suggestions section heading
                    ai_suggestions = result.get("ai_suggestions", "No suggestions available.")  # safely get suggestions string
                    st.info(f"💡 {ai_suggestions}")  # display suggestions in a blue info box

# ─────────────────────────────────────────────────────────────
# MODE 2: BULK RESUME RANKING
# ─────────────────────────────────────────────────────────────

elif mode == "Bulk Resume Ranking":  # check if user selected bulk ranking mode

    st.subheader("📋 Bulk Resume Ranking")  # render sub-heading for bulk mode

    bulk_col1, bulk_col2 = st.columns([1, 1])  # create two equal-width columns for layout

    with bulk_col1:  # enter left column for file uploader
        uploaded_files = st.file_uploader(  # render multi-file uploader widget
            "Upload Multiple Resumes (PDF)",  # label for the uploader
            type=["pdf"],  # restrict to PDF files only
            accept_multiple_files=True,  # allow selecting multiple files at once
            key="bulk_uploader"  # unique key to identify this widget
        )

    with bulk_col2:  # enter right column for job description
        bulk_jd = st.text_area(  # render multi-line text input for job description
            "Paste Job Description",  # label for the text area
            height=200,  # set text area height in pixels
            placeholder="Paste the job description here...",  # hint text when empty
            key="bulk_jd"  # unique key to identify this widget
        )

    analyze_all_btn = st.button(  # render the bulk analyze button
        "🚀 Analyze All Resumes",  # button label text
        key="bulk_analyze",  # unique key for this button
        use_container_width=True  # stretch button to full container width
    )

    if analyze_all_btn:  # check if the analyze all button was clicked

        if not uploaded_files:  # validate that at least one PDF was uploaded
            st.error("⚠️ Please upload at least one resume PDF.")  # show error if no files uploaded
        elif not bulk_jd.strip():  # validate that job description is not empty
            st.error("⚠️ Please paste a job description before analyzing.")  # show error if JD is empty
        else:  # inputs are valid, proceed with bulk analysis

            all_results = []  # initialize empty list to collect each candidate's analysis result

            progress_bar = st.progress(0)  # create a progress bar starting at 0%

            total_files = len(uploaded_files)  # get total count of uploaded files for progress calculation

            status_text = st.empty()  # create an empty placeholder for dynamic status messages

            for idx, pdf_file in enumerate(uploaded_files):  # loop through each uploaded PDF with index

                candidate_name = pdf_file.name.replace(".pdf", "").replace("_", " ").replace("-", " ")  # derive candidate name from filename by removing extension and replacing separators

                status_text.text(f"⏳ Analyzing {candidate_name} ({idx + 1}/{total_files})...")  # update status message with current candidate

                try:  # wrap each analysis in try-except to handle individual failures gracefully

                    resume_text = extract_text(pdf_file)  # extract text from current PDF file

                    if not resume_text.strip():  # check if text extraction yielded empty result
                        st.warning(f"⚠️ Skipping {candidate_name}: Could not extract text (may be scanned PDF).")  # warn about unreadable PDF
                        progress_bar.progress((idx + 1) / total_files)  # update progress bar even for skipped files
                        continue  # skip to next file without adding to results

                    with st.spinner(f"🤖 Gemini analyzing {candidate_name}..."):  # show spinner for current candidate
                        result = analyze_resume(resume_text, bulk_jd)  # call Gemini to analyze current resume

                    if "error" in result:  # check if this analysis returned an error
                        st.warning(f"⚠️ Skipping {candidate_name}: {result['error']}")  # warn user about this failure
                        progress_bar.progress((idx + 1) / total_files)  # update progress bar for failed file
                        continue  # skip failed candidate and move to next

                    result["candidate_name"] = candidate_name  # add the candidate name to their result dict

                    all_results.append(result)  # add this candidate's result to the collected results list

                except Exception as e:  # catch any unexpected error for this candidate
                    st.warning(f"⚠️ Error processing {candidate_name}: {str(e)}")  # warn user about the exception

                progress_bar.progress((idx + 1) / total_files)  # update progress bar after processing each file

            status_text.text("✅ Analysis complete!")  # update status text when all files are processed

            if all_results:  # check if we have any successful results to rank

                ranking_data = [  # build list of simplified dicts for the ranking function
                    {  # each dict contains only the fields needed by rank_candidates
                        "candidate_name": r["candidate_name"],  # candidate name from the result
                        "match_percentage": r.get("match_percentage", 0),  # match percentage with fallback 0
                        "recommendation": r.get("recommendation", "N/A")  # recommendation with fallback N/A
                    }
                    for r in all_results  # iterate over all collected results
                ]

                ranked_df = rank_candidates(ranking_data)  # call ranker to get sorted DataFrame

                st.markdown("---")  # render divider before ranked table
                st.subheader(f"🏆 Candidate Rankings ({len(ranked_df)} candidates)")  # render table heading with count

                def highlight_top3(row):  # define function to apply conditional row styling
                    """Return green background style for top 3 ranked rows."""  # docstring
                    rank = row.name  # get the rank (index value) for the current row
                    if rank <= 3:  # check if this row is in the top 3
                        return ["background-color: #d4edda; color: #155724"] * len(row)  # return green style for all cells
                    return [""] * len(row)  # return no style for rows outside top 3

                styled_df = ranked_df.style.apply(highlight_top3, axis=1)  # apply row-wise highlight function to the DataFrame

                st.dataframe(  # render the styled DataFrame as an interactive table
                    styled_df,  # pass the styled DataFrame
                    use_container_width=True,  # stretch table to full container width
                    height=min(400, 50 + len(ranked_df) * 40)  # set dynamic height based on row count
                )

                st.markdown("---")  # render divider after the table

                st.subheader("📋 Detailed Results")  # render heading for detailed breakdown section

                for r in all_results:  # loop through each candidate's full result

                    with st.expander(f"📄 {r['candidate_name']} — {r.get('match_percentage', 0)}% Match"):  # create collapsible expander for each candidate

                        detail_col1, detail_col2 = st.columns(2)  # create two columns for skills display

                        with detail_col1:  # enter left column for matching skills
                            st.markdown("**✅ Matching Skills**")  # render matching skills sub-heading
                            for skill in r.get("matching_skills", []):  # loop through matching skills
                                st.success(f"✔ {skill}")  # display each matching skill as green badge

                        with detail_col2:  # enter right column for missing skills
                            st.markdown("**❌ Missing Skills**")  # render missing skills sub-heading
                            for skill in r.get("missing_skills", []):  # loop through missing skills
                                st.error(f"✘ {skill}")  # display each missing skill as red badge

                        st.markdown("**🧠 AI Suggestions:**")  # render AI suggestions label
                        st.info(r.get("ai_suggestions", "N/A"))  # display suggestions in blue info box

            else:  # no results were successfully analyzed
                st.error("❌ No resumes could be analyzed successfully. Please check your PDFs and try again.")  # show final error
