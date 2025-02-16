#!/usr/local/bin/perl

# ealis ver.3.0   sub unit
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC ��)

use 5.004;
use vars qw[%FORM];

require './ealis_cfg.cgi';

package main;

	if(!$ENV{QUERY_STRING}){
		&print_header('�Ǽ��ĤΤĤ�������');
		&show_readme;

	}elsif($ENV{QUERY_STRING} eq 'pickcolor'){ 
		&pickcolor;
		exit;
	}elsif($ENV{QUERY_STRING} eq 'nullimg'){ 
		&out_nullimg;
		exit;

	}elsif ($ENV{QUERY_STRING} eq 'prev_ico') { 
		&print_header('�����������',1);
		&preview_icon;
	}elsif ($ENV{QUERY_STRING} eq 'prev_color') { 
		&print_header('ʸ��������',1);
		&preview_color;
	}elsif ($ENV{QUERY_STRING} =~ /^prev_colorj;/) { 
		&print_header('ʸ�������� by java',1);
		&preview_color_jscript;

	## ����
	}else{
		&print_header('��ʸ�����⡼��');

		require 'jcode.pl';

		&form_decode;
		my $pnum_cnt = &read_pcount;

		&print_findMenu($pnum_cnt);
		if($FORM{word}){
			$| = 1;
			&find_main($pnum_cnt);
		}
	}

	&print_footer;
exit;




#find-------
#�� ������Ϣ
sub read_pcount
{
	($ini::pnumfile) || return;

	open(PNUM,$ini::pnumfile) || die "��$ini::pnumfile�פ������ޤ���";
	$_ = scalar(<PNUM>);
	close(PNUM);

	return $_;
}

sub print_findMenu
{
	my($pnum_cnt) = @_;

	# �����å�����Ƥ���������
	my(@checks);
	(($FORM{cond} eq 'or') ? $checks[1] : $checks[0] ) = ' checked';

	(($FORM{zone} eq 'past') ? $checks[4] 
	 : ($FORM{zone} eq 'all') ? $checks[5] 
	 : $checks[2] ) = ' checked';

	if(!$FORM{word} || $FORM{caps}){ $checks[6] = ' checked';}
	$value = $FORM{word};
	$value =~ s/</&lt\;/go;
	$value =~ s/>/&gt\;/go;
	$value =~ s/"/&quot;/go;
	$value =~ s/'/&#39;/go;

	print <<"EOD";
<script type="text/javascript" defer><!--
	function fm_reset(){
		self.document.query.word.value = '';
		self.document.query.cond[0].checked = true;
		if(self.document.query.zone[0]) self.document.query.zone[0].checked = true;
		self.document.query.caps.checked = true;
	}
// --></script>

<form action="$ini::scriptsub?find" method=POST name="query">
<fieldset class="findform">
	<legend accesskey=F>���������ե�����</legend>
	<p>����������<strong>�������</strong>�����Ϥ��������ΰ�����򤷤ơָ����ܥ���פ򲡤��Ƥ���������</p>
	<p>������ɡ� <input type=text name="word" size=30 value="$value" accesskey=Q class="in"></p>
	<p>�������
		<input type=radio name="cond" value="and"$checks[0] accesskey=A>���Ƥθ��ޤࡡ
		<input type=radio name="cond" value="or"$checks[1] accesskey=O>�����줫�θ��ޤࡡ
		<input type=checkbox name="caps" value="TRUE"$checks[6]>Caps��Ʊ��뤷�ʤ��ʹ�®��
	</p>

	<p>�����ϰ�
		<input type=radio name="zone" value="now"$checks[2]>���ԥ���
	@{[ ($pnum_cnt)
		 ?	qq!\t<input type=radio name="zone" value="past"$checks[4]>����(#$pnum_cnt)��\n!
			 . qq!\t\t<input type=radio name="zone" value="all"$checks[5]>���ƤΥ�\n!
		 : undef ]}
	</p>
	<div class="valueinput">
		<input type=submit value="��������">
		<input type=button onclick="javascript:fm_reset()" onkeypress ="javascript:fm_reset()" value="���ꥢ">
	</div>
</fieldset>
</form>
EOD
}

## ��������ºݤθ���ʬ��
sub find_main
{
	my($pnum_cnt) = @_;

	# �ҥå�Ƚ��obj
	my $findkey = new FindKeyword \%FORM;

	# ���ԥ��ˤĤ��Ƹ���
	if($FORM{zone} eq 'all' || $FORM{zone} eq 'now'){
		print "<h2>���ԥ��������</h2>\n";
		print qq!<div class="article">\n<ol class="findresult">\n!;
		&find_nowLog($findkey);
		print "</ol></div>\n";
	}

	# �����ˤĤ��Ƹ���
	if($FORM{zone} eq 'all' || $FORM{zone} eq 'past'){
		print "<h2>�����������</h2>\n";
		while($pnum_cnt >= 1 ) {
			&find_pastLog($findkey,$pnum_cnt);
			$pnum_cnt--;
		}
	}
}


## ���ԥ�����θ����롼����
sub find_nowLog
{
	my($findkey) = @_;

	# �ե�������ɤ߹���
	open(DB,"$ini::logfile") || die "��$ini::logfile�פ������ޤ���";
	scalar(<DB>);	#�إå����ڤ�

	# ��������
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd);
	my($line);
	while ($line = <DB>) {
		$findkey->decide(\$line) || next;

		($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);

		$subj = (substr($seri,0,1) eq '-') ? '��<small>response</small>' : ($subj || '(̵��)') ;
		$name = qq!<a href="mailto:$email">$name</a>! if($email);
		($url) &&= qq!��<a href="http://$url" target="_top">http://$url</a>!;

		# ��̤�ɽ��
		print qq!\t<li><h3><span class="atclno"><a href="$ini::scriptmain?pick=$number">$number</a></span>:\n!;
		print qq!\t <em class="subj">$subj</em>����<cite>$name</cite>��<span class="stamp">on $date $url </span></h3>\n!;
		print qq!\t<p style="color:$color">$comment</p>��\n\n!;
	}
	close(DB);
}

## ��������θ����롼����
sub find_pastLog
{
	my($findkey,$pastno) = @_;

	unless(-e "$ini::pastdir/$pastno\.html"){
		print "<h3>��$ini::pastdir/$pastno\.html�פ������ޤ���Ǥ���</h3>\n";
		return;
	}

	# �����ե�������ɤ߹���
	open(DB,"$ini::pastdir/$pastno\.html") || die "���� $ini::pastdir/$pastno\.html ��¸�ߤ��ʤ�";

	# seek <body>
	while (index(scalar(<DB>),'<body') < 0) { ; }

	my $http_this = ($ini::pasthttp || "$ini::pastdir/") . $pastno . '.html';

	my($flag,$line);
	while ($line = <DB>) {
		$findkey->decide(\$line) || next;

		# ���к�
		$line =~ s!<div class="atclbody">!!og;
		if( index($line,' class="msghere"') > -1 ){
			$line =~ s!<span class="atclno"><a href="\?#msg([0-9]+)" class="msghere">([0-9]+)</a></span>!<span class="atclno"><a href="$http_this?#msg$1" class="msghere">$2</a></span>!;
		}


		# for ver.2.x
		$line =~ s!<blockquote>|</blockquote></dl>!!og;
		$line =~ s!</blockquote><dl>$!!og;
		
		$line =~ s!^\t<dd>!!og;
		$line =~ s!</dd>$!!og;
		$line =~ s!\t<li>!!og;
		
		$line .= '</div>' if($line =~ s!</div><font!</div><div class="doc"><font!og); # ����ä��԰�

		# ���ƤΥҥåȤʤ饤��ǥ�������
		if(!$flag){
			$flag = 1;
			print qq!\n<hr class="atclhr">\n\n<div class="article">\n!;
			printf qq!<h2>����<a href="%s%d\.html">No.%d</a>�θ������</h2>\n!,
						($ini::pasthttp || "$ini::pastdir/"), $pastno, $pastno;
			print "<ol>\n";
		}

		print "\t<li>" unless($line =~ /^\t+<li/);
		print $line;
		if(index($line,'<div class="atclbody">') > -1){
			print "</div>\n";
		}
	}
	close(DB);
	print "</ol></div>\n" if($flag);
}



###---------
#�� �Ǽ��ĤλȤ���
sub show_readme
{
	print <<"EOM";
<div class="infobox">
	<h3>���Ĥ�ɽ���⡼�ɤ���äƤ��ޤ�</h3>
	<ul>
		<li><strong>Normal Mode</strong><br>
			�̾�Ϥ��Υ⡼�ɤǻ��Ѥ���Ȼפ��ޤ���</li>
		<li><strong>DynamicHTML Mode</strong> <em>(after MSIE 4.x,Mozilla/Gecko)</em><br>
			�ֿ����Ф�����Ǥ���Τ�ɽ�������ä��ꤷ�Ƥ��ޤ���<br>
			����������礭����äƤ���Τ�Ĺʸ�����Ϥ��䤹���Ǥ���</li>
		<li><strong>Thread View</strong><br>
			�Ƶ�������Ƭ����ʬ�Τߤ�ɽ�����ޤ����ֿ�������ˤʤä��Ȥ��˸��Ϥ��������ޤ���</li>
		<li><strong>Lapse View</strong><br>
			ȯ�����������ɽ�����ޤ����Ƶ������ֿ��������硣</li>
	</ul>
	<h3>�񤭹��߻��������</h3>
	<ul>
		<li>��������Ƥ����Ǥ�ɬ�����Ϲ��ܤ�<strong>Name</strong>��<strong>����</strong>�Ǥ���</li>
		<li>�����ˤϡ�<strong>Ⱦ�ѥ��ʤϰ��ڻ��Ѥ��ʤ��ǲ�������</strong>ʸ�������θ����Ȥʤ�ޤ���</li>
		<li>��ƻ���<strong>��������</strong>�ʱѿ�����8ʸ������ˤ�����Ƥ����ȡ����ε����ϼ��󵭻������ˤ�ä�<strong>���</strong>���뤳�Ȥ��Ǥ��ޤ���</li>
		<li>�������ݻ������<strong>���� $ini::logmax ��</strong>�Ǥ��������Ķ����ȸŤ����<strong>@{[ $ini::pnumfile ? '�����˰�ư' : '��ư���' ]}</strong>����ޤ���</li>
		<li>�����Ԥ������������פ�Ƚ�Ǥ��뵭����¾�ͤ�����������뵭����ͽ��ʤ�������뤳�Ȥ�����ޤ���</li>
	</ul>
	<h3>Tips</h3>
	<ul>
		<li>�ֿ��ե�����ο��������<strong>��</strong>�����򤹤�ȹ�����ʸ���������Ǥ��ޤ���<br>
			�����ʥ����ɤǤ⥫�顼̾��hotpink,whitesmoke�ʤɡˤǤ����ϲ�ǽ�Ǥ���<br>
			�ޤ����ٻ��ꤹ��ȥ��å������졢<strong>��</strong>�ǥ��å���������ʸ��������ѤǤ��ޤ���</li>
		<li>JavaScript��ͭ���ʾ�硢<strong>&lt;color&gt;</strong>�ܥ���ϵ����ץ�ӥ塼���ͤƤ��ޤ��������Ѳ�������</li>
		<li>�ʲ���accesskey�����ꤵ��Ƥ��ޤ���
			<ul>
				<li><strong>Alt + I</strong>:����ǽ��˥塼</li>
				<li><strong>Alt + N</strong>:��������ƥե�����</li>
				<li><strong>Alt + [0-9]</strong>:������ܤ��ֿ��ե�����</li>
				<li><strong>Alt + M</strong>:��View Mode</li>
				<li><strong>Alt + P</strong>:��Log Pager</li>
			</ul></li>
	</ul>
</div>
EOM
}

#�� �����򥦥���ɥ� 
sub pickcolor
{
#	print "Last-Modified: Sat, 31 Sep 2002 14:41:00 GMT\n";
	print "Pragma: no-cache\n";
	print "Content-type: text/html; charset=euc-jp\n\n";
	print <<'EOD',
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
<meta http-equiv="content-type" content="text/html; charset=euc-jp">
<meta http-equiv="content-style-type" content="text/css">
<meta http-equiv="content-script-type" content="text/javascript">
<title>ealis color manager</title>
<script type="text/javascript">

var hexChars = "0123456789ABCDEF";
var mode = getCookie();
var cpos;

function getCookie(){
	cpos = document.cookie.indexOf('EALISCOL=');
	if( cpos >= 0 ){
		return document.cookie.substr(cpos+9 ,1);
	}else{
		return -1;
	}
}

function Dec2Hex (Dec){
	var a = Dec % 16;
	var b = (Dec - a)/16;
	return hexChars.charAt(b) + hexChars.charAt(a);
}

function setColor(hexColor){
	document.forms[0].COLOR.value = hexColor;
	document.fgColor = "#" + hexColor;
	document.bgColor = "#" + hexColor;
	if( window.opener.document.forms[0].color2 ){
		for (i=0; i < window.opener.document.forms.length; i++){
			window.opener.document.forms[i].color2.value = "#" + hexColor;
		}
	}
}

// �ͥ��ƥå�,����Υ�����,�ѥ����󳫻�,��λ
function printColorMap(divid,imgsize,start,end){
	var red, blue, green, colorCode;
	var irohaba = Math.floor(256/ (divid -1));
	document.writeln("<table border=0 cellspacing=1 cellpadding=0>");
	for (red=0; red<256; red+=irohaba){
		document.writeln("<tr>");
		for (green=start; green<end; green+=irohaba){
			for (blue=0; blue<256; blue+=irohaba){
				colorCode = Dec2Hex(red) + Dec2Hex(green) + Dec2Hex(blue);
				document.writeln("<td bgcolor=\"#" + colorCode + "\">");
				document.writeln("<a href=\"javascript:setColor('" + colorCode + "')\" BORDER=0>");
				document.writeln("<img src='?nullimg' width=" + imgsize + " height=11 border=0></A></TD>");
			}
		}
	}
	document.writeln("</table>");
}
function changeLst(num){
	document.cookie = 'EALISCOL=' + num;
	location.reload();
}
function writeList(){
	var i;
	for (i=0; i<=3; i++){
		document.write('<option value=' , i);
		if( i == mode) document.write(' selected');
		document.write('>');

		if( i == 1){
			document.write('8x8x8 = 512');
		}else if( i == 2){
			document.write('10x10x10 = 1000');
		}else if( i == 3){
			document.write('12x12x12 = 1728');
		}else{
			document.write('Win&Mac���� 6x6x6=126');
		}
	}
}
</script></head>

<body style="margin-top:0">
<form action="javascript:">

<div style="font:10pt Verdana,sans-serif; background: #E6F2F2; color:#333;">
	ealis color manager��
	<select name="pal" style="font-size:9pt; position:absolute; top:0; right:1px;" onchange="changeLst(this.value);">
		<script type="text/javascript">
		writeList();
		</script>
	</select>
</div>

<table border=1 cellpadding=4 cellspacing=0 bgcolor="white" align=center>
	<tr><td align=middle style="font-size: 9pt;">
	<div class="date">����<strong>value:</strong> <big>#</big>
		<input name="COLOR" maxlength=6 size=9 type=text onChange="setColor(this.value);" style="ime-mode:disabled">
		����ư���ϻ���Tab�ǳ���</div>

		<script type="text/javascript">
		if(mode == 1){
			printColorMap(8,7,0,128);
			printColorMap(8,7,128,256);
		}else if(mode == 2){
			printColorMap(10,6,0,128);
			printColorMap(10,6,128,256);
		}else if(mode == 3){
			printColorMap(12,6,0,128);
			printColorMap(12,6,128,256);
		}else{
			printColorMap(6,8,0,256);
		}
		// for debug
//		if(mode == -1) document.writeln('no cookie');
//		document.writeln(document.cookie,"<br>cpos:", cpos,"<br>selected:", mode);
		</script>
	</td></tr>
</table>
</form>
</body></html>
EOD
}

# Ʃ����1x1��gif
sub out_nullimg
{
	print "Last-Modified: Sat, 28 Apr 2001 15:52:09 GMT\n";
	print "Content-type: image/gif\n\n";
	print pack('H*', '4749463839610100010080000000000000000021F90403000000002C00000000010001000002024401003B');
}


###---------
#�� HTML�Υإå���
sub print_header
{
	my($title,$noshow) = @_;

	print "Content-type: text/html; charset=euc-jp\n\n";
	print qq!<\!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n!;
	print qq!<html lang="ja">\n<head>\n!;
	print qq!\t<meta http-equiv="content-style-type" content="text/css">\n!;
	print qq!\t<meta http-equiv="Content-Script-Type" content="text/javascript">\n!;
	print qq!\t<meta http-equiv="pragma" content="no-cache">\n!;
	print qq!\t<meta name="robots" content="NOINDEX, NOFOLLOW">\n!;
	print qq!\t<link rel="stylesheet" type="text/css" href="$ini::cssfile" media="screen,projection">\n!;
	print qq!\t<link rel="index" href="$ini::scriptmain?">\n!;
	print qq!\t<link rel="start" href="$ini::backurl">\n!;
	print qq!\t<link rel="help" href="$ini::scriptsub">\n!;
	print qq!\t<title>$ini::title - $title</title>\n</head>\n!;
	print "<body>\n\n";

	print "<h1 class=\"sub\">$title</h1>\n\n";

	if(!$noshow){
		print "<div class=\"menubox\"><p>";
		print "<a href=\"$ini::scriptmain?\" accesskey=I>Normal</a>";
		print " <a href=\"$ini::scriptmain?dhtml\" accesskey=I>DynamicHTML</a>";
		print " <a href=\"$ini::scriptmain?thread\" accesskey=I>Thread</a>";
		print " <a href=\"$ini::scriptmain?lapse\" accesskey=I>Lapse</a>";
		print "</p><hr class=\"section\"></div>\n\n\n";
	}
}
sub print_footer
{
	print "\n\n<hr class=\"section\">$ini::footcom\n";
	print "<address> - ealis - </address>\n</body></html>\n";
}

## �ե�����ǥ�����
sub form_decode
{
	my $buf;
	read(STDIN, $buf, $ENV{CONTENT_LENGTH});

	my($name, $value);
	foreach ( split(/[&;]/,"$buf;$ENV{QUERY_STRING}") ) {
		($name, $value) = split(/=/, $_,2);
		$value =~ tr/+/ /;
		$value =~ s/%(..)/pack('H2',$1)/eg;
		$FORM{$name} = &jcode::euc($value);
	}
}




###---------
#�� �ץ�ӥ塼��ǽ
sub preview_color
{
	my $arr = \@Sozai::colpalet;

	print qq!<div class="article" id="preview_color"><div class="atclbody">\n<table border=0 class="preview">\n!;

	for ($_ = 0; $_ < scalar(@{$arr}); $_ +=2) {
		print "<tr>\n" if($_ % 4 == 0);
		(substr($arr->[$_],0,1) ne '*') || next;
		print "\t<th>$arr->[$_+1]</th>\n";
		printf qq!\t<td style="padding-right:1em; color:%s">%s</td>\n!,
				$arr->[$_],
				'�ä������Ե������ɤ��������ɤ�������<br>���ε֤�ۤ��������������Ѥ�餺���ĤޤǤ�<br>����ľ�����ͤ����Ϥ���褦��<br>�錄�ĤߤΤ褦�ʶ��������褭�ä�';
	}

	print "</table>\n</div></div>\n";
}

sub preview_color_jscript
{
	my $arr = \@Sozai::colpalet;
	my($formnum) = (split(/;/,$ENV{QUERY_STRING}))[1] || 0;

	print qq!<div class="article" id="preview_colorj"><div class="atclbody">\n!;
	print qq!<script type="text/javascript">\n!;
	print qq! var showText;\n!;
	print qq! if(window.opener.document.forms[$formnum].comment.value){ \n!;
	print qq!  showText = window.opener.document.forms[$formnum].comment.value;\n!;
	print qq!  showText = showText.replace("\\r\\n","<br>");\n!;
	print qq!  showText = showText.replace("\\r","<br>");\n!;
	print qq!  showText = showText.replace("\\n","<br>");\n!;
	print qq! }else{\n!;
	print qq!  showText = "�ä������Ե������ɤ��������ɤ�������<br>���ε֤�ۤ��������������Ѥ�餺���ĤޤǤ�<br>����ľ�����ͤ����Ϥ���褦��<br>�錄�ĤߤΤ褦�ʶ��������褭�ä�";\n!;
	print qq! }\n!;

	print " var opt_col = window.opener.document.forms[$formnum].color2.value\n";
	print " var col_code = new Array(opt_col,";

	my($i);
	for ($i=0 ; $i<=($#{$arr}); $i++ ) {
		print "," unless($i == 0);
		print "'$arr->[$i]'" if($arr->[$_]);
		$i++;
	}
	print ");\n";

	print " var col_name = new Array(opt_col,";
	for ($i=0 ; $i<=($#{$arr}); $i++ ) {
		print "," unless($i == 0);
		$i++;
		print "'$arr->[$i]'" if($arr->[$_]);
	}
	print ");\n\n";

	printf " for(i=0; i<=%d; i++){\n" , scalar(@{$arr})/2;
	## col��rand�����к�
	print q!  document.writeln("<p><a href=\"javascript:setCol('" + col_code[i] + "')\">" + col_name[i] + '</a>����');! . "\n";
	print qq!  document.writeln('<span style="color:'+ col_code[i] + '">' + showText + '</span></p>');\n!;
	print qq! }\n\n!;

	print qq! function setCol(hexColor){\n!;
	print qq!	for (i=0; i < window.opener.document.forms.length; i++){\n!;
	print qq!		window.opener.document.forms[i].color2.value = hexColor;\n!;
	print qq!	}\n!;
	print qq! }\n!;
	print qq!</script>\n!;
	print qq!</div></div>\n!;
}
sub preview_icon
{
	my $arr = \@Sozai::icopalet;
	print qq!<div class="article" id="preview_icon">\n!;

	my($i,$j,$tflag);
	for ($i = 0; $i < scalar(@{$arr}); $i +=2) {
		if(substr($arr->[$i],0,1) eq '*'){
			if($arr->[$i] eq '**'){
				print qq!</table></div>\n\n! if($j);
				print "<h3><em>$arr->[$i+1]</em></h3>\n";
				print qq!<div class="atclbody"><table border=0 class="preview">\n!;
				$j = 0; $tflag=1;
			}
		}else{
			if(!$tflag){
				print qq!<div class="atclbody"><table border=0 class="preview">! ;
				$tflag = 1;
			}
			print "<tr>\n" if($j % 4 == 0);
			print qq!\t<td style="width:20%; text-align:center">!;
			print qq!<img src="$ini::imgpath$arr->[$i]" alt="$arr->[$i]"><br>$arr->[$i+1]</td>\n!;
			$j++;
		}
	}
	print "</table></div>\n</div>\n";
}



###---------
#�� �������Ƚ��
package FindKeyword;
sub new
{
	shift;
	my $form = shift;

	my($p) = {};
	$p->{cond} = $form->{cond};
	$p->{caps} = $form->{caps};

	# �������Ƥ�ò�
	my($word) = $form->{word};
	$word =~ s'<'&lt;'go;
	$word =~ s'>'&gt;'go;
	$word =~ s'��' 'go;
	$word =~ s'\t' 'go;
	@{ $p->{words} } = split(/\s/,$word);

	bless $p;
}
sub decide
{
	my($obj,$line) = @_;

	my($result,$query);
	foreach $query (@{ $obj->{words} }){
		# Ƚ����
		$result = 0;
		HIT:{
			if($obj->{caps}) {
				(index($$line, $query) > -1) || last HIT;
				($$line =~ /\G((?:[\x00-\x7F]|[\x8E\xA1-\xFE][\xA1-\xFE]|\x8F[\xA1-\xFE][\xA1-\xFE])*?)$query/io ) || last HIT;
				$result = 1;
			}else{
				($$line =~ /\G((?:[\x00-\x7F]|[\x8E\xA1-\xFE][\xA1-\xFE]|\x8F[\xA1-\xFE][\xA1-\xFE])*?)$query/io ) || last HIT;
				$result = 1;
			}
		}

		# and/or��ʬ
		if($result && $obj->{cond} eq 'or'){ return 1; }
		elsif(!$result && $obj->{cond} eq 'and'){ return 0; }
	}
	return ($obj->{cond} eq 'and') ? 1 : 0;
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
