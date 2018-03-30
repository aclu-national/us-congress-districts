<?php

$in = fopen('test_coords.csv', 'r');
$out = fopen('test_urls.txt', 'w');

$headers = fgetcsv($in);

while ($row = fgetcsv($in)) {
	list($lng, $lat) = $row;
	fwrite($out, "http://localhost:5000/pip?lat=$lat&lng=$lng\n");
}

fclose($in);
fclose($out);
