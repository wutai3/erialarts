#!/usr/local/bin/perl

# ealis ver.3.0   past-log unit
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC ��)

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



## ����������ȥե�������ɤ߹���
sub read_pcount
{
	open(PNUM,$ini::pnumfile) || die "��$ini::logdir/$ini::pnumfile�פ������ޤ���";
	$PASTNUM = scalar(<PNUM>);
	close(PNUM);
}

## �ե졼����
sub print_frame
{
	# �����ե������¸�ߤ�Ƚ��
	my($loglink);
	unless(-e "$ini::pastdir/$PASTNUM\.html") { 
		$loglink = "$ini::scriptlog?notfound_mes";
	}else{
		# @nifty�к�
		$loglink = ($ini::pasthttp) ? "$ini::pasthttp$PASTNUM.html" : "$ini::pastdir/$PASTNUM.html";
	}

	print "Content-type: text/html; charset=euc-jp\n\n";

	print qq|<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN">\n|;
	print qq!<html lang="ja">\n<head>\n!;
	print qq!\t<meta name="robots" content="NOINDEX, NOFOLLOW">\n!;
	print qq!\t<title>$ini::title  - ����</title>\n!;
	print qq!</head>\n\n!;

	print qq!<frameset cols="155,*" title="����">\n!;
	print qq!\t<frame name="menu" frameborder=0 src="$ini::scriptlog?menu" title="�����ꥹ��">\n!;
	print qq!\t<frame name="data" frameborder=0 src="$loglink" title="��������">\n!;
	print qq!\t<noframes><body>\n!;
	print qq!\t\t<p>�ե졼��̤�б�������<a href="$ini::scriptlog?menu">�ꥹ�Ȳ���</a>�ء�</p>\n!;
	print qq!\t\t<p style="display:none;">$ini::footcom</p>\n!;
	print qq!\t</body></noframes>\n!;
	print qq!</frameset>\n!;

	print "</html>\n";
}

## Log���ʤ��衼
sub print_nolog
{
	if( $PASTNUM == 1){
		print "<h2>�����Ϥޤ���������Ƥ��ޤ���</h2>\n";
		print "<p>�����������($ini::logmax��)��ۤ���ȼ�ưŪ�˺�������ޤ���";
	}else{
		print "<h2>���顼���ǿ��β����Ϥޤ�����Ƥ��ޤ���</h2>\n";
		print "<p>�����ե�����ȥ���������(<strong>$ini::pnumfile</strong>)���ͤ����פ��ޤ���<p>";
	}
}

## �������񤱤뤫���ʿ���
sub check_plogwrite
{
	print "\n\n<h2>������ǽư������å�</h2>\n";
	print "<div class=\"infobox\">\n<ul>\n";

	print "\t<li>dir found �� `-d $ini::pastdir` is <strong>"
			 . ((-d $ini::pastdir) ? 'ok' : 'NG') . "</strong>\n";
	print "\t<li>permisson �� `-w $ini::pastdir` is <strong>"
			 . ((-w $ini::pastdir) ? 'ok' : 'NG') . "</strong>\n";
	print "\t<li>pnumfile �� `-w $ini::pnumfile` is <strong>"
			 . ((-w $ini::pnumfile) ? 'ok' : 'NG') . "</strong>\n";
	print "\t<li>pasthttp �� <strong>"
			 . (($ini::pasthttp) ? $ini::pasthttp : $ini::pastdir) . "</strong>\n";

	print "</ul></div>\n";
}

## ��˥塼��
sub print_menu
{
	print "<h1 class=\"sub\">����</h1>\n\n";

	print "<p class=\"menubox\"><a href=\"$ini::scriptmain?\" target=\"_parent\" accesskey=I>Normal</a>";
	print "/<a href=\"$ini::scriptmain?dhtml\" target=\"_parent\" accesskey=I>DHTML</a>";
	print "/<a href=\"$ini::scriptmain?thread\" target=\"_parent\" accesskey=I>Thread</a>";
	print "</p>\n\n";

	print "<hr>\n";
	print "\t<p><a href=\"$ini::scriptsub?find\" target=\"_parent\" accesskey=M>����ʸ����</a></p>\n";
	print "<hr>\n\n";
	print "<ul class=\"plogfiles\">\n";


	# ������[���]�򿷵����ɽ��
	$ENV{TZ} = 'JST-9';
	my($psize_sigma,$file,$sec,$min,$hour,$mday,$mon,$year,$wday);
	my($i,$file);
	for( $i = $PASTNUM ; $i>0 ; $i--) {
		$file = "$ini::pastdir/$i.html";

		printf '	<li title="%dKB">[<a href="%s" target="data">%s</a>] ',
				(-s $file)/1024,
				(($ini::pasthttp) ? "$ini::pasthttp$i.html" : $file),
				(($i == $PASTNUM) ? '�ǿ�' : $i );

		# �ե���������դ�ɽ��
	    if (-e $file) {
			$psize_sigma += (-s $file);			# ��������Ͽ
			($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime( (stat($file))[9] );
			printf "<var>%02d/%02d/%02d %02d:%02d</var>\n",
					$year % 100,++$mon,$mday,$hour,$min;
		}else{
			print "Not found.\n";
		}
	}
	print "</ul>\n\n<hr>\n";


	# ����ץ����������
	printf "<p>��<strong>%dKB</strong>/p �Ǻ���<br>\n", $ini::pastsize;
	printf "�߷� <strong>%dKB</strong></p>\n", $psize_sigma /1024;
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
	print qq!\t<title>$ini::title - ����</title>\n!;
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
<h2>ealis����̿Ū�����ƥ२�顼��ȯ�����ޤ�����</h2>
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
