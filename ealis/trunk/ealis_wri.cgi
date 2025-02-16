#!/usr/local/bin/perl

# ealis ver.3.0   write unit
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC ��)

use 5.004;
use Fcntl qw[:flock];
use vars qw[%FORM];

require 'jcode.pl';
require './ealis_cfg.cgi';
require $ini::leteng;

package main;

	&form_decode;
	&check_input;

	&set_cookie if(!defined($FORM{chtm}));
	&writelog;

	if($ini::plug_mail){
		require "$ini::plug_mail";
		&PlugMail::send(\%FORM);
	}

	&http_locate;
exit;


### -------------
## �����
sub writelog
{
	# ���򳫤�
	my $logobj = new LogReader;

	# ����������
	my $fl = new FileLock;
	$fl->lock;

	open(OUT,">$fl->{out}") || die "��å����ԡ�$fl->{out}�������ԡ�";
	print OUT &new_header($logobj);

	## �Ƶ����ΤȤ�
	if (!$FORM{resno}) {
		print OUT &new_message($logobj);

		my($line,$i,$j,$plog);
		while ($line = $logobj->lread()) {
			$j++;
			# ����οƵ����򥫥����
			if(substr($line,0,1) eq '*') { 
				$i++;
				# ���Կ���1000��Ķ�������ˤʤä��鵭�����³���
				($ini::logmax) && ($j > 900) && ($ini::logmax = 0);
			}
			&parse_line(\$line,undef);

			# ���ԥ��˻Ĥ�ʬ
			if($i < $ini::logmax){
				print OUT $line;
				next;
			}
			($ini::pnumfile) || last;

			# ��������
			($plog) ||= new PastLog \%FORM;
			$plog->pwrite($line);
		}

	## �쥹�����ʥ����ȡˤΤȤ�
	} elsif ($ini::res_sort) {
		# Ʊ������No.����Ŀ�/�쥹���������
		my($line,$flag);
		while ($line = $logobj->lread()) {
			if(&parse_line(\$line,$FORM{resno})){
				$flag = 1;
				print OUT $line;
			}elsif($flag){
				last;
			}
		}
		($flag) || &error("�ֿ��ֹ�($FORM{resno})���ޥå����ޤ���Ǥ���");

		print OUT &new_message($logobj);

		# ����ʳ������
		$logobj->seektop(); # ��Ƭ�˥ݥ��󥿤��᤹
		while ( $_ = $logobj->lread() ) {
			(index($_,"\t$FORM{resno}\t") == 4 ) || print OUT $_;
		}


	## �쥹�����ΤȤ�
	} else {
		my($line,$i);
		while ($line = $logobj->lread()) {
			unless($i == 2){
				if (&parse_line(\$line,$FORM{resno})) {
					$i = 1;
				}elsif ($i) {
					print OUT &new_message($logobj);
					$i = 2;
				}
			}else{
				&parse_line(\$line,undef);
			}
			print OUT $line;
		}
		if($i == 0){ &error("�ֿ��ֹ�($FORM{resno})���ޥå����ޤ���Ǥ���"); }
		elsif($i == 1){ print OUT &new_message($logobj); }
	}

	undef($logobj);
	close(OUT);
	$fl->unlock;
}

# �����Ƥ�����å���resno��hit�����true���֤�
sub parse_line
{
	my($pline,$resno) = @_;

	if( index($$pline,"\t$FORM{comment}\t") > -1 ){
		my(@parse) = split("\t",$$pline,8);
		($FORM{name} ne $parse[3]) || ($FORM{comment} ne $parse[5]) || ($FORM{color} ne $parse[6])  || &error('�����Ƥ��Ȼפ��ޤ�');
		($parse[1] eq $resno) && return(1);
	}else{
		($resno && index($$pline,"\t$resno\t") == 4 ) && return(1);
	}
}

## �إå�����ե����ޥå�
sub new_header
{
	my($logobj) = @_;

	# �Ƶ����ξ�硢�������򥫥���ȥ��å�
	if(!$FORM{resno}){
		$logobj->{oya_last}++;
		if($logobj->{oya_num} < $ini::logmax){ $logobj->{oya_num}++; }
		elsif($logobj->{oya_num} > $ini::logmax){ $logobj->{oya_num} = $ini::logmax; }	# ¿��ʬ�ϥ�����ä���
	}

	# �ǽ��������ꥢ���û� ��ɬ�������
	$logobj->{seri_last} = sprintf '%03d', (++$logobj->{seri_last})%1000;

	my($header);
	$header = "[ealis3],$logobj->{oya_num},$logobj->{oya_last},$logobj->{seri_last},$FORM{nowdate} $FORM{name}";
	$header =~ tr/\x0D\x0A//d;

	return "$header\n";
}

# ����������ե����ޥå�
sub new_message
{
	my($logobj) = @_;

	# �ۥ���̾�����
	my($hostname) = $ENV{REMOTE_HOST};
	if( !$hostname || $hostname eq $ENV{REMOTE_ADDR}) {
		$hostname = gethostbyaddr(pack('C4',split(/\./,$ENV{REMOTE_ADDR})),2) || $ENV{REMOTE_ADDR};
	}

	# pwd�Ź沽
	&crypt_delkey(\$FORM{pwd})  if($FORM{pwd});

	# ��ʸ��ù�
	&mark_quote(\$FORM{comment}) if($ini::markquote);
	&http_autolink(\$FORM{comment}) if($ini::autolink);

	# �����������������
	if($FORM{icon} eq '*RAND*'){
		my $key;
		RND:{
			$key = int(rand(scalar(@Sozai::icopalet) /2)) *2;
			(substr((@Sozai::icopalet)[$key],0,1) ne '*') || redo RND;
			$FORM{icon} = (@Sozai::icopalet)[$key];
			$FORM{icon} || die 'CFG icon miss';
		}
	}

	my($new_msg);
	$new_msg  = (($FORM{resno}) ? '-' : '*');		# ��/��Ƚ�̥ޡ�����
	$new_msg .= "$logobj->{seri_last}\t";						# �������ꥢ��
	$new_msg .= (($FORM{resno}) ? $FORM{resno} : $logobj->{oya_last});	# �������ֹ�
	$new_msg .= "\t$FORM{nowdate}\t$FORM{name}\t$FORM{subj}\t$FORM{comment}\t$FORM{color}\t$FORM{email}\t$FORM{url}\t$FORM{icon}\t\t$hostname\t$FORM{pwd}";

	$new_msg =~ tr/\x0D\x0A//d;

	return "$new_msg\n";
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

# ���������Ź沽
sub crypt_delkey
{
	my($pstr) = @_;

	my($now) = time;
	my($p1, $p2) = unpack('C2', $now);
	my($temp) = $now / (60*60*24*7) + $p1 + $p2 - 8;
	my(@saltset) = ('a'..'z','A'..'Z','0'..'9','.','/');
	my($nsalt) = $saltset[$temp % 64] . $saltset[$now % 64];

	$$pstr = crypt($$pstr,$nsalt);
}

## ���å�����ȯ�� ------
#�� http�إå���ȯ��
sub set_cookie
{
	my($secg,$ming,$hourg,$mdayg,$mong,$yearg,$wdayg) = gmtime(time + 60*24*60*60);
	my($date_gmt) = sprintf '%s, %02d-%s-%04d %02d:%02d:%02d GMT',
		('Sun','Mon','Tue','Wed', 'Thu','Fri','Sat')[$wdayg],$mdayg,
		('Jan','Feb','Mar','Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov','Dec')[$mong],
		$yearg +1900,$hourg,$ming,$secg;

	my $cookie = &gene_cookdata;
	$cookie =~ s/(\W)/'%' . unpack('H2',$1)/eg;

	print "P3P: CP='ONLi COM CUR OUR'\n";
	print "Set-Cookie: EALIS=$cookie; expires=$date_gmt;\n";
}
# cookie��body��Ĥ���
sub gene_cookdata
{
	my($hash) = {};

	# �����ͤ����Ϥ���Ƥ����ɬ��cook
	foreach (qw[email url icon]){
		$hash->{$_} = $FORM{$_};
	}

	# �����ͤ�res�����䴰
	HOKAN:{
		($FORM{resno}) || last HOKAN;

		# �ɤ��ͤ�Ѿ����뤫leteng���䤤��碌
		(@leteng_contains != () ) || last HOKAN;

		# http-cook����
		my($key,$cookstr,$value);
		GCOOK:{
			foreach ( split(/;/,$ENV{QUERY_STRING}) ) {
				($key,$cookstr) = split(/=/, $_,2);
				$key =~ tr/ //d;
				if($key eq 'EALIS'){
					last GCOOK;
				};
			}
			last HOKAN;
		}

		$cookstr =~ s/%(..)/pack('H2',$1)/eg;
		foreach ( split(/,/,$cookstr) ) {
			@_ = split(/:/, $_,2);
			$hash->{ shift() } = shift;
		}

		# leteng_contains�ǻ��ꤵ�줿�Τ�õ�
		foreach (@leteng_contains){
			$hash->{$_} = undef;
		}
	}

	return "name:$FORM{name},email:$hash->{email},url:$hash->{url},pwd:$FORM{pwd},color:$FORM{color},icon:$hash->{icon}";
}

##---------
#�� �ե��������
sub form_decode
{
	foreach(@ini::deniedaddrs){
		if($ENV{REMOTE_ADDR} =~ /^$_/ && length($_) > 4 ){
			print "Status: 204\n\n";
			exit;
		}
	}
	($ENV{CONTENT_LENGTH} < 51200) || &error('��ƥǡ������礭�����ޤ���');

	# form decode
	my($buf,$name, $value);
	read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	($buf) || &error("�����ƤӽФ����ѤǤ���<a href=\" $ini::scriptmain\">������إ�������</a>��");

	foreach ($ENV{QUERY_STRING}, $buf){
		foreach ( split(/[&;]/,$_) ) {
			($name, $value) = split(/=/, $_,2);
			$value =~ tr/+/ /;
			$value =~ s/%(..)/pack('H2',$1)/eg;
			$value =~ s/\t/    /og;
			# ;��̵���Τ�&�Ϥ�������
			$value =~ s/&/&amp;/og if(index($value,';') < 0);

			unless($ini::allowtag && $name eq 'comment') {
				$value =~ s/</&lt\;/go;
				$value =~ s/>/&gt\;/go;
				$value =~ s/"/&quot;/go;
				$value =~ s/'/&#39;/go;
			}else{
				(index($value,'<!--#') < 0 ) || &error('SSI�����ػ�');  #-->
			}

			$FORM{$name} = &jcode::euc($value) || '';
		}
	}
}
#�� �񤭹�������
sub check_input
{
	# �����μ���
	$ENV{TZ} = 'JST-9';
	my($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time);
	$FORM{nowdate} = sprintf('%02d/%02d/%02d %02d:%02d:%02d',
					$year % 100 ,++$mon,$mday,$hour,$min,$sec);

	# cgi-dir��path�����
	$ini::locate ||= sprintf 'http://%s%s/',  $ENV{SERVER_NAME},
					substr($ENV{SCRIPT_NAME}, 0, rindex($ENV{SCRIPT_NAME},'/') );

	# ¾�����Ȥ���Υ����������ӽ�
	if($ini::refcheck) {
		my($ref_url) = $ENV{HTTP_REFERER};
		$ref_url =~ s/\?(.|\n)*//ig;
		$ref_url =~ s'%7E'~'igo;
		(index($ref_url, $ini::locate ) > -1) || &error("�����ʥ��������Ǥ���</p><p>ref:$ref_url<br>allow:$ini::locate");
	}

	# ���Ϲ��ܤΥ����å�
	($FORM{name})    || &error('̾�������Ϥ���Ƥ��ޤ���');
	($FORM{comment}) || &error('������ʸ�����Ϥ���Ƥ��ޤ���');
	($FORM{url} && $FORM{url} !~ s!^http://!!) && &error('����������ޤ��󤬡�http://�ʳ��Υ������ޤˤ��б����Ƥ��ޤ���');

	# �������Ȥ��ӽ�
	(index($FORM{icon},'/') < 0 ) || &error('��������ꥹ�Ȥ������Ǥ�');
	($FORM{icon} ne '*') || &error('����������������������롼�׸��Ф��ˤʤäƤޤ�');

	# color������ɬ��
	if($FORM{color}){
		;
	}elsif($FORM{color2} && $FORM{color2} ne '#') {
		$FORM{color} = $FORM{color2};
	}else{
		# �桼���������Ϥ�����
		&input_color; exit;
	}

	# �ͤ򥨥󥳡���
	if ($ini::allowtag){
		if(index($FORM{comment},'<') < 0){
			# <���ʤ��Τ�>��������ϰ��Ѥȸ��ʤ�
			$FORM{comment} =~ s'>'&gt;'g;
		}else{
			$FORM{comment} =~ s/^>/&gt;/g;
			$FORM{comment} =~ s/<br>>/<br>&gt;/g;
		}
	}elsif ($ini::plug_grad){
		# <gd>�ϵ���
		$FORM{comment} =~ s'&lt;gd&gt;'<gd>'ig;
		$FORM{comment} =~ s'&lt;/gd&gt;'</gd>'ig;
	}
	$FORM{comment} =~ s/\x0D\x0A/<br>/og;
	$FORM{comment} =~ s/\x0D/<br>/og;
	$FORM{comment} =~ s/\x0A/<br>/og;
}

## ���顼�����ɤ����Ϥ�����
sub input_color
{
	defined($FORM{chtm}) && &error('���顼��������­');

	&header;
	$ENV{QUERY_STRING} =~ s'&'&amp;'og;

	print <<"EOM";
<script TYPE="text/javascript" defer><!--
	function chk(col){ document.forms[0].color2.value = col; }
	function colsel() { window.open('$ini::scriptsub?pickcolor','colsel','scrollbars=no,status=no,height=160,width=370'); }
--></script>

<h1 class="main">$ini::h1</h1>
<div class="menubox"><p><a href="javascript:history.go(-1)" accesskey=I>����äѤ�᤿</a></p><hr></div>


<form action="$ini::scriptwri?$ENV{QUERY_STRING}" accept-charset="euc-jp" method="POST">
<div class="infobox">
	<h3>�� ���顼����������ե�����</h3>
	<p class="msg-oya">���ε����ο��򲿿��ˤ��뤫�����Ʋ����������󤫤��cookie�������Ϥ��ʤ��ޤ���<br>
	�������ʥ����ɤǤ⥫�顼̾�Ǥ��hotpink,whitesmoke�ʤɡ����ϲ�ǽ�Ǥ�</p>

	<p class="msg-oya">
		Name <input type=text name="name" value="$FORM{name}" size=20 class="in"><br>
        <input type="hidden" name="pwd" value="$FORM{pwd}">
		<textarea name="comment" cols="70" rows=3  wrap="soft">$FORM{comment}</textarea><br>
		��<a href="javascript:colsel()">��������ߤ�</a>
		<input type=text name="color2" size=11 value="#" class="in" style="ime-mode:disabled">
		<input type=submit value="����Ǥ���"><br><br>
EOM

	my $arr = \@Sozai::colpalet;
	for ($_ = 0; $_ < scalar(@{$arr}); $_ +=2) {
		print (($arr->[$_]) ? 
			qq!\t\t\t<input type=radio onclick="chk('$arr->[$_]')"><span style="color:$arr->[$_]">��</span>\n!
			:'<br>' );
	}

	# textbox��ɽ������ʪ�ʳ��ϡ�hidden������
	my($name, $value);
	while (($name, $value) = each(%{$obj})) {
		($name ne 'name' && $name ne 'email' && $name ne 'comment' &&
		   $name ne 'color' && $name ne 'color2' && $name ne 'resno') || next;

		print qq!\t\t<input type=hidden name="$name" value="$value">\n!;
	}

	print qq!\t</p>\n</div>\n</form>\n!;

	print qq!\n<hr class="section">\n\n!;
	print "$ini::footcom</body>\n</html>\n";
}

# ��Ƶ����򼺤�ʤ��褦��%FORM�򥲥�
sub form_dump
{
	print "<h2>form�����</h2>\n";
	print "<div class=\"infobox\"><blockquote><dl>";
	my($key);
	foreach $key (sort %{$obj}) {
		($FORM{$key}) || next;
		if($key eq 'comment'){
			$FORM{$key} =~ s/</&lt\;/go;
			$FORM{$key} =~ s/>/&gt\;/go;
		}
		print "\t<dt>$key</dt><dd>$FORM{$key}</dd>\n";
	}
	print "</dl></blockquote></div>\n";
}




## HTML�Υإå���
sub header
{
	print "Content-type: text/html; charset=euc-jp\n";
	print "Pragma: no-cache\n\n";

	print "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\">\n";
	print qq!<html lang="ja">\n<head>\n!;
	print qq!\t<meta http-equiv="content-type" content="text/html; charset=euc-jp">\n!;
	print qq!\t<meta http-equiv="Content-Style-Type" content="text/css">\n!;
	print qq!\t<meta http-equiv="Content-Script-Type" content="text/javascript">\n!;
	print qq!\t<link rel="stylesheet" type="text/css" href="$ini::cssfile" media="screen,projection">\n!;
	print qq!\t<link rel="index" href="$ini::scriptmain?">\n!;
	print qq!\t<link rel="start" href="$ini::backurl">\n!;
	print qq!\t<link rel="help" href="$ini::scriptsub">\n!;
	print qq!\t<title>$ini::title - �񤭹��ߥ⡼��</title>\n</head>\n\n<body>\n!;
}

# for CompactHTML
sub out_chtml
{
	$_ = "<html><head><title>$ini::title : write unit</title></head><body>@{[ shift() ]}</body></html>";

	print "Content-type: text/html; charset=Shift_JIS\n";
	printf "Content-length: %d\n\n" , length($_);

	&jcode::euc2sjis(\$_);

	print $_;
}


#�� Location:��ealis.cgi���᤹
sub http_locate
{
	if(defined($FORM{chtm})){
		&out_chtml(qq!<h1>��ƴ�λ</h1><p><a href="$ini::locate$ini::plug_chtm">���</a></p>!);
	}else{
		$ini::locate .= $ini::scriptmain . (
			( $ENV{QUERY_STRING} =~ /dhtml/  ) ? '?dhtml' :
			( $ENV{QUERY_STRING} =~ /thread/ ) ? '?thread' :
			undef);

		print "Content-type: text/html; charset=euc-jp\n";
		print "Pragma: no-cache\n";
		print "Location: $ini::locate\n\n";

		print "<!DOCTYPE HTML PUBLIC \"-//IETF//DTD HTML 2.0//EN\">\n";
		print "<html><head>\n";
		print "<meta http-equiv=\"content-type\" content=\"text/html; charset=euc-jp\">\n";
		print "<title>$ini::title : ��ƴ�λ</title>\n";
		print "</head>\n<body>\n";
		print "<h1>��Ƥ�λ���ޤ���</h1>\n";
		print "<p>�ʲ���URL����Ǽ��Ĥˤ���꤯��������</p>\n";
		print "<p><a href=\"$ini::locate\">$ini::locate</a></p>\n";
		print "<hr><address>- ealis -</address>\n";
		print "</body></html>\n";
	}
}

## ���顼����
sub error
{
	my($msg) = @_;

	if(defined($FORM{chtm})){
		&out_chtml( qq!<h1>���顼</h1><p>$msg</p><p><a href="$ini::locate$ini::plug_chtm">���</a></p>! );
	}else{
		&header;

		print qq!<h1 class="sub">ealis write unit</h1>\n<h2>ealis�Υ��顼�Ǥ�</h2>\n!;
		print qq!<div class="infobox"><p>$msg</p>\n<p><a href="$ini::scriptmain">Refresh</a></p></div>\n\n!;

		&form_dump;
		print qq!<hr class=\"section\">\n$ini::footcom\n<address>- ealis -</address>\n</body>\n</html>\n!;
	}
	exit;
}




###---------
## �����ɤ���إå�����
package LogReader;
sub new
{
	my($p) = {};

	open(IN,"$ini::logfile") || die "���ե������$ini::logfile�פ������ޤ���";
	$_ = scalar(<IN>);
	chomp($_);

	@_ = split(/,/,$_,5);
	(shift eq '[ealis3]') || die 'ealis �裳����Υ��ǤϤ���ޤ���';
	($p->{oya_num},$p->{oya_last},$p->{seri_last}) = @_[0,1,2];

	bless $p;
}
sub lread
{
	return scalar(<IN>);
}
sub seektop
{
	seek(IN,0,0);
	scalar(<IN>); #�إå����ڤ�
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

	open(LOCK, "+<$ini::lockfile") || die "$ini::lockfile �������ޤ����permission����";
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
	chmod(0666,$obj->{out});
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
	die "��͡���˼��Ԥ��ޤ���(MS-IIS?)��<br>.tmp�Ȥ��Ƽ��Ԥ����������뤫�⤷��ޤ���<blockquote> $!</blockquote>";
}
sub DESTROY
{
	my($obj) = @_;
	(-e $obj->{out}) && unlink($obj->{out});
}


### -------------
## ����object
package PastLog;

## �����ե�����򳫤�
sub new
{
	shift;
	my($form) = shift;
	my($p) = {};

	# �����Υե�����̾�����
	open(PNUM,"$ini::pnumfile") || die "��$ini::pnumfile���ɹ�����";
	my($pnum_cnt) = scalar(<PNUM>);
	close(PNUM);
	($pnum_cnt) || die "`$ini::pnumfile`���ͤ����������Ǥ�";

	$p->{pastlog} = "$ini::pastdir/$pnum_cnt\.html";

	if(!-e $p->{pastlog}){
		# ¸�ߤ��ʤ�  �������������
		&create_newplog($p,$pnum_cnt,$form->{nowdate});
	}elsif( (-s $p->{pastlog}) > ($ini::pastsize * 1024) ){
		# ���������礭��   ���եå����դ��Ƥ��鿷���������
		open(PLOG,">>$p->{pastlog}") || die "��̿Ū���顼������$p->{pastlog}�׽������";
		print PLOG qq!\n\n<hr class="section">\n\n</body>\n</html>!;
		close(PLOG);
		$pnum_cnt++;
		&create_newplog($p,$pnum_cnt,$form->{nowdate});
	}else{
		# ���ߤβ������ɵ�
		open(PLOG,">>$p->{pastlog}") || die "��̿Ū���顼������$p->{pastlog}�׽������";
		print PLOG qq!\n<div class="article">\n!;
	}

	# �쥹form��sub���ޤޤ�Ƥ���������˴ޤ��
	foreach(@::leteng_contains){
		($_ eq 'subj') and $p->{writesubj} = 1;
	}

	bless $p;
}

## ��������Ͽ��������λ���
sub create_newplog
{
	my($p,$pnum_cnt,$nowdate) = @_;

	# ���������ե����������
	$p->{pastlog} = "$ini::pastdir/$pnum_cnt\.html";
	(!-e $p->{pastlog}) || die "�������� $p->{pastlog} �������� - ����¸�ߡ�`$ini::pnumfile`���ͤ���������";
	(-w $ini::pnumfile) || die "`$ini::pnumfile`����Բ� - Permission��";

	open(PLOG,">$p->{pastlog}") || die "�������� $p->{pastlog} �������� - `$ini::pastdir` DIR��Permission���ǧ���Ʋ�����";
	$p->{chmodflag} = 1;

	# �إå������
	print PLOG qq|<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n|;
	print PLOG qq!<html lang="ja">\n<head>\n!;
	print PLOG qq!\t<meta http-equiv="content-type" content="text/html; charset=euc-jp">\n!;
	print PLOG qq!\t<meta http-equiv="Content-Style-Type" content="text/css">\n!;
	print PLOG qq!\t<link rel="stylesheet" type="text/css" href="$ini::cssfile">\n!;
	print PLOG qq!\t<title>$ini::title - ������$nowdate �ʹ�)</title>\n!;
	print PLOG qq!</head>\n<body class="pastlog">\n\n!;
	print PLOG qq!<h2>�� No.$pnum_cnt , $nowdate �ʹ�</h2>\n\n!;
	print PLOG qq!<div class="article">\n!;

	# ��No.����¸
	open(PNUM,">$ini::pnumfile");
	print PNUM  $pnum_cnt;
	close(PNUM);
}

sub pwrite
{
	my($obj,$line) = @_;

	# leteng¦��pwrite����ʤ�Ǥ����
	if(defined(&::leteng_pwrite)){
		&::leteng_pwrite($obj,\$line,\*PLOG);
		return;
	}

	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) 
		= split("\t",$line);
	my($oyaflag) = ((substr($seri,0,1) eq '*') ? 1 : 0 );

	($subj) ||= '(̵��)';
	($url) &&= qq!<a href="http://$url" target="_top" class="web">[url]</a>!;
	($email) && ($name = qq!<a href="mailto:$email">$name</a>!);
	$comment =~ s!<gd>!<span class="grad">!og;
	$comment =~ s!</gd>!</span>!og;

	if( $oyaflag ){
		# ʣ���οƻҵ��������Ǥ��ݤ�ɬ��
		if($obj->{appentflag}){
			print PLOG qq!\t</ul>\n</div>\n<hr class="atclhr">\n!;
		}else{
			$obj->{appentflag} = 1;
		}

		print PLOG qq!\t<h3 id="msg$number"><span class="atclno"><a href="?#msg$number" class="msghere">$number</a></span> : <em>$subj</em>��!;
		print PLOG qq!/ <cite>$name</cite>��<span class="stamp">($date)</span>��$url </h3>!;
		print PLOG qq!<div class="atclbody">!;
		print PLOG qq!<p style="color: $color" class="msg-oya">$comment</p>\n!;

		print PLOG qq!\t<ul class="msg-res">\n!;
	}else{
		print PLOG qq!\t\t<li style="color: $color"><cite>$name</cite>!;
		if($obj->{writesubj}){
			print PLOG qq! : <em class="subj">$subj</em><br>$comment <span class="stamp">($date)</span></li>\n!;
		}else{
			print PLOG qq!&gt; $comment <span class="stamp">($date)</span></li>\n!;
		}
	}
}

sub DESTROY
{
	my $obj = shift;

	print PLOG qq!\t</ul>\n</div></div>\n<hr class="atclhr">\n!;
	close(PLOG);

	# ���������ե������chmod
	if($obj->{chmodflag}){
		chmod(0777,"$obj->{pastlog}") || die "������$obj->{pastlog}�� chmod����";
	}
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
