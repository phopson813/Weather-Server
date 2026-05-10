<?php
header('Content-Type: application/json');

try {
    $db = new PDO('newdb.db');
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    $range = isset($_GET['range']) ? $_GET['range'] : "day";
    $dateParam = isset($_GET['date']) ? $_GET['date'] : null;

    $times = [];
    $temps = [];

    if ($range === "day") {

        // Calendar Search
        if ($dateParam) {
            $stmt = $db->prepare("
                SELECT strftime('%H',created_at) AS hour, AVG(tempF) AS tempF
                FROM readings
                WHERE date(created_at) = :selectedDate
                GROUP BY hour
                ORDER BY hour
            ");
            $stmt->execute([':selectedDate' => $dateParam]);
        } else {
        // Hourly average for today
            $stmt = $db->prepare("
                SELECT strftime('%H',created_at) AS hour, AVG(tempF) AS tempF
                FROM readings
                WHERE date(created_at) = date('now', 'localtime')
                GROUP BY hour
                ORDER BY hour
            ");
            $stmt->execute();
        }

        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        // Fill 24 hours
        for ($h = 0; $h < 24; $h++) {
            $label = sprintf('%02d:00', $h);
            $found = false;
            foreach ($rows as $row) {
                if (intval($row['hour']) === $h) {
                    $temps[] = round($row['tempF'],2);
                    $found = true;
                    break;
                }
            }
            if (!$found) $temps[] = null;
            $times[] = $label;
        }

    } elseif ($range === "month") {
        // Daily average for current month
        $stmt = $db->prepare("
            SELECT strftime('%d', created_at) AS day, AVG(tempF) AS tempF
            FROM readings
            WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m','now')
            GROUP BY day
            ORDER BY day
        ");
        $stmt->execute();
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

        foreach ($rows as $row) {
            $times[] = $row['day'];
            $temps[] = round($row['tempF'],2);
        }

    } else {
        echo json_encode(['error'=>"Invalid range"]);
        exit;
    }

    echo json_encode([
        "times" => $times,
        "temps" => $temps
    ]);
} catch (Exception $e) {
    echo json_encode(['error'=>$e->getMessage()]);
}
?>
