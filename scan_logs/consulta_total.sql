SELECT
    (SELECT SUM(Pages * Copies) FROM logs) +
    (SELECT SUM(IFNULL(bw_copies, 0) + IFNULL(colorful_copies, 0)) FROM logs_scans) AS total_geral;