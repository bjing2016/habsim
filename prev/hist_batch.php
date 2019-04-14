<?php


$TIME = time();


$COMMAND = "python historical_batch.py gfshist/ ";
$COMMAND = $COMMAND . $_GET['y'] . " ";
$COMMAND = $COMMAND . $_GET['mo'] . " ";
$COMMAND = $COMMAND . $_GET['d'] . " ";
$COMMAND = $COMMAND . $_GET['h'] . " ";
$COMMAND = $COMMAND . $_GET['mi'] . " ";
$COMMAND = $COMMAND . $_GET['tn'] . " ";
$COMMAND = $COMMAND . $_GET['ti'] . " ";
$COMMAND = $COMMAND . $_GET['lat'] . " ";
$COMMAND = $COMMAND . $_GET['lon'] . " ";
$COMMAND = $COMMAND . $_GET['asc'] . " ";
$COMMAND = $COMMAND . $_GET['an'] . " ";
$COMMAND = $COMMAND . $_GET['var'] . " ";
$COMMAND = $COMMAND . $_GET['step'] . " ";
$COMMAND = $COMMAND . $_GET['alt'] . " ";
$COMMAND = $COMMAND . $_GET['desc'] . " ";
$COMMAND = $COMMAND . $_GET['max_h'] . " ";
$COMMAND = $COMMAND . " > res/" . $TIME;

exec($COMMAND);

header('Location: '."https://web.stanford.edu/~bjing/cgi-bin/res/" . $TIME);

?>


