#!/usr/local/bin/perl

# ealis ver.3.0   past-log unit
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC 入)

use 5.004;
use vars qw[$PASTNUM];

require './ealis_cfg.cgi';

package main;

	&read_pcount;

	if ($ENV{QUERY_STRING} eq 'menu') { 
		&print_header(TRUE);
		&print_menu;
		&print_footer;
	}elsif ($ENV{QUERY_STRING} eq 'notfound_mes') { 
		&print_header;
		&print_nolog;
		&check_plogwrite;
		&print_footer;
	}elsif ($ENV{QUERY_STRING} eq 'check') { 
		&print_header;
		&check_plogwrite;
		&print_footer;
	}else{
		&print_frame;
	}
exit;



## 過去ログカウントファイルを読み込み
sub read_pcount
{
	open(PNUM,$ini::pnumfile) || die "「$ini::logdir/$ini::pnumfile」が開けません";
	$PASTNUM = scalar(<PNUM>);
	close(PNUM);
}

## フレーム部
sub print_frame
{
	# 過去ログファイルの存在を判別
	my($loglink);
	unless(-e "$ini::pastdir/$PASTNUM\.html") { 
		$loglink = "$ini::scriptlog?notfound_mes";
	}else{
		# @nifty対策
		$loglink = ($ini::pasthttp) ? "$ini::pasthttp$PASTNUM.html" : "$ini::pastdir/$PASTNUM.html";
	}

	print "Content-type: text/html; charset=euc-jp\n\n";

	print qq|<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN">\n|;
	print qq!<html lang="ja">\n<head>\n!;
	print qq!\t<meta name="robots" content="NOINDEX, NOFOLLOW">\n!;
	print qq!\t<title>$ini::title  - 過去ログ</title>\n!;
	print qq!</head>\n\n!;

	print qq!<frameset cols="155,*" title="過去ログ">\n!;
	print qq!\t<frame name="menu" frameborder=0 src="$ini::scriptlog?menu" title="過去ログリスト">\n!;
	print qq!\t<frame name="data" frameborder=0 src="$loglink" title="過去ログ内容">\n!;
	print qq!\t<noframes><body>\n!;
	print qq!\t\t<p>フレーム未対応の方は<a href="$ini::scriptlog?menu">リスト画面</a>へ。</p>\n!;
	print qq!\t\t<p style="display:none;">$ini::footcom</p>\n!;
	print qq!\t</body></noframes>\n!;
	print qq!</frameset>\n!;

	print "</html>\n";
}

## Logがないよー
sub print_nolog
{
	if( $PASTNUM == 1){
		print "<h2>過去ログはまだ作成されていません</h2>\n";
		print "<p>記事が規定数($ini::logmax件)を越えると自動的に作成されます。";
	}else{
		print "<h2>エラー：最新の過去ログはまだ作られていません</h2>\n";
		print "<p>過去ログファイルとログ数カウンタ(<strong>$ini::pnumfile</strong>)の値が一致しません。<p>";
	}
}

## 過去ログが書けるか自己診断
sub check_plogwrite
{
	print "\n\n<h2>過去ログ機能動作チェック</h2>\n";
	print "<div class=\"infobox\">\n<ul>\n";

	print "\t<li>dir found ： `-d $ini::pastdir` is <strong>"
			 . ((-d $ini::pastdir) ? 'ok' : 'NG') . "</strong>\n";
	print "\t<li>permisson ： `-w $ini::pastdir` is <strong>"
			 . ((-w $ini::pastdir) ? 'ok' : 'NG') . "</strong>\n";
	print "\t<li>pnumfile ： `-w $ini::pnumfile` is <strong>"
			 . ((-w $ini::pnumfile) ? 'ok' : 'NG') . "</strong>\n";
	print "\t<li>pasthttp ： <strong>"
			 . (($ini::pasthttp) ? $ini::pasthttp : $ini::pastdir) . "</strong>\n";

	print "</ul></div>\n";
}

## メニュー部
sub print_menu
{
	print "<h1 class=\"sub\">過去ログ</h1>\n\n";

	print "<p class=\"menubox\"><a href=\"$ini::scriptmain?\" target=\"_parent\" accesskey=I>Normal</a>";
	print "/<a href=\"$ini::scriptmain?dhtml\" target=\"_parent\" accesskey=I>DHTML</a>";
	print "/<a href=\"$ini::scriptmain?thread\" target=\"_parent\" accesskey=I>Thread</a>";
	print "</p>\n\n";

	print "<hr>\n";
	print "\t<p><a href=\"$ini::scriptsub?find\" target=\"_parent\" accesskey=M>■全文検索</a></p>\n";
	print "<hr>\n\n";
	print "<ul class=\"plogfiles\">\n";


	# 過去ログの[リンク]を新規順に表示
	$ENV{TZ} = 'JST-9';
	my($psize_sigma,$file,$sec,$min,$hour,$mday,$mon,$year,$wday);
	my($i,$file);
	for( $i = $PASTNUM ; $i>0 ; $i--) {
		$file = "$ini::pastdir/$i.html";

		printf '	<li title="%dKB">[<a href="%s" target="data">%s</a>] ',
				(-s $file)/1024,
				(($ini::pasthttp) ? "$ini::pasthttp$i.html" : $file),
				(($i == $PASTNUM) ? '最新' : $i );

		# ファイルの日付を表示
	    if (-e $file) {
			$psize_sigma += (-s $file);			# サイズを記録
			($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime( (stat($file))[9] );
			printf "<var>%02d/%02d/%02d %02d:%02d</var>\n",
					$year % 100,++$mon,$mday,$hour,$min;
		}else{
			print "Not found.\n";
		}
	}
	print "</ul>\n\n<hr>\n";


	# ログ合計サイズを求める
	printf "<p>約<strong>%dKB</strong>/p で作成<br>\n", $ini::pastsize;
	printf "累計 <strong>%dKB</strong></p>\n", $psize_sigma /1024;
}


## HTML base
sub print_header
{
	print "Content-type: text/html; charset=euc-jp\n";
	print "Pragma: no-cache\n\n";

	print qq!<\!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN">\n!;
	print qq!<html lang="ja">\n<head>\n!;
	print qq!\t<meta http-equiv="content-style-type" content="text/css">\n!;
	print qq!\t<meta name="robots" content="NOINDEX, NOFOLLOW">\n!;
	print qq!\t<link rel="INDEX" href="$ini::scriptmain?">\n!;
	print qq!\t<link rel="stylesheet" type="text/css" href="$ini::cssfile" media="screen,projection">\n!;
	print qq!\t<title>$ini::title - 過去ログ</title>\n!;
	print &doc_styles if(shift());
	print qq!</head>\n\n<body class="plogmenu">\n!;
}
sub print_footer
{
	print "\n\n<hr class=\"section\">\n";
	print "<address>- ealis -</address>\n</body>\n</html>\n";
}
sub doc_styles
{
 <<"EOD";
	<style type="text/css"><!--
		body { margin: 3px 0 0 4px;}
		hr{ margin: 1px 0 }
		p , ul { margin: 0.1em 0em; font-size:10pt; }
		p.menubox { float: none; text-align:center}
		ul li var{ font-size:9pt;}
		ul li{ margin: 1px 2px 1px 15px ; padding:0}
	--></style>
EOD
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
