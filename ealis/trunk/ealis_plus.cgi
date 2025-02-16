#!/usr/local/bin/perl

# ealis ver.3.0   plus plugin
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC ��)

use 5.004;
require './ealis_cfg.cgi';

package iniplus;
	$countmin = 2;					#���ο�̤�������פ�����ʤ���­�ڤ��͡�
#	$img_size = 'height=100';		#��������Ǥ����פλ����ץ�ӥ塼�����Υ�����



package main;

	my $mode = $ENV{QUERY_STRING} || 'name';

	 ($mode eq 'nameoya') ? &print_header('ȯ�������ס�at �Ƶ���')
	 :($mode eq 'nameres') ? &print_header('ȯ�������ס�at �쥹����')
	 :($mode eq 'thread') ? &print_header('����åɿ�����')
	 :($mode eq 'host') ? &print_header('�񤭹��ߥɥᥤ��������')
	 :($mode eq 'date') ? &print_header('ȯ����������')
	 :($mode eq 'icon') ? &print_header('��������������')
	 :($mode eq 'color') ? &print_header('ʸ����������')
	 : &print_header('ȯ��������');

	&print_menu;
	&start_ranking($mode);

	print "<hr class=\"section\">\n";
	print "<address>- ealis plus -</address>\n</body>\n</html>";
exit;




## ���׽����������ȡ�
sub start_ranking
{
	my($mode) = @_;

	print qq!<div class="article">\n!;

	my($logobj)  = new LogPackage $mode;
	my($lstdraw) = new ListDrawer $mode, $logobj;

	# Ϣ��̾�ǥ�����
	if($mode eq 'date'){ 
		foreach ( sort { $b cmp $a } keys %{$logobj->{db}}) {
			$lstdraw->out(\$_);
		}
		undef($lstdraw);
		$logobj->day_avg();

	# ������Ȥǥ�����
	}else{
		foreach $_ ( sort { $logobj->{db}->{$b} <=> $logobj->{db}->{$a} } keys %{$logobj->{db}}) {
			$_ || next;
			#�Ǿ���̤����ɽ�����ʤ�
			($logobj->{db}->{$_} >= $iniplus::countmin) || next;
			$lstdraw->out(\$_);
		}
	}

	print qq!</div>\n!;
}

# ��ǽ��ˤ�
sub print_menu
{
	print qq!<div class="view-select">\n!;
	print qq!\t<span class="label">sort by : </span>\n!;
	print qq!\t<a href="$ini::plug_plus?name" accesskey=M>ȯ����</a>\n!;
	print qq!\t��<a href="$ini::plug_plus?nameoya" accesskey=M>�Ƶ���</a>,<a href="$ini::plug_plus?nameres">�쥹����</a>��\n!;
	print qq!\t<a href="$ini::plug_plus?thread" accesskey=M>����åɿ�</a>\n!;
	print qq!\t<a href="$ini::plug_plus?host" accesskey=M>�ɥᥤ��</a>\n!;
	print qq!\t<a href="$ini::plug_plus?date" accesskey=M>ȯ����</a>\n!;
	print qq!\t<a href="$ini::plug_plus?color" accesskey=M>ʸ����</a>\n!;
	print "\t<a href=\"$ini::plug_plus?icon\" accesskey=M>��������</a>\n" if(scalar(@Sozai::icopalet));
	print qq!</div>\n<p>\n!;
}

# HTML�Υإå���
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
# ����ե쥿���
#
sub new
{
	my($p) = {};

	shift;
	$p->{mode} = shift;
	$p->{logobj} = shift;

	print "<pre>";
	printf "�����콸��: %d, ­�ڤ�: %d (ȯ�����̰ʳ�)\n", $p->{logobj}->{siguma},$iniplus::countmin;
	print "<ol start=0>\n";
	printf '<li class="head">%-42s cnt    per</li>', 'Name';

	bless $p;
}
sub DESTROY
{
	my $obj = shift;
	print "\n</ol></pre>\n";
}


# �⡼���̤˹���̾�����
sub out
{
	my($obj,$pkey) = @_;

	if($obj->{mode} eq 'thread'){
		my($number,$subj) = split("\t",$$pkey,2);

		if(length($subj) > 27) { $subj = substr($subj,0,30) . ' ..';
		}else{ $subj ||= '��̵���'; }

		$subj =~ s/</&lt;/og;
		$subj =~ s/>/&gt;/og;

		$obj->printbar( qq!<a href="$ini::scriptmain?pick=$number">$number</a>: $subj! ,
					length(" $number: $subj ") , $obj->{logobj}->{db}->{$$pkey} );

	}elsif($obj->{mode} eq 'icon'){
		# �ե�����̾���饢������̾�򸡺�
		my $name,$i;
		for ($i = 0; $i < scalar(@Sozai::icopalet); $i +=2) {
			($Sozai::icopalet[$i] eq $$pkey) || next;
			$name = $Sozai::icopalet[$i+1];
			last;
		}
		$obj->printbar( qq!$name<br><img src="$ini::imgpath$$pkey" $iniplus::img_size  alt="$$pkey">!,
					length($$pkey), $obj->{logobj}->{db}->{$$pkey} );

	}elsif($obj->{mode} eq 'color'){
		# �����ɤ���ʸ����̾�򸡺�
		my $name,$i;
		for ($i = 0; $i < scalar(@Sozai::colpalet); $i +=2) {
			($Sozai::colpalet[$i] eq $$pkey) || next;
			$name = ' : ' . $Sozai::colpalet[$i+1];
			last;
		}

		$obj->printbar( qq!<span style="color:$$pkey">�� $$pkey$name</span>!, 
					length("�� $$pkey$name") ,$obj->{logobj}->{db}->{$$pkey} );

	}elsif($obj->{mode} eq 'name'){
		$obj->printbar( &make_findlink($$pkey), 
					length($$pkey) , $obj->{logobj}->{db}->{$$pkey},
					$obj->{logobj}->{db_oya}->{$$pkey} ,  $obj->{logobj}->{db_res}->{$$pkey});

	}else{
		$obj->printbar( &make_findlink($$pkey), length($$pkey) , $obj->{logobj}->{db}->{$$pkey});
	}
}


# �ͤ�������ɽ���
sub printbar  # (��������HTML,ɽ��ʸ��, �� , ��2,3(��ά��) ) 
{
	my($obj,$content,$strlen,$value,$value1,$value2) = @_;

	# �ѡ�����Ȥ򻻽�
	$value || return;
	my($persentage) = ($value / $obj->{logobj}->{siguma}) * 100 ;

	# ����̾,�ͤ����
	printf '<li>%s%s  %4s  %4d%% ', $content, ' 'x(40 - $strlen), $value, $persentage;

	# �����
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

	# ���ܸ��url�˻Ȥ��Ȥ��ϥ��󥳡���
	my($url) = $input;
	$url =~ s/(\W)/sprintf('%%%02X', ord($1))/eg;

	return sprintf '<a href="%s?find;cond=and;zone=now;caps=1;word=%s">%s</a>',
			$ini::scriptsub, $url, $input;
}


### ----------------------
package LogPackage;
#
# �����ǡ��������ɤ߹���
#
sub new
{
	shift;
	my $mode = shift;

	my($p) = {};

	open(DB,"$ini::logfile") || die "���ե������$ini::logfile�פ������ޤ���";
	(index(scalar(<DB>), '[ealis3]' ) == 0 ) || die 'ealis �裳����Υ��ǤϤ���ޤ���';

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
			if($oyaflag){ $oyasubj = $subj;				#�Ƶ�������
			}else{ $p->{db}->{ "$number\t$oyasubj"}++; }		 	#�쥹�����Υ������

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
		$p->{siguma}++;	# ���Կ�
	}
	close(DB);

	bless $p;
}

sub day_avg
{
	my($obj) = @_;
	printf '<p>ʿ�ѽ񤭹��߿���%0.2f ��/��</p>', ($obj->{siguma} / scalar(keys %{$obj->{db}}));
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
