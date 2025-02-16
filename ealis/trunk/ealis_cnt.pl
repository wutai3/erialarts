# ealis ver.3.0   counter plugin
# ---  erialarts : https://github.com/wutai3/erialarts/

package count;

my($count);
$count = (-s "$ini::logdir/ealis_cnto.db")  if(-e "$ini::logdir/ealis_cnto.db");

$count++;

if( $count >= 1000 ){
	open(CNT,">$ini::logdir/ealis_cnto.db")  || return "cnt ($ini::logdir/ealis_cnto.db) err";
	close (CNT);
	open(CNTK,">>$ini::logdir/ealis_cntk.db") || return "cnt ($ini::logdir/ealis_cntk.db) err";
	print CNTK ' ';
	close (CNTK);
	$count = 0;
}else{
	open(CNT,">>$ini::logdir/ealis_cnto.db") || return "cnt ($ini::logdir/ealis_cnto.db) err";
	print CNT ' ';
	close(CNT);
}

if(-e "$ini::logdir/ealis_cntk.db"){ $count += (-s "$ini::logdir/ealis_cntk.db") * 1000;}

return $count;
