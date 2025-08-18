from app.schemas.notes import BaseNoteSchema, NoteResponseSchema


def summarize_prompt(note: BaseNoteSchema) -> str:
    return f"Summarize the following note, respond in plain text. Title = {note.title}, Content = {note.content} "


def ask_from_similar_notes_prompt(
    query: str, notes: list[NoteResponseSchema]
) -> str:
    return f"Answer question based only on following notes, if it isn't relevant, write that nothing was found. Respond in plain text:\n QUESTION: {query},\n NOTES: {notes}"
