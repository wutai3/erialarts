#!/usr/local/bin/perl

# ealis ver.3.0   compactHTML plugin
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC 入)

use 5.004;
require 'jcode.pl';
require './ealis_cfg.cgi';

package main;
	use vars qw[%FORM %COOKIE];

	&form_decode;

	my($logobj) = new LogReader;
	my($htmdata) = new HtmlOut;

	if(defined($FORM{thr})){
		$htmdata->header('thr.');
		$htmdata->{q} .= &ThreadMode::main($logobj);
		$htmdata->{q} .= &LogPager($logobj,'thr');
	}elsif($FORM{pick}){
		$htmdata->header("#$FORM{pick}");
		$htmdata->{q} .= &PrintArticle::main($logobj,$FORM{pick});

	}elsif(defined($FORM{lap})){
		$htmdata->header('lap.');
		my($lapse) = new LapseMode $logobj;
		$htmdata->{q} .= $lapse->show($logobj);
		$htmdata->{q} .= &LogPager($logobj,'lap');

	}elsif(defined($FORM{new})){
		$htmdata->header("New");
		$htmdata->{q} .= &PostForms::oya;
	}elsif($FORM{res}){
		$htmdata->header("Res");
		$htmdata->{q} .= &PostForms::res($FORM{res});

	}else{
		$htmdata->header(undef);
		$htmdata->{q} .= &print_top($logobj);
	}

	$htmdata->{q} .= &print_navi if($ENV{QUERY_STRING});

	$htmdata->out();

exit;


sub print_top
{
	return
	"<h1>$ini::h1</h1>"
	. '<p>' . shift()->{lastwrite} .'</p>'
	. '<ul>'
	. qq!<li><a href="$ini::plug_chtm?thr" accesskey=7>Thread</a>!
	. qq!<li><a href="$ini::plug_chtm?lap" accesskey=8>Lapse</a>!
	. qq!<li><a href="$ini::plug_chtm?new" accesskey=9>新規投稿</a>!
	. '</ul>';
}
sub print_navi
{
	return qq!<hr><a href="?" accesskey=0>Top</a>!;
	
#	return qq!<hr><center><a href="$ini::plug_chtm?thr" accesskey=7>Thr</a>,<a href="$ini::plug_chtm?lap" accesskey=8>Lap</a>,<a href="$ini::plug_chtm?new" accesskey=9>New</a> - <a href="$ini::plug_chtm?" accesskey=0>Top</a></center>!;
}

sub LogPager
{
	my($logobj,$arg) = @_;

	my $current_tab = int( $main::FORM{st} / $main::FORM{show} ) + 1;
	my $tab = (($current_tab >= 4) ? ($current_tab - 2) : 1);		# 開始タブNo.

	my($tmp,$gopage);
	for(1 .. 5){
		if($tab == $current_tab){
			$tmp .= "$tab ";
		}else{
			$gopage = $main::FORM{show} * ( $tab - 1 );		# 何頁目の記事かを生成
			($gopage < $logobj->{oya_num}) || last;			# 含有する親記事数より多い頁
			$tmp .= sprintf '<a href="%s?%s;st=%d;show=%d">%d</a> ',
							$ini::plug_chtm, $arg,$gopage,$main::FORM{show},$tab;
		}
		$tab++;
	}

	return "<br>$tmp";
}

## 
sub form_decode
{
	# Deny IP Check
	foreach(@ini::deniedaddrs){
		if(index($ENV{REMOTE_ADDR}, $_ ) == 0 && length($_) > 4 ){
			print "Status: 204";
			exit;
		}
	}

	# form decode
	my($name, $value);
	foreach ( split(/[&;]/,$ENV{QUERY_STRING}) ) {
		($name, $value) = split(/=/, $_,2);
		$value =~ tr/+/ /;
		$FORM{$name} = $value || '';
	}

	# set default
	$FORM{show}  ||= 4;
	$FORM{st} ||= 0;
}


sub error
{
	&out_buffer( sprintf '<html><body><h1>エラー</h1><p>%s</p>',shift);
	exit;
}

###---------
package HtmlOut;
sub new
{
	bless { q => '' };
}
sub header
{
	my($obj,$mode) = @_;

	$obj->{q} .= sprintf '<html><head><title>%s%s</title></head><body>',
					$ini::title , ($mode ? " - $mode" : undef);
}
sub out
{
	my($obj) = @_;
	$obj->{q} .= '</body></html>';

	print "Content-type: text/html; charset=Shift_JIS\n";
	printf "Content-length: %d\n\n" , length($obj->{q});

	&jcode::euc2sjis(\$obj->{q});
	print $obj->{q};
}

###---------
package PostForms;
sub oya
{
	return
	qq!<h2>新規投稿</h2><form action="$ini::scriptwri" method=post>!
	. qq!Name<input name=name size=20><br>!
	. qq!Subj<input name=subj size=20><br>!
	. qq!<textarea cols=20 rows=6 name=comment></textarea><br>color !
	. &SozaiBank::irolist
	. qq!<input type=hidden name=chtm value=1>!
	. qq!<br><input type=submit value="新規投稿"></form>!;
}

sub res
{
	my($pick) = @_;

	return 
	"<h2>返信 #$pick</h2>"
	. qq!<form action="$ini::scriptwri" method=post>!
	. qq!Name <input name=name size=20><br>!
	. qq!<textarea cols=20 rows=6 name=comment></textarea><br>color !
	. &SozaiBank::irolist
	. qq!<input type=hidden name=chtm value=1>!
	. qq!<input type=hidden name=resno value=$pick>!
	. qq!<br><input type=submit value="返信"></form>!;
}


###---------
package PrintArticle;
sub main
{
	my($logobj,$pick) = @_;

	my($tmp,$line,$seeflag);
	while($line = $logobj->lread()){
		(index($line, "\t$pick\t") != 4 ) && next;
		$oyaflag = 0;
		if(substr($line,0,1) eq '*'){ $oyaflag = 1;}
		else{ ++$rescnt; }

		$tmp .= &lettering($line,$oyaflag,$rescnt);
	}
	return $tmp . qq!<br><a href="$ini::plug_chtm?res=$pick" accesskey=1>→返信</a>!;
}
sub lettering
{
	my($ATC);
	($ATC{seri},$ATC{number},$ATC{date},$ATC{name},$ATC{subj},$ATC{comment},$ATC{color},$ATC{email},
		$ATC{url},$ATC{icon},$ATC{edt},$ATC{ipaddr},$ATC{pwd})
			= split("\t",shift());

	if( shift() ){
		return  qq!<h2>$ATC{subj} $ATC{name}</h2>!
				 . qq!<p><font color="$ATC{color}">$ATC{comment}</font></p>!;
	}else{
		return qq!ο$ATC{name} <font color="$ATC{color}">$ATC{comment}</font><br>!;
	}
}

###---------
package ThreadMode;
sub main
{
	my($logobj) = @_;

	my($tmp) =  "<h2>記事一覧</h2>";

	my($line,$i,$ankor,$parent,$flag,$rescnt);
	while($line = $logobj->lread()){
		if(substr($line,0,1) eq '*'){
			if($main::FORM{st} < $i){
				$ankor++;
				if($ankor > $main::FORM{show}){ $flag = 1; last; }
				$tmp .= &show(\$parent,$rescnt);
				$rescnt = 0;
			}
			$i++;
			$parent = $line;
		}else{
			($main::FORM{st} < $i) && $rescnt++;
		}
	}
	close(IN);
	($flag) || ( $tmp .= &show(\$parent,$rescnt));

	return $tmp;
}
sub show
{
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr)
		 = split("\t",${shift()});
	my($rescnt) = shift;

	($subj) ||= ((substr($seri,0,1) eq '*') ? '(無題)' : ' (res) ');

	return sprintf '∇<a href="%s?pick=%d">%d</a>.%d:%s<br>%s<br>',
							$ini::plug_chtm, $number,$number,$rescnt,$name,$subj;
}


###---------
package LapseMode;
sub new
{
	shift;
	my($logobj) = shift;

	my($p) = {};
	$logobj->{oya_num} = 0;

	# シリアル範囲でhash雛形作成
	my($key);
	for(0 .. ($main::FORM{show} -1)){
		$key = $logobj->{seri_last} - $main::FORM{st} - $_ ;
		$key += 1000 if($key < 0);
		($key >= 0) || last;
		$p->{ sprintf '%03d',$key } = '';
	}

	# 雛形に合った記事を読む
	my($seri,$line);
	my($showcnt) = $main::FORM{show};
	while($line = $logobj->lread() ){
		$logobj->{oya_num}++;				# pagerに必須

		($showcnt > 0) || next;

		$seri = substr($line,1,3);
		if( defined($p->{$seri}) ){
			$p->{$seri} = $line;
			--$showcnt;
		}
	}

	bless $p;
}


sub show
{
	my($obj,$logobj) = @_;

	my($buf) = '<h1>lapse</h1>';

	my($key);
	foreach $key (	map { $_->[0] }
					sort { $b->[1] <=> $a->[1] }
					map { [$_, (($_ > $logobj->{seri_last}) ? ($_ -1000) : $_ )] }
				keys %{$obj} ) {

		($obj->{$key}) || next;
		my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr)
			 = split("\t",$obj->{$key});

		($subj) ||= '---' if(substr($seri,0,1) eq '*');

		$buf .=
		 "∇<a href=\"?pick=$number\">$number</a>:$subj"
		. "<br>$name ($date)<br>"
		. qq!<font color="$color">$comment</font><br>!;

	}

	return $buf;
}


###---------
package SozaiBank;
sub irolist
{
	my($tmp);
	my($arr) = \@Sozai::colpalet;
	for ($_ = 0; $_ < scalar(@{$arr}); $_ +=2) {
		($arr->[$_] ne '*') || next;
		$tmp .= qq!<option value="$arr->[$_]">$arr->[$_+1]!;
	}

	return '<select name=color>'. $tmp . '</select>';
}

###---------
package LogReader;
sub new
{
	my($p) = {};

	open(IN,"$ini::logfile") || die "ログファイル「$ini::logfile」が開けません";
	$_ = scalar(<IN>);
	chomp($_);

	split(/,/,$_,5);
	(shift eq '[ealis3]') || die 'ealis 第３世代のログではありません';
	($p->{oya_num},$p->{seri_last},$p->{lastwrite}) = @_[0,2,3];

	bless $p;
}
sub lread
{
	return scalar(<IN>);
}
sub DESTROY
{
	close(IN);
}

BEGIN{
	$SIG{'__DIE__'} = sub{
	print "Content-Language: ja\n";
	print "Content-type: text/plain; charset=euc-jp\n\n";
	print <<"EOD";
<h2>ealisの致命的システムエラーが発生しました。</h2>
<p><strong>$_[0]</strong></p>
<p><a href="$ini::scriptmain?">Refresh</a></p>

<pre>
// perl env
	perl: $]  (at $^X )
	OS  : $^O
	file: $0
// cgi env
	CONTENT_LENGTH: $ENV{'CONTENT_LENGTH'}
	QUERY_STRING  : $ENV{'QUERY_STRING'}
	REQUEST_METHOD: $ENV{'REQUEST_METHOD'}

	HTTP_PATH  : $ENV{'HTTP_HOST'} $ENV{'SCRIPT_NAME'}
	SERVER_SOFTWARE : $ENV{'SERVER_SOFTWARE'}  -on-  $ENV{'OS'}
// end
</pre>
EOD
	exit;}
}
