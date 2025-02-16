#!/usr/local/bin/perl

# ealis ver.3.0   plus plugin
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC 入)

use 5.004;
require './ealis_cfg.cgi';

package iniplus;
	$countmin = 2;					#この数未満は統計に入れない（足切り値）
#	$img_size = 'height=100';		#アイコンでの統計の時、プレビュー画像のサイズ



package main;

	my $mode = $ENV{QUERY_STRING} || 'name';

	 ($mode eq 'nameoya') ? &print_header('発言者統計　at 親記事')
	 :($mode eq 'nameres') ? &print_header('発言者統計　at レス記事')
	 :($mode eq 'thread') ? &print_header('スレッド数統計')
	 :($mode eq 'host') ? &print_header('書き込みドメイン別統計')
	 :($mode eq 'date') ? &print_header('発言日別統計')
	 :($mode eq 'icon') ? &print_header('アイコン別統計')
	 :($mode eq 'color') ? &print_header('文字色別統計')
	 : &print_header('発言者統計');

	&print_menu;
	&start_ranking($mode);

	print "<hr class=\"section\">\n";
	print "<address>- ealis plus -</address>\n</body>\n</html>";
exit;




## 統計処理すたーと！
sub start_ranking
{
	my($mode) = @_;

	print qq!<div class="article">\n!;

	my($logobj)  = new LogPackage $mode;
	my($lstdraw) = new ListDrawer $mode, $logobj;

	# 連想名でソート
	if($mode eq 'date'){ 
		foreach ( sort { $b cmp $a } keys %{$logobj->{db}}) {
			$lstdraw->out(\$_);
		}
		undef($lstdraw);
		$logobj->day_avg();

	# カウントでソート
	}else{
		foreach $_ ( sort { $logobj->{db}->{$b} <=> $logobj->{db}->{$a} } keys %{$logobj->{db}}) {
			$_ || next;
			#最小値未満は表示しない
			($logobj->{db}->{$_} >= $iniplus::countmin) || next;
			$lstdraw->out(\$_);
		}
	}

	print qq!</div>\n!;
}

# 機能めにう
sub print_menu
{
	print qq!<div class="view-select">\n!;
	print qq!\t<span class="label">sort by : </span>\n!;
	print qq!\t<a href="$ini::plug_plus?name" accesskey=M>発言者</a>\n!;
	print qq!\t（<a href="$ini::plug_plus?nameoya" accesskey=M>親記事</a>,<a href="$ini::plug_plus?nameres">レス記事</a>）\n!;
	print qq!\t<a href="$ini::plug_plus?thread" accesskey=M>スレッド数</a>\n!;
	print qq!\t<a href="$ini::plug_plus?host" accesskey=M>ドメイン</a>\n!;
	print qq!\t<a href="$ini::plug_plus?date" accesskey=M>発言日</a>\n!;
	print qq!\t<a href="$ini::plug_plus?color" accesskey=M>文字色</a>\n!;
	print "\t<a href=\"$ini::plug_plus?icon\" accesskey=M>アイコン</a>\n" if(scalar(@Sozai::icopalet));
	print qq!</div>\n<p>\n!;
}

# HTMLのヘッダー
sub print_header
{
	my($mode) = @_;;

	print "Content-type: text/html; charset=euc-jp\n";
	print "Pragma: no-cache\n";

	if($ini::gzip && $ENV{HTTP_ACCEPT_ENCODING}=~ /gzip/ && (-x $ini::gzip)){
		print "Content-Encoding: gzip\n\n";
		open(STDOUT,"| $ini::gzip -1 -c");
	}else{
		print "\n";
	}

	print qq!<\!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n!;
	print qq!<html lang="ja">\n<head>\n!;
	print qq!\t<meta http-equiv="content-type" content="text/html; charset=euc-jp">\n!;
	print qq!\t<meta http-equiv="content-style-type" content="text/css">\n!;
	print qq!\t<meta name="robots" content="NOINDEX, NOFOLLOW">\n!;
	print qq!\t<link rel="stylesheet" type="text/css" href="$ini::cssfile" media="screen,projection">\n!;
	print qq!\t<link rel="index" href="$ini::scriptmain?">\n!;
	print qq!\t<link rel="start" href="$ini::backurl">\n!;
	print qq!\t<link rel="help" href="$ini::scriptsub">\n!;
	print qq!\t<title>$ini::title - plus $mode</title>\n!;
	print qq!\t<style type="text/css"><\!-- \n!;
	print qq!		span.graph_bar{ background: pink; font-size: 8pt;}\n !;
	print qq!		span.graph_bar2{ background: #bde; font-size: 8pt;}\n !;
	print qq!		ol li { border-bottom: 1px dotted #ccc; } \n!;
	print qq!		ol li.head { color: #222255; background:#E6EBF0}\n!;
	print  "\t--></style>\n";
	print "</head>\n\n";

	print "<body>\n\n";
	print qq!<h1 class="sub">$mode</h1>\n!;

	print "<div class=\"menubox\"><p>\n";
	print " <a href=\"$ini::scriptmain?\" accesskey=I>Normal</a>";
	print " <a href=\"$ini::scriptmain?dhtml\" accesskey=I>DynamicHTML</a>";
	print " <a href=\"$ini::scriptmain?thread\" accesskey=I>Thread</a>";
	print " <a href=\"$ini::scriptmain?lapse\" accesskey=I>Lapse</a>\n";
	print "</p></div>\n\n";
}


## ----------------------
package ListDrawer;
#
# グラフレタリング
#
sub new
{
	my($p) = {};

	shift;
	$p->{mode} = shift;
	$p->{logobj} = shift;

	print "<pre>";
	printf "統計母集団: %d, 足切り: %d (発言日別以外)\n", $p->{logobj}->{siguma},$iniplus::countmin;
	print "<ol start=0>\n";
	printf '<li class="head">%-42s cnt    per</li>', 'Name';

	bless $p;
}
sub DESTROY
{
	my $obj = shift;
	print "\n</ol></pre>\n";
}


# モード別に項目名を出力
sub out
{
	my($obj,$pkey) = @_;

	if($obj->{mode} eq 'thread'){
		my($number,$subj) = split("\t",$$pkey,2);

		if(length($subj) > 27) { $subj = substr($subj,0,30) . ' ..';
		}else{ $subj ||= '（無題）'; }

		$subj =~ s/</&lt;/og;
		$subj =~ s/>/&gt;/og;

		$obj->printbar( qq!<a href="$ini::scriptmain?pick=$number">$number</a>: $subj! ,
					length(" $number: $subj ") , $obj->{logobj}->{db}->{$$pkey} );

	}elsif($obj->{mode} eq 'icon'){
		# ファイル名からアイコン名を検索
		my $name,$i;
		for ($i = 0; $i < scalar(@Sozai::icopalet); $i +=2) {
			($Sozai::icopalet[$i] eq $$pkey) || next;
			$name = $Sozai::icopalet[$i+1];
			last;
		}
		$obj->printbar( qq!$name<br><img src="$ini::imgpath$$pkey" $iniplus::img_size  alt="$$pkey">!,
					length($$pkey), $obj->{logobj}->{db}->{$$pkey} );

	}elsif($obj->{mode} eq 'color'){
		# コードから文字色名を検索
		my $name,$i;
		for ($i = 0; $i < scalar(@Sozai::colpalet); $i +=2) {
			($Sozai::colpalet[$i] eq $$pkey) || next;
			$name = ' : ' . $Sozai::colpalet[$i+1];
			last;
		}

		$obj->printbar( qq!<span style="color:$$pkey">■ $$pkey$name</span>!, 
					length("■ $$pkey$name") ,$obj->{logobj}->{db}->{$$pkey} );

	}elsif($obj->{mode} eq 'name'){
		$obj->printbar( &make_findlink($$pkey), 
					length($$pkey) , $obj->{logobj}->{db}->{$$pkey},
					$obj->{logobj}->{db_oya}->{$$pkey} ,  $obj->{logobj}->{db_res}->{$$pkey});

	}else{
		$obj->printbar( &make_findlink($$pkey), length($$pkey) , $obj->{logobj}->{db}->{$$pkey});
	}
}


# 値を入れると表を書く
sub printbar  # (挿入するHTML,表示文字, 値 , 値2,3(省略可) ) 
{
	my($obj,$content,$strlen,$value,$value1,$value2) = @_;

	# パーセントを算出
	$value || return;
	my($persentage) = ($value / $obj->{logobj}->{siguma}) * 100 ;

	# 項目名,値を出力
	printf '<li>%s%s  %4s  %4d%% ', $content, ' 'x(40 - $strlen), $value, $persentage;

	# グラフ
	if(!$value2){
		printf '<span class="graph_bar">%s</span>' , '.' x int($persentage/2);
	}else{
		printf '<span class="graph_bar">%s</span>' , '.' x int(($value1 / $obj->{logobj}->{siguma}) * 50);
		printf '<span class="graph_bar2">%s</span>', '.' x int(($value2 / $obj->{logobj}->{siguma}) * 50);
	}

	print '</li>';
}

sub make_findlink
{
	my($input) = @_;

	# 日本語をurlに使うときはエンコード
	my($url) = $input;
	$url =~ s/(\W)/sprintf('%%%02X', ord($1))/eg;

	return sprintf '<a href="%s?find;cond=and;zone=now;caps=1;word=%s">%s</a>',
			$ini::scriptsub, $url, $input;
}


### ----------------------
package LogPackage;
#
# 処理データーを読み込む
#
sub new
{
	shift;
	my $mode = shift;

	my($p) = {};

	open(DB,"$ini::logfile") || die "ログファイル「$ini::logfile」が開けません";
	(index(scalar(<DB>), '[ealis3]' ) == 0 ) || die 'ealis 第３世代のログではありません';

	my($oyasubj,$oyaflag);
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd);
	while (<DB>) {
		($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd)
			= split("\t",$_);
		$oyaflag = ((substr($seri,0,1) eq '*') ? 1 : 0 );

		if($mode eq 'name'){
			$p->{db}->{$name}++;
			$p->{ (($oyaflag) ? 'db_oya' : 'db_res')}->{$name}++;
		}elsif($mode eq 'nameoya'){
			($oyaflag) || next;
			$p->{db}->{$name}++;
		}elsif($mode eq 'nameres'){
			(!$oyaflag) || next;
			$p->{db}->{$name}++;

		}elsif($mode eq 'thread'){
			if($oyaflag){ $oyasubj = $subj;				#親記事処理
			}else{ $p->{db}->{ "$number\t$oyasubj"}++; }		 	#レス記事のカウント

		}elsif($mode eq 'host'){
			if( $ipaddr =~ /[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*$/ ){
				;	# nothing to do
			}else {
				$ipaddr =~ s/^.+\.([\w\.\~\-\/\?\&\+\=\:\@\%\;\#]+)\.([a-z0-9A-Z]+)\.([a-z0-9A-Z]+)$/$1.$2.$3/g;
			}
			$p->{db}->{$ipaddr}++;
		}elsif($mode eq 'date'){
			$p->{db}->{ substr($date,0,8)}++;
		}elsif($mode eq 'icon'){
			($icon) || next;
			$p->{db}->{$icon}++;
		}elsif($mode eq 'color'){
			$p->{db}->{$color}++;
		}
		$p->{siguma}++;	# ログ行数
	}
	close(DB);

	bless $p;
}

sub day_avg
{
	my($obj) = @_;
	printf '<p>平均書き込み数　%0.2f 件/日</p>', ($obj->{siguma} / scalar(keys %{$obj->{db}}));
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
</pre>
EOD
	exit;}
}
