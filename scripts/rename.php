<?php

$root = dirname(__DIR__);
$files = glob("$root/data/*/*.geojson");

foreach ($files as $file) {
	$new_file = preg_replace('/(fl|nc|va)_113_to_115_(\d+).(display|lookup)\.geojson$/', '$1_113_to_114_$2.$3.geojson', $file);
	if ($new_file != $file) {
		echo "$file => $new_file\n";
		exec("git mv $file $new_file");
	} else {
		//echo "$file ok\n";
	}
}
