<?php
// Set headers to allow cross-origin requests
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json");

// Get the JSON data from the request
$json_data = file_get_contents('php://input');
$data = json_decode($json_data, true);

// Initialize response
$response = array(
    'success' => false,
    'message' => '',
    'email_sent' => false,
    'sms_sent' => false
);

// Validate request
if (!$data) {
    $response['message'] = 'Invalid request data';
    echo json_encode($response);
    exit;
}

// Check notification type
$type = isset($data['type']) ? $data['type'] : '';

if ($type === 'email') {
    // Send email notification
    $to = isset($data['email']) ? $data['email'] : '';
    $subject = isset($data['subject']) ? $data['subject'] : 'USB Security Alert';
    $message = isset($data['message']) ? $data['message'] : '';
    
    if (empty($to)) {
        $response['message'] = 'Email address is required';
        echo json_encode($response);
        exit;
    }
    
    // Set email headers
    $headers = "MIME-Version: 1.0" . "\r\n";
    $headers .= "Content-type:text/html;charset=UTF-8" . "\r\n";
    $headers .= "From: USB Security Monitor <noreply@usbsecuritymonitor.com>" . "\r\n";
    
    // Format HTML message
    $html_message = "
    <html>
    <head>
        <title>$subject</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .header { background-color: #0f172a; color: white; padding: 10px 20px; border-radius: 5px 5px 0 0; }
            .content { padding: 20px; }
            .footer { font-size: 12px; color: #666; margin-top: 20px; border-top: 1px solid #ddd; padding-top: 10px; }
            .alert-critical { color: #ef4444; font-weight: bold; }
            .alert-warning { color: #f59e0b; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class='container'>
            <div class='header'>
                <h2>USB Security Alert</h2>
            </div>
            <div class='content'>
                <p>$message</p>
                <p>This is an automated notification from your USB Security Monitoring System.</p>
            </div>
            <div class='footer'>
                <p>USB Security Monitor - Protecting your system from USB threats</p>
                <p>Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    ";
    
    // Send email
    $email_sent = mail($to, $subject, $html_message, $headers);
    
    if ($email_sent) {
        $response['success'] = true;
        $response['email_sent'] = true;
        $response['message'] = 'Email notification sent successfully';
    } else {
        $response['message'] = 'Failed to send email notification';
    }
} elseif ($type === 'sms') {
    // For SMS, we would typically use a service like Twilio
    // This is a placeholder for SMS sending logic
    // In a real implementation, you would use a service like Twilio's API
    
    $phone = isset($data['phone']) ? $data['phone'] : '';
    $message = isset($data['message']) ? $data['message'] : '';
    
    if (empty($phone)) {
        $response['message'] = 'Phone number is required';
        echo json_encode($response);
        exit;
    }
    
    // Log the SMS request (since we can't actually send SMS in this demo)
    $log_file = 'sms_log.txt';
    $log_message = date('Y-m-d H:i:s') . " - To: $phone - Message: $message\n";
    file_put_contents($log_file, $log_message, FILE_APPEND);
    
    // Simulate successful SMS sending
    $response['success'] = true;
    $response['sms_sent'] = true;
    $response['message'] = 'SMS notification logged (would be sent in production)';
    
    /* 
    // Twilio implementation would look something like this:
    require_once 'vendor/autoload.php'; // Twilio PHP SDK
    
    $account_sid = 'YOUR_TWILIO_ACCOUNT_SID';
    $auth_token = 'YOUR_TWILIO_AUTH_TOKEN';
    $twilio_number = 'YOUR_TWILIO_PHONE_NUMBER';
    
    $client = new Twilio\Rest\Client($account_sid, $auth_token);
    
    try {
        $message = $client->messages->create(
            $phone,
            [
                'from' => $twilio_number,
                'body' => $message
            ]
        );
        
        $response['success'] = true;
        $response['sms_sent'] = true;
        $response['message'] = 'SMS notification sent successfully';
    } catch (Exception $e) {
        $response['message'] = 'Failed to send SMS notification: ' . $e->getMessage();
    }
    */
} else {
    $response['message'] = 'Invalid notification type';
}

// Return JSON response
echo json_encode($response);
?>
