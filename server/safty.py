
# core/safety.py
unsafe = False
UNSAFE_KEYWORDS = [
    # Violence / harm
    "kill", "suicide", "murder", "harm myself", "end my life",
    # Illegal activities
    "bomb", "hack bank", "drugs", "terrorist", "weapon",
    # Hate / offensive
    "hate speech", "racist", "sexist", "offensive slur"
]
def is_unsafe(): return unsafe
def refusal(): return 'I cannot answer that.'
def check_safety(user_input: str) -> str | None:
    """
    Checks if the user input contains unsafe intent.
    Returns a polite refusal string if unsafe, else None.
    """
    text = user_input.lower()
    unsafe = False
    for word in UNSAFE_KEYWORDS:
        if word in text:
            unsafe = True
            return (
                "I'm sorry, but I can’t help with that request. "
                "If you’re feeling unsafe, please reach out to a trusted person or professional."
            )

    return None
