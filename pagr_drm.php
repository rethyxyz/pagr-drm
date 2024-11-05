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

// Escape input data to prevent SQL injection
$drm_key_esc = $conn->real_escape_string($drm_key);
$hardware_id_esc = $conn->real_escape_string($hardware_id);

// Validate drm_key
$sql = "SELECT max_devices FROM drm_keys WHERE drm_key = '$drm_key_esc'";
$result = $conn->query($sql);

if ($result->num_rows == 0) {
    // Invalid DRM key
    http_response_code(403);
    echo json_encode(["error" => "Invalid DRM key"]);
    exit();
}

$row = $result->fetch_assoc();
$max_devices = $row['max_devices'];

// Check if hardware_id is already registered
$sql = "SELECT * FROM registrations WHERE drm_key = '$drm_key_esc' AND hardware_id = '$hardware_id_esc'";
$result = $conn->query($sql);

if ($result->num_rows > 0) {
    // Already registered
    echo json_encode(["message" => "Already registered", "status" => "approved"]);
    exit();
}

// Check if the maximum number of devices has been reached
$sql = "SELECT COUNT(*) as device_count FROM registrations WHERE drm_key = '$drm_key_esc'";
$result = $conn->query($sql);
$row = $result->fetch_assoc();
$device_count = $row['device_count'];

if ($device_count >= $max_devices) {
    // Too many devices registered
    echo json_encode(["error" => "Too many devices registered", "status" => "denied"]);
    exit();
}

// Register the new hardware_id
$sql = "INSERT INTO registrations (drm_key, hardware_id) VALUES ('$drm_key_esc', '$hardware_id_esc')";

if ($conn->query($sql) === TRUE) {
    // Registration successful
    echo json_encode(["message" => "Registration complete", "status" => "approved"]);
    exit();
} else {
    // Registration failed
    echo json_encode(["error" => "Registration failed", "status" => "denied"]);
    exit();
}

$conn->close();
?>
