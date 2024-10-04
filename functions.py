import ollama

MODEL = "tinyllama"  # Using TinyLlama model


def make_ollama_call(system_prompt: str, user_prompt: str) -> str:
    """Generic function to make Ollama calls"""
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = ollama.chat(model=MODEL, messages=messages)
        return response["message"]["content"]
    except Exception as e:
        print(f"Error fetching the response from Ollama: {e}")
        raise e


def create_chapters(number: int, title: str, description: str) -> list:
    """Create a list of chapter names for the book"""
    system_prompt = f"""Create a list of {number} chapters for an ebook, include introductory 
    and concluding chapters and create interesting names for the introduction and 
    conclusion chapter. Respond only with the chapter names separated by commas.
    Don't include the number or the word 'chapter'."""

    user_prompt = (
        f"Book Title: {title}, Book Description: {description or 'not supplied'}"
    )

    for _ in range(5):  # Try up to 5 times
        response = make_ollama_call(system_prompt, user_prompt).replace("\n", " ")
        chapters = response.split(",")
        chapters = [chapter.strip() for chapter in chapters]  # Clean up whitespace
        if len(chapters) == number:
            return chapters

    return response.split(",")


def write_next_chapter(
    book_name: str,
    book_description: str,
    chapter_number: int,
    chapter_name: str,
    summary_so_far: str,
    number_of_words: int = 350,
) -> str:
    """Write the next chapter of the book"""
    if chapter_number == 1:
        system_prompt = f"""You are writing the first chapter of an ebook. Make this first chapter interesting to 
        encourage the user to read on. Write approximately {number_of_words} words.
        BOOK NAME: {book_name}
        BOOK DESCRIPTION: {book_description or 'not supplied'}"""
    else:
        system_prompt = f"""You are writing a chapter of an ebook. Write approximately {number_of_words} words.
        Use the previous chapter summaries provided to keep a consistent narrative, make this
        chapter follow on naturally from the previous chapter.
        Don't mention the present or previous chapters by name.
        BOOK NAME: {book_name}
        BOOK DESCRIPTION: {book_description or 'not supplied'}
        SUMMARY SO FAR: {summary_so_far or 'not supplied'}"""

    user_prompt = f"""CHAPTER NUMBER: {chapter_number}
        CHAPTER NAME: {chapter_name}"""

    return make_ollama_call(system_prompt, user_prompt)


def summarize(input_text: str, number_of_words: int) -> str:
    """Create a summary of the provided text"""
    system_prompt = (
        f"You are writing a {number_of_words} word summary of an ebook chapter."
    )
    user_prompt = f"Book Chapter: {input_text}"

    return make_ollama_call(system_prompt, user_prompt)
