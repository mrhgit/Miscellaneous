<?php
if (isset($_GET["cmd"])) {
$cmd = $_GET["cmd"];
if ($cmd != ""){
	$room = $_GET["room"];
	echo 'Received command ' . htmlspecialchars($cmd);
	if ($room=="lr") {
		if ($cmd=="off") exec("/home/pi/Desktop/ir/bin/acoff.sh");
		if ($cmd=="ac")  exec("/home/pi/Desktop/ir/bin/ac.sh");
		if ($cmd=="heat")  exec("/home/pi/Desktop/ir/bin/heat.sh");
	}
	else if ($room=="br") {
		if (in_array($cmd, array("heat","ac","off"))){
			exec("/home/pi/Desktop/ir/bin/runbrremote.sh $cmd");
		}
	}
	header("Location: ."); /* Redirect browser */
}
print "<br>";
}
 ?>
 <style>
	 h2 {font-size: 60px}
	 a {font-size:60px}
 </style>
<h2>Living Room</h2>
<a href="?cmd=heat&room=lr">Heat</a><p>
<a href="?cmd=ac&room=lr">A/C</a><p>
<a href="?cmd=off&room=lr">Off</a><p>
	
<h2>Bedroom</h2>
<a href="?cmd=heat&room=br">Heat</a><p>
<a href="?cmd=ac&room=br">A/C</a><p>
<a href="?cmd=off&room=br">Off</a><p>
