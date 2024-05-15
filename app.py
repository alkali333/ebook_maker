import streamlit as st
import os
from dotenv import load_dotenv
import csv

from functions import create_chapters, write_next_chapter, summarize


load_dotenv()


st.title("Create An Ebook")
input_title = st.text_input(
    "Book Title", value="The History Of Cambodia Through The Eyes Of Cats"
)
input_description = st.text_input("Book Description")
submit_button = st.button("Submit")


if submit_button and input_title:

    chapter_list = []
    ebook_content = ""
    summary_so_far = ""

    with st.spinner("Creating Chapters..."):
        response_list = create_chapters(input_title, input_description)
        try:
            response_list = create_chapters(input_title, input_description)
            for field in response_list:
                st.write(field.strip() + ",")
                chapter_list.append(field.strip())
        except Exception as e:
            st.error(f"An error occurred: {e}")

        # hardcoding the chapter number to 1 for now, this will loop through all chapters

        for i, chapter in enumerate(chapter_list):

            ebook_content += f"Chapter {i+1}: {chapter} \n\n"

            with st.spinner(f"Writing Chapter: {i+1}"):
                try:
                    response = write_next_chapter(
                        book_name=input_title,
                        book_description=input_description,
                        chapter_number=i + 1,  #
                        chapter_name=chapter_list[i],
                        summary_so_far=summary_so_far,
                    )
                    st.title(f"CHAPTER {i+1}: {chapter_list[i]}")
                    st.write(response)
                    ebook_content += response + "\n\n"

                    with st.spinner(f"Summarizing Chapter {i+1}..."):
                        try:
                            summary = summarize(response)
                            summary_so_far += f"Chapter {i+1} Summary: {summary} \n\n"
                            st.title(f"CHAPTER {i + 1} Summary")
                            st.write(summary)
                        except Exception as e:
                            st.error(f"An error occurred summarizing with OpenAI: {e}")

                except Exception as e:
                    st.error(f"An error occurred writing chapter with OpenAI: {e}")

        # Specify the file path
        file_name = input_title.strip().replace(" ", "_")
        file_path = f"/home/alkai333/ebook-writer/{file_name}.txt"

        # Write the ebook_content to the text file
        try:
            with open(file_path, "w") as file:
                file.write(ebook_content)
            st.success("Ebook content written to file successfully!")
        except Exception as e:
            st.error(f"An error occurred while writing to file: {e}")
