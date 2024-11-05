<?php
// pagr_drm.php

header('Content-Type: application/json');

// Database credentials
$servername = "localhost";
$username = "eO3EPtUBC0j896YExiVp"; // Replace with your DB username
$password = "uON2dlBF9sHWrnap4OjH@"; // Replace with your DB password
$dbname = "pagr_drm";

// Get the POST data
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!isset($data['drm_key']) || !isset($data['hardware_id'])) {
    http_response_code(400);
    echo json_encode(["error" => "Invalid request"]);
    exit();
}

$drm_key = $data['drm_key'];
$hardware_id = $data['hardware_id'];

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    http_response_code(500);
    echo json_encode(["error" => "Database connection failed"]);
    exit();
}

// Validate drm_key
$stmt = $conn->prepare("SELECT max_devices FROM drm_keys WHERE drm_key = ?");
$stmt->bind_param("s", $drm_key);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows == 0) {
    // Invalid DRM key
    http_response_code(403);
    echo json_encode(["error" => "Invalid DRM key"]);
    $stmt->close();
    $conn->close();
    exit();
}

$row = $result->fetch_assoc();
$max_devices = $row['max_devices'];
$stmt->close();

// Check if hardware_id is already registered
$stmt = $conn->prepare("SELECT * FROM registrations WHERE drm_key = ? AND hardware_id = ?");
$stmt->bind_param("ss", $drm_key, $hardware_id);
$stmt->execute();
$result = $stmt->get_result();

if ($result->num_rows > 0) {
    // Already registered
    echo json_encode(["message" => "Already registered", "status" => "approved"]);
    $stmt->close();
    $conn->close();
    exit();
}
$stmt->close();

// Check if the maximum number of devices has been reached
$stmt = $conn->prepare("SELECT COUNT(*) as device_count FROM registrations WHERE drm_key = ?");
$stmt->bind_param("s", $drm_key);
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();
$device_count = $row['device_count'];
$stmt->close();

if ($device_count >= $max_devices) {
    // Too many devices registered
    echo json_encode(["error" => "Too many devices registered", "status" => "denied"]);
    $conn->close();
    exit();
}

// Register the new hardware_id
$stmt = $conn->prepare("INSERT INTO registrations (drm_key, hardware_id) VALUES (?, ?)");
$stmt->bind_param("ss", $drm_key, $hardware_id);

if ($stmt->execute()) {
    // Registration successful
    echo json_encode(["message" => "Registration complete", "status" => "approved"]);
} else {
    // Registration failed
    echo json_encode(["error" => "Registration failed", "status" => "denied"]);
}
$stmt->close();
$conn->close();
exit();
?>
