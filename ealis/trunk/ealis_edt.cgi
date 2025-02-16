#!/usr/local/bin/perl

# ealis ver.3.0   edit unit
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC ��)

use 5.004;
use Fcntl qw[:flock];
use Time::Local;
use vars qw[%FORM $ADMINFLAG];

require './ealis_cfg.cgi';

package main;
	&form_decode;

	if( defined($FORM{admin}) ) { 
		&print_header('������˥塼');
		&print_adminmenu;
		&print_footer;

	}elsif($FORM{mode} eq 'rewrite') { 
		require 'jcode.pl';
		&EditLog::check_input;
		&EditLog::rewrite;
		&http_locate;
	}elsif($FORM{mode} eq 'erase') { 
		&EditLog::erase;
		&http_locate;

	}elsif($FORM{mode} eq 'edit') { 
		&print_header('�����Խ��⡼��');
		&MenuView::print_editview;
		&print_footer;
	}elsif( shift(@{$FORM{sel}}) ){
		&error('����̿�᤬���򤵤�Ƥ��ޤ���');

	}else{
		&print_header( (($ADMINFLAG) ? '���������⡼��' : '������˥塼') );
		my $logobj = new LogReader;
		my $cook = &init_cookie;

		&MenuView::print_noteMenu($cook);
		if(defined($FORM{max})){ $FORM{show} = $ini::logmax; }
		&print_logpager($logobj);
		&MenuView::print_articles($logobj);
		&print_logpager($logobj);
		&print_footer;
	}
exit;



#�� Location�Ǹ���CGI���᤹
sub http_locate
{
	&initLocation;

	$ini::locate .= $ini::scriptedt;
	$ini::locate .= "?key=$FORM{key}" if($ADMINFLAG);

	print "Content-type: text/html; charset=euc-jp\n";
	print "Pragma: no-cache\n";
	print "Location: $ini::locate\n\n";

	print "<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML 2.0//EN\">\n";
	print "<html><head>\n";
	print "<meta http-equiv=\"content-type\" content=\"text/html; charset=euc-jp\">\n";
	print "<title>$ini::title : ��ƴ�λ</title>\n";
	print "</head>\n<body>\n";
	print "<h1>������λ���ޤ���</h1>\n";
	print "<p>�ʲ���URL���餪��꤯��������</p>\n";
	print "<p><a href=\"$ini::locate\">$ini::locate</a></p>\n";
	print "<hr><address>- ealis -</address>\n";
	print "</body></html>\n";
}

sub initLocation
{
	$ini::locate ||= sprintf('http://%s%s/',  $ENV{SERVER_NAME},
			substr($ENV{SCRIPT_NAME}, 0 , rindex($ENV{SCRIPT_NAME},'/') )
	);
}

sub print_logpager
{
	my($logobj) = @_;

	print qq!\n<div class="log-pager">\n!;
	print qq!\t<span class="label">Log <span class="key">P</span>ager :</span>��\n!;

	my $current_tab = $FORM{start} / $FORM{show};	# ���ߤε������ǿ���¬��
	$current_tab = ( $current_tab == int($current_tab) ? $current_tab : int($current_tab + 1) ) +1;
	my $tab = ($current_tab >= 20) ? ($current_tab - 10) : 1;	# ����10���ɽ��
	my $arg = "key=$::FORM{key};" if($::ADMINFLAG);

	my($gopage);
	for(0 .. 20){
		if($tab == $current_tab){
			print "\t<em>$tab</em>\n";
		}else{
			$gopage = $FORM{show} * ( $tab - 1 );		# �����ܤε�����������
			($gopage < $logobj->{oya_num}) || last;			# ��ͭ����Ƶ��������¿����
			printf qq!\t<a href="%s?%sstart=%d;show=%d" accesskey=P>%d</a>\n!,
							$ini::scriptedt,$arg,$gopage,$FORM{show},$tab;
		}
		$tab++;
	}
	print qq!\t<a href="$ini::scriptlog" accesskey=P>File</a>\n!  if($ini::pnumfile);

	# �ڡ����������ڤ��ؤ�
	my $step = int($ini::show /2);		# �ѹ���

	print "\t����\@$FORM{show}atc/p(";
	printf '<a href="%s?%sstart=%d;show=%d" accesskey=P>+%d</a> ', $ini::scriptedt,$arg,$FORM{start},$FORM{show}+$step,$step;
	printf '<a href="%s?%sstart=%d;show=%d" accesskey=P>-%d</a> ', $ini::scriptedt,$arg,$FORM{start},$FORM{show}-$step,$step  if($FORM{show} > $step);
	printf '<a href="%s?%sstart=%d;show=%d" accesskey=P>def</a> ', $ini::scriptedt,$arg,$FORM{start},$ini::show  if($ini::show != $FORM{show});
	print  qq!, <a href="$ini::scriptedt?thread;max" accesskey=P>max:$ini::logmax</a>!;

	print ")\n</div>\n\n";
}


### others
#�� HTML�Υإå���
sub print_header
{
	my($title) = @_;

	print "Pragma: no-cache\n";
	print "P3P: CP='ONLi COM CUR OUR'\n";
	print "Content-type: text/html; charset=euc-jp\n\n";

	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\">\n";
	print qq!<html lang="ja">\n<head>\n!;
	print qq!\t<meta http-equiv="content-style-type" content="text/css">\n!;
	print qq!\t<meta http-equiv="Content-Script-Type" content="text/javascript">\n!;
	print qq!\t<meta name="robots" content="NOINDEX, NOFOLLOW">\n!;
	print qq!\t<link rel="stylesheet" type="text/css" href="$ini::cssfile" media="screen,projection">\n!;
	print qq!\t<link rel="index" href="$ini::scriptmain?">\n!;
	print qq!\t<link rel="start" href="$ini::backurl">\n!;
	print qq!\t<link rel="help" href="$ini::scriptsub">\n!;
	print qq!\t<title>$ini::title - $title</title>\n</head>\n!;

	print "<body>\n\n";
	print "<h1 class=\"sub\">$title</h1>\n\n";

	print "<div class=\"menubox\"><p>";
	print "<a href=\"$ini::scriptmain?\" accesskey=I>Normal</a>";
	print " <a href=\"$ini::scriptmain?dhtml\" accesskey=I>DynamicHTML</a>";
	print " <a href=\"$ini::scriptmain?thread\" accesskey=I>Thread</a>";
	print " <a href=\"$ini::scriptmain?lapse\" accesskey=I>Lapse</a>";
	print "</p><hr></div>\n\n";

}

## ���顼���� 
sub error
{
	&print_header('ealis error')  unless($_[1]);

	print qq!<h2>ealis�Υ��顼�Ǥ�</h2>\n!;
	print qq!<div class="infobox"><p>@{[ shift() ]}</p></div>\n!;
	print qq!<hr class="section">\n</body></html>\n!;

	exit;
}

sub form_decode
{
	($ENV{CONTENT_LENGTH} < 51200) || &error('��ƥǡ������礭�����ޤ���');

	my($buf,$name, $value);
	read(STDIN, $buf, $ENV{CONTENT_LENGTH}) if($ENV{REQUEST_METHOD} eq 'POST');
	$buf .= ';' .$ENV{QUERY_STRING};

	foreach ( split(/[&;]/,$buf) ) {
		($name, $value) = split(/=/, $_,2);
		$value =~ tr/+/ /;
		$value =~ s/%(..)/pack('H2',$1)/eg;
		$value =~ s/\t/    /og;

		if ($name eq 'sel') {
			($value =~ /^[\w\*\-]+$/) || &error("�����ʵ�������Ǥ��� '$value'");
			push(@{$FORM{sel}},$value);
		}else{
			$FORM{$name} = $value || '';
		}
	}

	# set default
	$FORM{start} ||= 0;
	$FORM{show} ||= $ini::show;

	$ADMINFLAG = 1 if($FORM{key} && $FORM{key} eq $ini::pass);
}
# ���å��������
sub init_cookie
{
	my($p) = {};
	my($name, $value);
	foreach ( split(/;/,$ENV{HTTP_COOKIE}) ) {
		($name, $value) = split(/=/,$_,2);
		$name =~ tr/ //d;

		($name eq 'EALIS') || next;
		$value =~ s/%(..)/pack('H2',$1)/eg;
		foreach ( split(/,/,$value) ) {
			($name, $value) = split(/:/,$_,2);
			$p->{$name} = $value;
		}
		last;
	}
	return $p;
}

sub print_footer
{
	print "\n\n<hr class=\"section\">\n";
	print "<address> - ealis - </address>\n</body></html>\n";
}


## ��������������
sub print_adminmenu
{
	print qq!<h2>���������⡼��</h2>\n!;
	print qq!<form action="$ini::scriptedt" method=get>\n<div class="infobox">\n!;
	print qq!\t<p>�������Խ����������Ԥ��ޤ���<br>�ѥ���ɶ�������̾�κ���⡼�ɤˤʤ�ޤ���</p>\n!;
	print qq!\t<p>�����ԥѥ���ɡ� <input type=password name="key" size=11 maxlength=8 value=""><input type=submit value="ǧ��"></p>\n!;
	print qq!</div>\n</form>\n\n!;

	print qq!<h2>�����ƥ����</h2>\n<div class="infobox">\n<ul>\n!;

	{
		my($lines);
		open(IN,$ini::logfile) || die "���ե������$ini::logfile�פ������ޤ���";
		printf "\t<li><strong>LogHeader</strong>: %s\n", scalar(<IN>);
		while( read(IN,$_,1024) ){ $lines += tr/\n//; }		# ���Կ������
		close(IN);

		printf("\t<li><strong>Logfile:</strong> <var>%d</var>KB,<var>%d</var>lines",
					 (-s $ini::logfile)/1024 , $lines );;
		print " (999lines��ۤ��ʤ��褦��\$ini::logmax��Ĵ�����뤳��)\n";
	}

	&main::initLocation;
	print "\t<li><strong>Locate:</strong> $ini::locate\n";

	if($ini::gzip){
		printf "\t<li><strong>Content-Encoding:</strong> %s(%s) , UA is %s\n",
				$ini::gzip,
				((-x $ini::gzip) ? 'found' : 'not found'),
				(($ENV{HTTP_ACCEPT_ENCODING}=~ /gzip/) ? 'ready' : 'non-support');
	}

	open(FL, ">>$ini::lockfile") || die "$ini::lockfile �������ޤ���";
	eval{ flock(FL, 2); };
	printf "\t<li><strong>flock</strong>: %s\n",  @{[ ($@) ? 'error' : 'supported' ]};
	close(FL);

	print qq!\t<li><a href="$ini::scriptlog?check">������ǽư������å�</a>\n! if($ini::scriptlog);

	print "</ul>\n</div>\n";
}


###---------
##�� ����������Խ�����ɽ��
package MenuView;
## ������˥塼
sub print_noteMenu
{
	my($cook) = @_;

	print qq!<form action="$ini::scriptedt?" method=GET>\n\n!;
	print qq!<div class="infobox"><p>\n!;

	if($::ADMINFLAG){
		print "\t�������⡼�ɤ�ư��Ƥ��ޤ���<br>\n";
		print "\t�������Խ�����<strong>��Ĥ�������</strong>�������������<strong>ʣ�������ǽ</strong>�Ǥ���<br>\n";
		print "\t���Ƶ�����������Ȥ����ֿ�������������ޤ���\n";
	}else{
		print "\t������������å����������������Ϥ�����ˡ�ɬ�פʽ��������Ӽ¹Ԥ��Ƥ���������<br>\n";
		print "\t�������Խ�����ǽ�ʤΤ���Ƥ��飴�����ְ���Ǥ���<br>\n" if($ini::useredit == 2);
		print "\t���ֿ����դ����Ƶ����ϴ����Ͱʳ�����Ǥ��ޤ���\n";
	}
	print "</p></div>\n";


	print qq!<div class="valueinput">\n\t������!;
	if($::ADMINFLAG){
		print '<input type=radio name="mode" value="edit" checked>���ε������Խ���<strong>ñ���Τ�</strong>��';
		print '<input type=radio name="mode" value="erase">���ε���������<strong>ʣ����ǽ</strong>��';
	}elsif($ini::useredit){
		print '<input type=radio name="mode" value="edit" checked>���ε������Խ�';
		print '<input type=radio name="mode" value="erase">���ε�������';
	}else{
		print '<input type=radio name="mode" value="erase" checked>���ε�������';
	}

	print "\n\t����";
	print (($::ADMINFLAG)
			? qq!<input type=hidden name="key" value="$::FORM{key}">!
			: qq!<strong>��������</strong> <input type=text name="key" size=10 value="$cook->{pwd}" style="ime-mode:disabled">!);

	print qq!\n\t<input type=submit value="�¹�"><input type=reset value="���ꥢ">\n!;
	print "</div>\n<hr>\n";
}

## �Ρ��Ȱ���
sub print_articles
{
	my($logobj) = @_;

	print qq!\n<div class="article">\n\n<ul class="edtview">\n!;

	my($ankor,$oyaflag,$rescnt,$line,$nowline);
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd);
	while($line = $logobj->lread()){
		$oyaflag = 0;
		# ���ߤοƤ��İ�
		if(substr($line,0,1) eq '*') { $nowline++; $oyaflag=1;}
		($::FORM{start} >= $nowline) && next;

		($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);

		# �ͤ򥨥󥳡���
		$comment =~ s'<br>' 'go;
		$comment = substr($comment,0,58).'...' if(length($comment) > 60);
		$comment =~ s'<'&lt;'go;
		$comment =~ s'>'&gt;'go;

		if($oyaflag){
			$ankor++;
			($ankor > $::FORM{show}) && last;
			if($rescnt == 1){ print "\t\t</ol>\n\t</li>\n"; $rescnt = 0;}
			($subj) ||= '(̵��)';

			print "\t<li><h3>";
			print &make_chkbox($seri);

			print qq!\t\t[<span class="atclno"><a href="$ini::scriptmain?pick=$number">$number</a></span>] <em>$subj</em>!;
			print qq!�� From: <cite>$name</cite>�� <span class="stamp">($date)</span><br>\n\t\t $comment !;
			print qq!\n\t\t��<span class="stamp">[$ipaddr]</span>!  if ($::ADMINFLAG);
			print qq!</h3>\n!;
		}else{
			if($rescnt == 0){ print "\n\t\t<ol>\n"; $rescnt = 1; }

			print "\t\t<li>";
			print &make_chkbox($seri);
			print qq!\t\t\t<cite>$name</cite> <span class="stamp">($date)</span>\n\t\t\t$comment!;
			print qq!\n\t\t\t<span class="stamp">[$ipaddr]</span>!  if ($::ADMINFLAG);
			print "</li>\n";
		}
	}
	print "\t\t</ol>\n" if($rescnt == 1);
	print "\t</li>\n</ul>\n</div>\n\n";
	print "</form>\n";
}
# �����å���
sub make_chkbox
{
	return sprintf qq!<input type=%s name="sel" value="%s">\n!,
			(($::ADMINFLAG) ? 'checkbox' : 'radio') , shift;
}


##  �����Խ����̤�ɽ��
sub print_editview
{
	scalar(@{$::FORM{sel}}) || &::error('�Խ��оݵ��������ꤵ��Ƥ��ޤ���',TRUE);
	(scalar(@{$::FORM{sel}}) == 1) || &::error('�Խ��оݵ����ϰ�Ĥ�������Ǥ���������<br>�⤷���ϡ��Խ��⡼�ɡפȡְ�����⡼�ɡפ�ְ㤨�Ƥޤ���',TRUE);

	# ������pick
	my $logobj = new LogReader;
	my($line,$hitcnt);
	while($_ = $logobj->lread()){
		(substr($_,0,4) eq ${$::FORM{sel}}[0]) || next;
		$line = $_;
		$hitcnt++;
	}
	($line) || &::error("�Խ��оݵ��������Ĥ���ޤ���Ǥ�����(no ${$::FORM{sel}}[0])");
	($hitcnt == 1) || &::error("�Խ��оݵ�����ʣ��($hitcnt)�ޥå������Τǡ�ǰ�Τ����������ߤ��ޤ�����");

	# �ǡ������
	chomp($line);
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);
	&EditLog::decide_key($pwd,TRUE);		# �ä��Ƥ⤤��
	($::ADMINFLAG) || &EditLog::decide_edtlim($date) || &::error('�Խ����¡ʽ����Ƥ��飴�����֡ˤ�᤮�Ƥ���ΤǤ��ε������Խ��Ǥ��ޤ���',TRUE);

	# �ǡ�������
	$comment =~ s/<br>/\n/og;
	$comment =~ s/&/&amp;/og;
	$comment =~ s/<[^>]*>//g  if(!$ini::allowtag);   # ��ư��󥯤�<q>����

	($pwd) ||= '&lt;uninputed&gt;';
	($url) &&= "http://$url";


	print <<"EOD";
<script type="text/javascript"><!--
	function colsel() { window.open('$ini::scriptsub?pickcolor','colsel','scrollbars=no,status=no,height=300,width=380,resizable=yes'); }
	function chkin(){
		if(document.forms[0].key.value == ''){
			alert('�������������Ϥ���Ƥ��ޤ���');
			return(false);
		}
		return(true);
	}
--></script>

<form action="$ini::scriptedt?mode=rewrite" method=POST accept-charset="euc-jp" onSubmit="return chkin()">
<fieldset class="edtform"><legend>��������</legend>
	<table border=0>
		<tr><th><label class="requisite" for="fmname">Name</label></th>
		<td><input type=text name="name" size=30 value="$name" class="in" id="fmname"></td>
		<th>Mail</th><td><input type=text name="email" size=30 value="$email" class="in"></td></tr>
		<tr><th>Title</th>
		<td><input type=text name="subj" size=40 value="$subj" class="in"></td>
		<th>��Key</th><td><var>$pwd</var></td></tr>
		<tr><th>URL</th>
		<td colspan=3><input type=text size=78 name="url" value="$url" class="in"></td></tr>
	</table>

	<p><textarea cols=70 rows=10 name="comment" wrap="soft">$comment</textarea></p>
	<div class="list-colors">
		<script type="text/javascript"><!--
			 document.writeln('<a href="javascript:prevtxt(0)">&lt;color&gt;<\\/a>');
		//--></script>
		<noscript><a href="$ini::scriptsub?prev_color" target="elsprv">&lt;color&gt;</a></noscript>
		@{[ &ins_iroradio ]} / 
		<input type=radio name="color" value="" checked><span style="color:$color">��</span><input type=text name="color2" value="$color" size=10 class="in"><a href="javascript:colsel()"><small>����</small></a>
	</div>
	<p>@{[ &ins_icolist(\$icon) ]}</p>
	<p><!--  ���������Ѥ�������(�Խ�����) -->
		�������<input type="hidden" name="date" value="$date"><var>$date</var><br>
		����å��ֹ桧<var>$number</var>, 
		�������ꥢ�롧<input type="hidden" name="seri" value="$seri"><var>$seri</var><br>
		@{[ ($::ADMINFLAG) ? "IP���ɥ쥹��<var>$ipaddr</var>" : undef ]}
	</p>
	<hr>
	<p>@{[ ($::ADMINFLAG) ? '�������Խ��⡼��' : '��ƻ��ε�������']} 
		<input type=text name="key" value="$::FORM{key}" size=25 class="in">
	 ����<input type=submit value="������������������ơ���"><input type=reset value="�ꥻ�å�"></p>
</fieldset>
</form>
EOD
}

sub ins_icolist
{
	(scalar(@Sozai::icopalet)) || return;

	my($picon) = @_;

	my $b;
	$b .= qq!\t\t<a href=\"$ini::scriptsub?prev_ico\" target=\"elsprv\">&lt;icon&gt;</a> \n!;
	$b .= qq!\t\t<select name="icon">\n!;
	$b .= qq!\t\t<option value="$$picon">�ѹ����ʤ�������@{[ $$picon || '�ʤ�']}��\n!;
	$b .= qq!\t\t<option value="*">-------------------\n!;

	my($arr) = \@Sozai::icopalet;
	my($flag);
	for ($_ = 0; $_ < scalar(@{$arr}); $_ +=2) {
		if($arr->[$_] eq '*'){
			$b .= "\t\t<option value=\"\">$arr->[$_+1]";
		}elsif($arr->[$_] eq '**'){
			$b .= '</optgroup>' if($flag);
			$b .= qq!\t\t<optgroup label="$arr->[$_+1]"><option class="group" value="*">$arr->[$_+1]!;
			$flag = 1;
		}else{
			$b .= "\t\t<option value=\"$arr->[$_]\">$arr->[$_+1]";
		}
	}
	$b .= '</optgroup>' if($flag);

	$b .= qq!\t\t</select>\n!;
	return $b;
}
sub ins_iroradio
{
	my $b;
	my $arr = \@Sozai::colpalet;

	for ($_ = 0; $_ < scalar(@{$arr}); $_ +=2) {
		$b .= (($arr->[$_] ne '*') ? qq!<input type=radio name="color" value="$arr->[$_]"><span style="color:$arr->[$_]">��</span>! : '<br>');
	}
	return $b;
}





###---------
##�� �ºݤ��Խ�/���
package EditLog;

# �����񴹻������Ϲ��ܤΥ����å�
sub check_input
{
	($::FORM{key}) || &::error('�������������Ϥ���Ƥ��ޤ���');
	($::ADMINFLAG) || ($ini::useredit) || &::error('���̥桼�����ε����Խ����Ե��Ĥ����ꤵ��Ƥ��ޤ���');
	($::FORM{date} && $::FORM{seri}) || &::error('��̿Ū���顼�������ͤ���­���Ƥ��ޤ�');

	$::FORM{color} ||= $::FORM{color2};

	# ���Ϲ��ܤΥ����å�
	($::FORM{name})    || &::error('̾�������Ϥ���Ƥ��ޤ���');
	($::FORM{comment}) || &::error('�����Ȥ����Ϥ���Ƥ��ޤ���');
	($::FORM{color}) || &::error('ʸ���������Ϥ���Ƥ��ޤ���');
	($::FORM{url} && $::FORM{url} !~ s!^http://!!) && &::error('����������ޤ��󤬡�http://�ʳ��Υ������ޤˤ��б����Ƥ��ޤ���');

	# �������Ȥ��ӽ�
	(index($::FORM{icon},'/') < 0 ) || die '��������ꥹ�Ȥ������Ǥ�';
	($::FORM{icon} ne '*') || &::error('����������������������롼�׸��Ф��ˤʤäƤޤ�');

	# EUC����ʤ���
	my($key);
	while ($key = each(%::FORM)) {
		&jcode::convert( \$::FORM{$key}, 'euc');

		# ;��̵���Τ�&�Ϥ�������
		$::FORM{$key} =~ s/&/&amp;/og if(index($::FORM{$key},';') < 0);

		unless($ini::allowtag && $key eq 'comment') {
			$::FORM{$key} =~ s/</&lt\;/go;
			$::FORM{$key} =~ s/>/&gt\;/go;
			$::FORM{$key} =~ s/"/&quot;/go;
			$::FORM{$key} =~ s/'/&#39;/go;
		}else{
			(index($::FORM{$key},'<!--#') < 0 ) || &::error('SSI�����ػ�');  #-->
		}
	}

	# �ͤ򥨥󥳡���
	if ($ini::allowtag){
		# <���ʤ��Τ�>��������ϰ��Ѥȸ��ʤ�
		$::FORM{comment} =~ s'>'&gt;'g  if(index($::FORM{comment},'<') < 0);
	}elsif ($ini::plug_grad){
		# <gd>�ϵ���
		$::FORM{comment} =~ s'&lt;gd&gt;'<gd>'ig;
		$::FORM{comment} =~ s'&lt;/gd&gt;'</gd>'ig;
	}
	$::FORM{comment} =~ s/\x0D\x0A/<br>/og;
	$::FORM{comment} =~ s/\x0D/<br>/og;
	$::FORM{comment} =~ s/\x0A/<br>/og;
	$::FORM{color} =~ tr/A-Z/a-z/;
}

# �ѥ���ɾȹ����
sub decide_key
{
	my($pwd,$headflag) = @_;

	$pwd =~ tr/\x0D\x0A//d;

	if($::ADMINFLAG) {
		;
	}elsif(!$::FORM{key}){
		&::error('�������������Ϥ��Ƥ���������',$headflag);
	}elsif(!$pwd){
		&::error('���ε����ˤϵ������������ꤵ��Ƥ��ޤ���',$headflag);
	}else{
		(crypt($::FORM{key}, substr($pwd, ((index($pwd, '$1$') == 0) ? 3 : 0) ,2) ) eq $pwd) || &::error('�����������㤤�ޤ���',$headflag);
	}
}


# ����ºݤ˽�����
sub rewrite
{
	my $logobj = new LogReader;

	my $fl = new FileLock;
	$fl->lock;
	open(OUT,">$fl->{out}") || die "��å����ԡ�$fl->{out}�������ԡ�";
	print OUT $logobj->{head};			# �إå��ϼ�Ĥ���

	# �����������������
	if($::FORM{icon} eq '*RAND*'){
		my $key;
		RND:{
			$key = int(rand(scalar(@Sozai::icopalet) /2)) *2;
			(substr((@Sozai::icopalet)[$key],0,1) ne '*') || redo RND;
			$::FORM{icon} = (@Sozai::icopalet)[$key];
			$::FORM{icon} || die 'CFG icon miss';
		}
	}

	my($hitflag,$line);
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd);
	while($line = $logobj->lread()){
		EDT:{
			(!$hitflag) || last EDT;

			# hitȽ��
			(substr($line,0,4) eq $::FORM{seri}) || next;
			($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);
			($date eq $::FORM{date}) || last EDT;		# ¾�ͤ��ѹ����Ƥ��ʤ���

			$hitflag = 1;

			# �ѥ���ɤ�ȹ�
			&decide_key($pwd);

			# �Խ����¤�����å�
			($::ADMINFLAG) || &decide_edtlim($date) || &::error('�Խ����¤�᤮�Ƥ��ޤ�');

			# �����Ȳù�
			&mark_quote(\$::FORM{comment}) if($ini::markquote);
			&http_autolink(\$::FORM{comment}) if($ini::autolink);

			# �����ǡ��������ղ�
			my($edtcnt,$edttime) = split(/,/,$edt,2);
			$edtcnt++;
			$edttime = &get_nowdate;

			# �񤭴���
			$line = "$seri\t$number\t$date\t$::FORM{name}\t$::FORM{subj}\t$::FORM{comment}\t$::FORM{color}\t$::FORM{email}\t$::FORM{url}\t$::FORM{icon}\t" . "$edtcnt,$edttime" ."\t$ipaddr\t$pwd";
			$line =~ tr/\x0D\x0A//d;
			$line .= "\n";
		}

		print OUT $line;
	}
	($hitflag) || &::error("�Խ��оݤε�����ȯ���Ǥ��ޤ���Ǥ��� (no  $::FORM{seri})");

	undef($logobj);
	close(OUT);
	$fl->unlock;
}

# �������ַв᤹����Խ��ԲĤˡ�OK�ʤ�1���֤�
sub decide_edtlim
{
	($ini::useredit == 2) || return 1;

	my($date) = @_;
	my($year,$mon,$mday,$hour,$min,$sec) = unpack('A2xA2xA2xA2xA2xA2', $date);
	$year += 2000; $mon--;					# 2100ǯ���꤬ȯ��

	my($wtime) = main::timelocal($sec,$min,$hour,$mday,$mon,$year);
	((time - $wtime) < 60*60*48 ) || return 0;
	return 1;
}
# ���ѹԤ�ԥå����å�
sub mark_quote
{
	my($in) = @_;
	(index($$in,'|') > -1) || (index($$in,'��') > -1) || (index($$in,'&gt;') > -1) || (index($$in,'��') > -1) || return;

	my($str,$doc,$eol);
	while($$in =~ /(.*?)($|<br>)/gso  ){
		$doc = $1; $eol = $2;
		if($doc =~ /^(\||��|��|&gt;)/ ){
			$str .= "<q>$doc</q>$eol";
		}else{
			$str .= $doc . $eol;
		}
	}
	$$in = $str;
}

# ��ư���  cite:perl-memo
sub http_autolink
{
	my($in) = @_;
	(index($$in,'http://') > -1) || (index($$in,'mailto:') > -1) || return;

	my($result,$skip,$txt,$tag);
	while ($$in =~ /([^<]*)(<!(?:--[^-]*(?:(?!--)-[^-]*)*--(?:(?!--)[^>])*)*(?:>|(?!\n)$|--.*$)|<[^"'>]*(?:"[^"]*"[^"'>]*|'[^']*'[^"'>]*)*>)?/gso) {
		($1) || ($2) || last;
		$txt = $1; $tag = $2;
		if ($skip) {
			$skip = 0 if( $tag =~ /^<\/[aA](?!\w)/);
		}else{
			$txt =~ s|(s?https?://[-_.!~*'()\w;/?:@&=+\$,%#]+)|<a href="$1" target="_top">$1</a>|go;
			$txt =~ s|(mailto:[\w\.\-]+)\@([\w\.\-]+\.[\w\.\-]+)|<a href="$1\@$2">$1\@$2</a>|go;
			$skip = 1 if( $tag =~ /^<[aA](?!\w)/ );
		}
		$result .= $txt . $tag;
	}
	$$in = $result;
}
# �����μ���
sub get_nowdate
{
	$ENV{TZ} = 'JST-9';
	my($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time);
	return sprintf('%02d/%02d/%02d %02d:%02d:%02d',
					$year % 100 ,++$mon,$mday,$hour,$min,$sec);
}


# ��������¹�
sub erase
{
	# check input
	scalar(@{$::FORM{sel}}) || &::error('������뵭�������򤷤Ʋ�������');
	($::FORM{key})   || &::error('�������������ϥ��Ǥ���');
	($::ADMINFLAG) || (scalar(@{$::FORM{sel}}) == 1) || &::error('���٤�ʣ���ε����������뤳�ȤϤǤ��ޤ���');

	my $logobj = new LogReader;

	# �Ƶ��������󥿤�Ĵ��
	foreach (@{$::FORM{sel}}){
		( substr($_,0,1) eq '*' ) && $logobj->{oya_num}--;
	}

	my $fl = new FileLock;
	$fl->lock;
	open(OUT,">$fl->{out}") || die "��å����ԡ�$fl->{out}�������ԡ�";

	# �إå��񤭽Ф�
	print OUT "[ealis3],$logobj->{oya_num},$logobj->{oya_last},$logobj->{seri_last},$logobj->{lastwrite}\n";

	# �������
	my($del_num,$verify_pwd,$flag,$line,$oyaflag,$delcnt);
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd);
	while($line = $logobj->lread()) {
		$flag = 0;
		($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);

		foreach (@{$::FORM{sel}}) {
			if ($_ eq $seri) {
				($::ADMINFLAG) || &decide_edtlim($date) || &::error('�Խ����¤�᤮�Ƥ��ޤ�');
				$delcnt++;
				$flag = 1;
				$del_num = $number;
				$verify_pwd = $pwd;
				(substr($seri,0,1) eq '*') && ($oyaflag = 1);
			}elsif($oyaflag == 1 && $del_num eq $number) {
				($::ADMINFLAG) || &::error('�ֿ����դ����Ƶ����ϴ����ͤ�������Ǥ��ޤ���');
				$flag = 1;
			}
		}
		($flag) || print OUT $line;
	}
	close(IN);
	($del_num) || &::error('����оݵ��������Ĥ���ޤ���Ǥ���');
	($delcnt == scalar(@{$::FORM{sel}})) || &::error('����оݵ����Υޥå�����������ä��Τǡ�ǰ�Τ����������ߤ��ޤ�����');

	# ����¹�OK������
	&decide_key($verify_pwd);

	undef($logobj);
	close(OUT);
	$fl->unlock;
}


### -------------
## �����ɤ���إå�����
package LogReader;
sub new
{
	my($p) = {};

	open(IN,"$ini::logfile") || die "���ե������$ini::logfile�פ������ޤ���";
	$_ = scalar(<IN>);
	$p->{head} = $_;
	chomp($_);

	split(/,/,$_,5);
	(shift eq '[ealis3]') || die 'ealis �裳����Υ��ǤϤ���ޤ���';
	($p->{oya_num},$p->{oya_last},$p->{seri_last},$p->{lastwrite}) = @_;

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

### -------------
## flock&rename �ǤΥ�å�
package FileLock;
# lockfile���Ф��ƥ�å�
sub new
{
	(-f "$ini::lockfile") || die "$ini::lockfile �Ϻ�äƤ����Ƥͤ�";

	open(LOCK, "+<$ini::lockfile") || die "$ini::lockfile �������ޤ���";
	eval{ flock(LOCK, 2); };
	truncate(LOCK, 0);
	print LOCK  scalar(time) . " ($$)";

	bless {};
}
# temp�����
sub lock
{
	my($obj) = @_;

	$obj->{out} = "$ini::logdir/$$\.tmp";
	open(OUT,">$obj->{out}") || die "temporary file �������ԡ�permission����";
	close(OUT);
	chmod 0666,$obj->{out};
}
sub unlock
{
	my($obj) = @_;

	REN:{
		# temp���͡���
		rename($obj->{out},"$ini::logfile") || last REN;
		(! -f $obj->{out}) || last REN;

		close(LOCK);
		return;
	}
	&::error("��͡���˼��Ԥ��ޤ���(MS-IIS?)��<br>.tmp�Ȥ��Ƽ��Ԥ����������뤫�⤷��ޤ���<blockquote> $!</blockquote>");
}
sub DESTROY
{
	my($obj) = @_;
	(-e $obj->{out}) && unlink($obj->{out});
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
