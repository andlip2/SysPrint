-- Tabela print_logs (Recebe os dados do arquivo XLSX)
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
-- Tabela print_limits (Guarda os dados do total de impressões)
CREATE TABLE IF NOT EXISTS print_limits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `User` VARCHAR (100) UNIQUE,
    `Max Prints` INT NOT NULL,
    `Start Date` DATE NOT NULL,
    `End Date` DATE NOT NULL,
    `Last Reset Date` DATE
);
-- Consulta para identificar quantas impressões o usuário fez
SELECT `User`,
    COUNT(*) AS `Total Prints`
FROM print_logs
GROUP BY `User`;