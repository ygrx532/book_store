-- Create the database if it doesn't already exist
CREATE DATABASE IF NOT EXISTS bookstore;
USE bookstore;

-- Create the Book table
CREATE TABLE IF NOT EXISTS Book (
    ISBN VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL,
    Author VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    genre VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (ISBN)
);

-- Create the Customer table
CREATE TABLE IF NOT EXISTS Customer (
    id INT AUTO_INCREMENT,
    userId VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    address VARCHAR(255) NOT NULL,
    address2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state CHAR(2) NOT NULL,
    zipcode VARCHAR(10) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY unique_userId (userId)
);
