CREATE TABLE IF NOT EXISTS print_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `Time` DATETIME,
    `User` VARCHAR(100),
    `Pages` VARCHAR (50),
    `Copies` VARCHAR(50),
    `Printer` VARCHAR(255),
    `Document Name` VARCHAR(255),
    `Client` VARCHAR(100),
    `Paper Size` VARCHAR(50),
    `Language` VARCHAR(50),
    `Duplex` BOOLEAN,
    `Grayscale` BOOLEAN,
    `Size` VARCHAR(50)
);