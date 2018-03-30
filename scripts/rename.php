<?php

$root = dirname(__DIR__);
$files = glob("$root/data/*/*.geojson");

foreach ($files as $file) {
	$new_file = preg_replace('/(\d+)\.geojson$/', '$1.lookup.geojson', $file);
	if ($new_file != $file) {
		echo "$file => $new_file\n";
		exec("git mv $file $new_file");
	} else {
		//echo "$file ok\n";
	}
}
