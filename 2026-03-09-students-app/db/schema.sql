-- Students App - Database Schema
-- Safe to run multiple times (uses IF NOT EXISTS)

CREATE DATABASE IF NOT EXISTS students_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE students_db;

CREATE TABLE IF NOT EXISTS students (
    id   INT          AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age  INT          NOT NULL
);
