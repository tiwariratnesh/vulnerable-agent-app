CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255),
    email VARCHAR(255),
    role VARCHAR(50),
    preferences JSONB,
    api_key VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    status VARCHAR(50),
    prompt TEXT,
    result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS agents_log (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(255),
    action VARCHAR(255),
    payload JSONB,
    result JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sensitive_data (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    data_type VARCHAR(100),
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (user_id, username, email, role, preferences, api_key) VALUES
('user-001', 'admin', 'admin@example.com', 'admin', '{"theme": "dark"}', 'sk-admin-key-12345'),
('user-002', 'alice', 'alice@example.com', 'user', '{"theme": "light"}', 'sk-alice-key-67890'),
('user-003', 'bob', 'bob@example.com', 'user', '{"theme": "dark"}', 'sk-bob-key-11111');

INSERT INTO sensitive_data (user_id, data_type, data) VALUES
('user-001', 'credit_card', '4532-1234-5678-9010'),
('user-002', 'ssn', '123-45-6789'),
('user-003', 'password', 'MySecretPassword123!');


