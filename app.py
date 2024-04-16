import os
from dataclasses import dataclass
import datetime

import streamlit as st
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection setup
con = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = con.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    prompt TEXT NOT NULL,
    genre TEXT NOT NULL,
    is_favorite BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
con.commit()

@dataclass
class Prompt:
    id: int = None
    title: str
    prompt: str
    genre: str
    is_favorite: bool = False
    created_at: datetime.datetime = None
    updated_at: datetime.datetime = None

def prompt_form(prompt=None):
    """
    Form for creating and updating prompts.
    """
    with st.form(key="prompt_form"):
        title = st.text_input("Title", value=prompt.title if prompt else "")
        prompt_text = st.text_area("Prompt", height=200, value=prompt.prompt if prompt else "")
        genre = st.text_input("Genre", value=prompt.genre if prompt else "")
        is_favorite = st.checkbox("Favorite", value=prompt.is_favorite if prompt else False)
        submitted = st.form_submit_button("Submit")
        if submitted:
            return Prompt(prompt.id if prompt else None, title, prompt_text, genre, is_favorite)

def add_or_update_prompt(prompt):
    """
    Insert or update a prompt in the database.
    """
    if prompt.id is None:  # Assuming a new prompt if no id is provided
        cur.execute(
            "INSERT INTO prompts (title, prompt, genre, is_favorite) VALUES (%s, %s, %s, %s) RETURNING id",
            (prompt.title, prompt.prompt, prompt.genre, prompt.is_favorite)
        )
        prompt_id = cur.fetchone()[0]
        st.success("Prompt added successfully!")
    else:  # Update existing prompt
        cur.execute(
            "UPDATE prompts SET title=%s, prompt=%s, genre=%s, is_favorite=%s, updated_at=CURRENT_TIMESTAMP WHERE id=%s",
            (prompt.title, prompt.prompt, prompt.genre, prompt.is_favorite, prompt.id)
        )
        st.success("Prompt updated successfully!")
    con.commit()
    return prompt.id

def delete_prompt(prompt_id):
    """
    Delete a prompt from the database.
    """
    cur.execute("DELETE FROM prompts WHERE id = %s", (prompt_id,))
    con.commit()
    st.success("Prompt deleted successfully!")

def display_prompts(search_query=None, sort_by='created_at'):
    """
    Display prompts with options to edit or delete, filtered by search and sorted.
    """
    query = "SELECT id, title, prompt, genre, is_favorite, created_at, updated_at FROM prompts"
    conditions = []
    if search_query:
        conditions.append(f"(title ILIKE '%{search_query}%' OR prompt ILIKE '%{search_query}%')")
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += f" ORDER BY {sort_by} DESC"
    
    cur.execute(query)
    prompts = cur.fetchall()
    
    for p in prompts:
        with st.expander(f"{p[1]} - {p[3]} ({'Favorite' if p[4] else 'Not Favorite'})"):
            st.text(f"Prompt: {p[2]}")
            if st.button("Edit", key=f"edit_{p[0]}"):
                edit_prompt = Prompt(p[0], p[1], p[2], p[3], p[4], p[5], p[6])
                edited_prompt = prompt_form(edit_prompt)
                if edited_prompt:
                    add_or_update_prompt(edited_prompt)
            if st.button("Delete", key=f"del_{p[0]}"):
                delete_prompt(p[0])

# UI for the app
st.title("Promptbase")
st.subheader("A simple app to store and retrieve writing prompts")

# Search and sort functionality
search_query = st.text_input("Search prompts")
sort_by = st.selectbox("Sort by", options=["created_at", "title", "is_favorite"])

# Adding a prompt
new_prompt = prompt_form()
if new_prompt:
    add_or_update_prompt(new_prompt)

# Displaying prompts
display_prompts(search_query, sort_by)
