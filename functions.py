from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.output_parsers import StrOutputParser


model = "gpt-4-turbo"  # have it here so we can change for debugging


def create_chapters(title: str, description: str) -> list:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Create a list of 7 chapters for an ebook, include introductory 
            and concluding chapters and create interesting names for the introduction and 
            conculsion chapter. Respond only with the chapter names seperated by commas.
            Don't include the number or the word 'chapter'.
            The book has a title and optional description
            Output Format: Chapter 1 Name, Chapter 2 Name, ...""",
            ),
            ("user", "Book Title: {title}, Book Description: {description}"),
        ]
    )

    llm = ChatOpenAI(model=model)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    try:
        response = chain.invoke(
            {"title": title, "description": description or "not supplied"}
        )
    except Exception as e:
        print(f"Error fetching the response: {e}")
        raise e

    response = response.replace("\n", " ")
    return response.split(",")


def write_next_chapter(
    book_name: str,
    book_description: str,
    chapter_number: int,
    chapter_name: str,
    summary_so_far: str,
    number_of_words: int = 350,
) -> str:
    """Writes the next chapter continuing from summary so far"""

    if chapter_number == 1:
        system_prompt = """You are writing the first chapter of an ebook. Make this first chapter interesting to 
        encourage the user to read on. {number_of_words} words\n
                    BOOK NAME: {book_name} \n
                    BOOK DESCRIPTION: {book_description} \n
                    {summary_so_far},
        """
    else:
        system_prompt = """You are writing a chapter of an ebook. {number_of_words} words. \n
                  Use the previous chapter summaries provided to keep a consistant narrative, and start 
                  each chapter with a transition from the previous chapter.
                  Don't mention the present or previous chapters by name \n\n
                    BOOK NAME: {book_name} \n
                    BOOK DESCRIPTION: {book_description} \n
                    SUMMARY SO FAR: {summary_so_far} """

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt,
            ),
            (
                "user",
                """ CHAPTER NUMBER: {chapter_number} \n
                    CHAPTER_NAME: {chapter_name}""",
            ),
        ]
    )

    llm = ChatOpenAI(model=model)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    try:
        response = chain.invoke(
            {
                "book_name": book_name,
                "book_description": book_description or "not supplied",
                "summary_so_far": summary_so_far or "not supplied",
                "chapter_number": chapter_number,
                "chapter_name": chapter_name,
                "number_of_words": number_of_words,
            }
        )
    except Exception as e:
        print(f"Error fetching the response: {e}")
        raise e

    return response


def summarize(input: str, number_of_words: int) -> str:
    """Summarizes the chapter, including list of key themes and ideas"""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are writing a {number_of_words} word summary of an ebook chapter:",
            ),
            ("user", "Book Chapter: {input}"),
        ]
    )

    llm = ChatOpenAI(model=model)
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser

    try:
        response = chain.invoke(
            {"input": input, "number_of_words": str(number_of_words)}
        )

        return response

    except Exception as e:
        print(f"Error fetching the response: {e}")
        raise e


# System prompt: "You are a writing chapter for an ebook called {title}".
# If previous chapters are provided, make sure to include the key themes, and start with a transition from the
# previous chapter.

# User prompt: Chapter Number:{number} Chapter Name: {chapter name}
# Summary of Book So Far: {summary}


# later make uncensored version