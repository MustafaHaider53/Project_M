-- Migration to add email field to students table
ALTER TABLE students ADD COLUMN IF NOT EXISTS email VARCHAR(255);
