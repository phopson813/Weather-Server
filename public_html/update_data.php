<?php

$allowed_ip = 'IP_ADDRESS';

if ($_SERVER['REMOTE_ADDR'] !== $allowed_ip) {
        http_response_code(403);
        echo json_encode(['status' => 'error', 'message' => 'Access denied']);
        exit;
}

header('Content-Type: application/json');

$input = file_get_contents('php://input');


$data = json_decode($input, true);

$required = ['Station', 'TempF', 'Humidity', 'Time'];

foreach ($required as $field) {
        if (!isset($data[$field])) {
                echo json_encode([
                        "status" => "error",
                        "message" => "Missing field: $field"
                ]);
                exit;
        }
}

$log_file = __DIR__ . '/../logs/sensor_log_fixed.txt';

file_put_contents($log_file, json_encode($data) . PHP_EOL, FILE_APPEND | LOCK_EX);

echo json_encode([
        "status" => "success"
]);

?>
