<?php
$name = $_POST['name'];
$email = $_POST['email'];
$rating = $_POST['rating'];
$review = $_POST['review'];

$review_data = "$name,$email,$rating,$review\n";
$file_path = "review.txt";

// Open the file in append mode
$file_handle = fopen($file_path, "a");

// Write the review data to the file
fwrite($file_handle, $review_data);

// Close the file handle
fclose($file_handle);
?>
