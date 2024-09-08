import os
import streamlit as st

import pdfkit
from functions import create_chapters, write_next_chapter, summarize

from dotenv import load_dotenv

load_dotenv()

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"


# If no API key is set, ask for it
if not st.session_state.api_key:
    api_key = st.sidebar.text_input(
        "Open AI API Key", value=os.getenv("OPENAI_API_KEY") or "", type="password"
    )
    submit_api_key = st.sidebar.button("Submit API Key")

    if submit_api_key and api_key:
        st.session_state.api_key = api_key
        st.rerun()
else:

    st.title("Create An Ebook")
    input_title = st.text_input("Book Title")
    input_description = st.text_input("Book Description")
    input_number = st.selectbox("Number Of Chapters", list(range(1, 21)), index=6)
    input_words = st.number_input("Words Per Chapter", value=350, step=1)
    submit_button = st.button("Submit")

    if submit_button and input_title:

        chapter_list = []
        ebook_content = ""
        summary_so_far = ""

        with st.spinner("Creating chapter list..."):
            try:
                response_list = create_chapters(
                    number=input_number,
                    title=input_title,
                    description=input_description,
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
                raise

            for field in response_list:
                st.write(field.strip() + ",")
                chapter_list.append(field.strip())

        for i, chapter in enumerate(chapter_list):

            ebook_content += f"<h1>Chapter {i+1}: {chapter}</h2> \n\n"

            with st.spinner(f"Writing Chapter {i+1}..."):
                try:
                    response = write_next_chapter(
                        book_name=input_title,
                        book_description=input_description,
                        chapter_number=i + 1,
                        chapter_name=chapter_list[i],
                        summary_so_far=summary_so_far,
                        number_of_words=input_words,
                    )
                except Exception as e:
                    st.error(f"An error occurred while writing chapter {i+1}: {e}")
                    raise

                st.title(f"CHAPTER {i+1}: {chapter_list[i]}")
                st.write(response)
                ebook_content += response.replace("\n", "</p><p>")
                ebook_content = "<p>" + ebook_content + "</p><br/><br/><br/>"

            with st.spinner(f"Thinking about chapter {i+1}..."):
                # summary length is a fraction of the number of words, but must be between 50 and 150
                summary_length = max(min(round(input_words / 7), 100), 50)
                try:
                    summary = summarize(input=response, number_of_words=summary_length)
                except Exception as e:
                    st.error(f"An error occurred summarizing with OpenAI: {e}")
                    raise

                if len(summary_so_far.split()) > 1200:
                    st.write("Summary exceeds 1000 words, reducing with LLM")
                    with st.spinner("Reviewing the story so far... "):
                        try:
                            summary = summarize(
                                input=summary_so_far, number_of_words=600
                            )
                        except Exception as e:
                            st.error(
                                f"An error occurred while summarizing the summary so far: {e}"
                            )
                            raise

                # We always want the most recent chapter in full
                summary_so_far += f"Chapter {i+1} Summary: {summary} \n\n"

                st.title(f"CHAPTER {i + 1} Summary")
                st.write(summary)

        file_name = f'{input_title.strip().replace(" ", "_")}.pdf'
        file_path = f"/home/alkai333/ebook-writer/ebooks/{file_name}"

        try:
            pdfkit.from_string(ebook_content, file_path, options={"encoding": "UTF-8"})
        except Exception as e:
            st.error(f"An error occurred while creating the PDF: {e}")
            raise

        st.success("Ebook content written to file successfully!")

        try:
            with open(file_path, "rb") as f:
                data = f.read()
        except Exception as e:
            st.error(f"An error occurred while reading the file: {e}")
            raise

        st.download_button("Download Ebook", data, file_name, "application/pdf")
