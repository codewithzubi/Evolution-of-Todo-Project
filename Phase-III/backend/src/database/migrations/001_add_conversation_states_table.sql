-- Migration: Add conversation_states table for FSM state management

CREATE TABLE IF NOT EXISTS conversation_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    intent_mode VARCHAR(50) NOT NULL DEFAULT 'IDLE',
    intent_step VARCHAR(50),
    intent_payload JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversation_states_conversation_user 
ON conversation_states(conversation_id, user_id);

CREATE INDEX idx_conversation_states_intent_mode 
ON conversation_states(intent_mode);
