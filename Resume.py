import pandas as pd
import streamlit as st
import openai
from difflib import SequenceMatcher
from docx import Document
from io import BytesIO
import fitz  # PyMuPDF
# import bcrypt
import base64


# Set your OpenAI API key here
with st.sidebar:
        openai.api_key = st.text_input("Add your open API Key",type="Password")
data=[]

# Function to calculate similarity ratio between strings
def similarity_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_completion(prompt, model="gpt-3.5-turbo-16k"):
    messages = [{"role": "user", "content": prompt}]
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.7,
    )
    
    return response.choices[0].message["content"]

st.title("Generate Matching Resume")

job_description= st.text_area("Enter Job Description")
# File upload for job description
job_description_file = st.file_uploader("Upload Job Description", type=["txt", "pdf", "docx"])

# File upload for resume
resume_files = st.file_uploader("Upload Your Resume", type=["txt", "pdf", "docx"],accept_multiple_files=True)

if st.button("Generate Resume") and (job_description_file or job_description) is not None and resume_files is not None:
    
    # Read content from uploaded job description file
    
    
    # Check if it's a DOCX file
    if job_description_file is not None:
            job_description_content = job_description_file.read()
            if job_description_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = Document(BytesIO(job_description_content))
                job_description = "\n".join(para.text for para in doc.paragraphs)
            elif job_description_file.type == "application/pdf":
                pdf = fitz.open(stream=job_description_content, filetype="pdf")
                job_description = ""
                for page_num in range(pdf.page_count):
                    page = pdf[page_num]
                    job_description += page.get_text()
            else:
                # Assume it's a text file
                job_description = job_description_content.decode("utf-8")


    # for resume_file in resume_files: 
    i=0
    while i<len(resume_files):   
        # Read content from uploaded resume file
        resume_file=resume_files[i]
        resume_content = resume_file.read()
        
        # Check if it's a DOCX file
        if resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(BytesIO(resume_content))
            resume_input = "\n".join(para.text for para in doc.paragraphs)
        elif resume_file.type == "application/pdf":
            pdf = fitz.open(stream=resume_content, filetype="pdf")
            resume_input = ""
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                resume_input += page.get_text()
        else:
            # Assume it's a text file
            resume_input = resume_content.decode("utf-8")

    
        input_text = f""" Your task is to compare the resume with the job_description provided. Provide the results in terms of percentage of suitability for the job. And provide me the reason on what basis you have provided the percentage.
                
                job_description :{job_description}
                resume: {resume_input}

            """
        
        generated_resume = get_completion(input_text)
        # st.write(generated_resume)  # Generate the resume using your function

        # Calculate matching rating
        # match_rating = similarity_ratio(resume_input, job_description)

        # Display the generated resume
        # st.subheader("Generated Resume")
        # st.write(generated_resume)

        # Display matching rating circular progress bar
        # st.subheader("Matching Rating")

        # Calculate percentage
        # match_percentage = int(match_rating * 100)

        data.append({"Name":resume_file.name ,"Match percentage":generated_resume})
        i=i+1
    df = pd.DataFrame(data)
    st.write(df)
    
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Encode to base64
    href = f'<a href="data:file/csv;base64,{b64}" download="data.csv"> Click On For Download CSV File</a>'
    st.markdown(href, unsafe_allow_html=True)

        # Create custom HTML for circular progress bar
        # html_code = f"""
        # <div style="text-align: center;">
        #     <div style="position: relative; display: inline-block;">
        #         <div class="circular-progress">
        #             <div class="inner" style="width: {match_percentage}%;"></div>
        #             <div class="label">{match_percentage}% Match</div>
        #         </div>
        #     </div>
        # </div>
        # """

        # # Render the HTML component
        # st.components.v1.html(html_code, width=200, height=200)

        # # Display matching percentage
        # st.write(f"Matching Percentage: {match_percentage}%")
        # st.progress(match_percentage)
