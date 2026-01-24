-- Create database
CREATE DATABASE course_portal;
USE course_portal;

-- 1. Categories table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL
);

-- 2. Subcategories table
CREATE TABLE subcategories (
    subcategory_id INT AUTO_INCREMENT PRIMARY KEY,
    subcategory_name VARCHAR(100) NOT NULL,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- 3. Items table (levels, languages, activities)
CREATE TABLE items (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    subcategory_id INT,
    FOREIGN KEY (subcategory_id) REFERENCES subcategories(subcategory_id)
);

-- Categories
INSERT INTO categories (category_name)
VALUES ('COURCE'),('ECA');

-- Subcategories
INSERT INTO subcategories (subcategory_name, category_id)
VALUES
('Basic science project',1),
('Robotics',1),
('Programming Language', 1);

-- Robotics
INSERT INTO items (item_name, subcategory_id)
Values
('Basic',2),
('Medium',2),
('Advance',2);

-- Programming languages
INSERT INTO items (item_name, subcategory_id)
VALUES
('Java', 3),
('Python', 3),
('HTML', 3),
('CSS', 3),
('JavaScript', 3);

