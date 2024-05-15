import streamlit as st
from dotenv import load_dotenv
import pdfkit
from functions import create_chapters, write_next_chapter, summarize


load_dotenv()


st.title("Create An Ebook")
input_title = st.text_input(
    "Book Title", value="The History Of Cambodia Through The Eyes Of Cats"
)
input_description = st.text_input("Book Description")
input_words = st.number_input("Words Per Chapter", value=350, step=1)
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

            ebook_content += f"<h1>Chapter {i+1}: {chapter}</h2> \n\n"

            try:
                with st.spinner(f"Writing Chapter {i+1}..."):
                    response = write_next_chapter(
                        book_name=input_title,
                        book_description=input_description,
                        chapter_number=i + 1,  #
                        chapter_name=chapter_list[i],
                        summary_so_far=summary_so_far,
                        number_of_words=input_words,
                    )
                    st.title(f"CHAPTER {i+1}: {chapter_list[i]}")
                    st.write(response)
                    ebook_content += response.replace("\n", "</p><p>")
                    ebook_content = "<p>" + ebook_content + "</p><br/><br/><br/>"

                with st.spinner(f"Summarizing Chapter {i+1}..."):
                    try:
                        summary_length = input_words / 7
                        summary = summarize(
                            input=response, number_of_words=summary_length
                        )
                        summary_so_far += f"Chapter {i+1} Summary: {summary} \n\n"
                        st.title(f"CHAPTER {i + 1} Summary")
                        st.write(summary)
                    except Exception as e:
                        st.error(f"An error occurred summarizing with OpenAI: {e}")

            except Exception as e:
                st.error(f"An error occurred writing chapter with OpenAI: {e}")

        # Specify the file path
        file_name = input_title.strip().replace(" ", "_")
        file_path = f"/home/alkai333/ebook-writer/ebooks/{file_name}.pdf"

        try:
            pdfkit.from_string(ebook_content, file_path)
            st.success("Ebook content written to file successfully!")
            st.download_button("Download Ebook", file_path)
        except Exception as e:
            st.error(f"An error occurred while creating the PDF: {e}")
