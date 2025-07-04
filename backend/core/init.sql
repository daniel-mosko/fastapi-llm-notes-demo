-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "vector"; -- For pgvector embeddings support

-- Notes table
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    hash TEXT NOT NULL
);


-- Note content embeddings (chunked for long notes)
CREATE TABLE notes_content_embeddings (
    id SERIAL PRIMARY KEY,
    note_id SERIAL NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL, -- Order of chunks within the content
    embedding VECTOR(384), -- Embedding for this chunk
    chunk_start_position INTEGER, -- Character position where chunk starts in original content
    chunk_end_position INTEGER, -- Character position where chunk ends in original content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(note_id, chunk_index)
);
