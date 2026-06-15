import tempfile
import pandas as pd
import streamlit as st
from pathlib import Path
from src.extractor import extract_text, get_pdf_preview
from src.matcher import compute_match
from config import APP_ICON, APP_TITLE
from core.logger import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title = APP_TITLE, page_icon = APP_ICON, layout = "wide" )

#initalising the session state

if "resumes" not in st.session_state:
    st.session_state.resume = {}

if "selected_resume" not in st.session_state:
    st.session_state.selected_resume = None

if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

if "results" not in st.session_state:
    st.session_state.results = {}

if "previews" not in st.session_state:
    st.session_state.previews = {}

st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("Upload resume · Paste a job description · Get instant match analysis")
st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Resumes")

    upload_files = st.file_uploader("Upload one or more resumes",
                                    type = ["pdf"],
                                    accept_multiple_files = True)
    
    #Process the upload files

    if upload_files:
        for file in upload_files:
            name = file.name

            if name not in st.session_state.resume:
                with st.spinner(f"Extracting {name}..."):
                    try:

                        pdf_bytes = file.read()
                        preview_bytes = get_pdf_preview(pdf_bytes)
                        st.session_state.previews[name] = preview_bytes

                        with tempfile.NamedTemporaryFile(suffix = ".pdf", delete = False) as temp:
                            temp.write(pdf_bytes)
                            temp_path = Path(temp.name)

                        text = extract_text(temp_path)
                        temp_path.unlink()
                        st.session_state.resume[name] = text
                        logger.info(f"Resume stored: {name}")
                        st.success(f"{name} extracted")

                    except Exception as e:
                        logger.error(f"Failed to extract: {name} : {e}")
                        st.error(f"Failed to rad: {name}")
    
    if st.session_state.resume:
        st.divider()

        resume_names = list(st.session_state.resume.keys())

        selected = st.selectbox("Select resume to preview",
                                options = resume_names,
                                key = "selected_resume")
        
        if selected:
            st.markdown("**Fist page Preview: **")

            if selected in st.session_state.previews:
                st.image(
                    st.session_state.previews[selected],
                    caption = selected,
                    use_container_width = True
                )
            
            st.caption(f"Extracted: {len(st.session_state.resume[selected])} chars")

with col_right:
    st.subheader("Job Discription")

    jd_text = st.text_area(
        "Paste the job discription here",
        height = 400,
        placeholder = "e.g. We are looking for AI Engineer ...",
        key = "jd_text"
    )

    if len(jd_text) < 500:
        st.warning(f"JD seems too short — add more details for better matching")
    elif len(jd_text) > 5000:
        st.warning(f"JD is very long — consider pasting key requirements only")
    else:
        st.caption(f"{len(jd_text.split())} words — good length")

st.divider()

col_empty_left, col_btn, ccol_empty_right = st.columns([3, 4, 3])
with col_btn:
    analyze_clicked = st.button(
        "Analyze Match",
        type = "primary",
        use_container_width = True
    )

    if analyze_clicked:
        if not st.session_state.resume:
            st.warning("Please upload at least one Resume")
        elif not jd_text.strip():
            st.warning("Please paste a job description")
        else:
            selected = st.session_state.selected_resume
            resume_text = st.session_state.resume[selected]

            with st.spinner(f"Analysing {selected}..."):
                try:
                    result = compute_match(resume_text, jd_text)
                    st.session_state.results[selected] = result
                    logger.info(f"Analysis complete: {selected}")

                except Exception as e:
                    logger.error(f"Analysis failed for {selected}: {e}")
                    st.error("Analysis failed - please try again")

if st.session_state.results:
    selected = st.session_state.selected_resume

    if selected in st.session_state.results:
        results = st.session_state.results[selected]

        st.divider()
        st.subheader(f"Results - {selected}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label = "match Score",
                value = f"{result['match_percentage']}%"
            )

        with col2:
            st.metric(
                label = "Missing Skills",
                value = len(result['missing_skills'])
            )
        
        with col3:
            st.metric(
                label="Matched Skills",
                value=len(result['match_skills'])
            )
        
        verdict = result['verdict']
        if verdict == "Strong Match":
            st.success(f"{verdict}")
        elif verdict == "Good Match":
            st.info(f"{verdict}")
        elif verdict == "Weak Match":
            st.warning(f"{verdict}")
        else:
            st.error(f"{verdict}")
            
        col_match, col_miss = st.columns(2)

        with col_match:
            st.markdown("**Matched Skills**")
            for skill in result['match_skills']:
                st.markdown(f"- {skill}")

        with col_miss:
            st.markdown("**Missing Skills**")
            for skill in  result["missing_skills"]:
                st.markdown(f"- {skill}")


st.divider()
st.subheader("Summary - All Resumes")

if not st.session_state.results:
    st.info("Analyse resume to see summary here")
else:
    row = []

    for resume_name, result in st.session_state.results.items():
        row.append({
            "Resume": resume_name,
            "Match%": result["match_percentage"],
            "Matched Skills": len(result["match_skills"]),
            "Missing Skills": len(result["missing_skills"]),
            "Verdict": result["verdict"]
        })
    
    df = pd.DataFrame(row)
    df = df.sort_values("Match%", ascending = False)

    st.dataframe(
        df,
        use_container_width = True,
        hide_index = True
    )
        

