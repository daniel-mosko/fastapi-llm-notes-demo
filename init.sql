-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector"; -- For pgvector embeddings support

-- Notes table
CREATE TABLE notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- Note content embeddings (chunked for long notes)
CREATE TABLE notes_content_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL, -- Order of chunks within the content
    embedding VECTOR(384), -- Embedding for this chunk
    chunk_start_position INTEGER, -- Character position where chunk starts in original content
    chunk_end_position INTEGER, -- Character position where chunk ends in original content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(note_id, chunk_index)
);

-- Word links - OPTIONAL: user-defined relationships between text spans across notes
CREATE TABLE word_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    source_text VARCHAR(255) NOT NULL, -- The actual text being linked from
    source_position_start INTEGER NOT NULL, -- Character position where linked text starts
    source_position_end INTEGER NOT NULL, -- Character position where linked text ends
    target_note_id UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    target_text VARCHAR(255) NOT NULL, -- The actual text being linked to
    target_position_start INTEGER NOT NULL, -- Character position where target text starts
    target_position_end INTEGER NOT NULL, -- Character position where target text ends
    link_type VARCHAR(50) NOT NULL DEFAULT 'reference', -- 'reference', 'synonym', 'related', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent self-links
    CHECK (source_note_id != target_note_id OR source_position_start != target_position_start)
);

