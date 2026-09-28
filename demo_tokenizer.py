"""Quick demo of the tokenizer functionality."""

from app.core.tokenizer import count_tokens, count_tokens_for_model

# Example 1: Simple text
text1 = "Hello, world!"
print(f'Text: "{text1}"')
print(f'Tokens: {count_tokens(text1)}\n')

# Example 2: Longer prompt
text2 = "Please write a detailed SQL query to select all users from the database."
print(f'Text: "{text2}"')
print(f'Tokens: {count_tokens(text2)}\n')

# Example 3: Code snippet
text3 = "def hello():\n    return 'Hello, world!'"
print(f'Code:\n{text3}')
print(f'Tokens: {count_tokens(text3)}\n')

# Example 4: Very verbose prompt
text4 = """
Please, if you would be so kind, could you possibly write a very detailed and 
comprehensive SQL query that will select all of the users from our database, 
making sure to include absolutely all of their information?
"""
print(f'Verbose prompt: "{text4.strip()}"')
print(f'Tokens: {count_tokens(text4)}')
