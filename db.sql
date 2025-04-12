CREATE DATABASE IF NOT EXISTS essay_app;
USE essay_app;

-- USERS TABLE: Admins and Users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RUBRICS: Created by Admin using LLM
CREATE TABLE rubrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(255) NOT NULL,
    requirements TEXT, -- optional admin input
    difficulty_level VARCHAR(50),
    structure JSON, -- generated + edited
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- ESSAYS SUBMITTED BY USERS
CREATE TABLE submissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    rubric_id INT NOT NULL,
    content TEXT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (rubric_id) REFERENCES rubrics(id)
);

-- FEEDBACK GENERATED FOR USER ESSAY
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    submission_id INT NOT NULL,
    content_score FLOAT,
    grammar_score FLOAT,
    structure_score FLOAT,
    conclusion_score FLOAT,
    final_score FLOAT,
    feedback_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (submission_id) REFERENCES submissions(id)
);
