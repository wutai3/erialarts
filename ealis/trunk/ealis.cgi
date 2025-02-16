#!/usr/local/bin/perl
# (EUC 入)
#
# ealis ver.3.0.9 ; GPL released 
# ---  erialarts : https://github.com/wutai3/erialarts/

use 5.004;
use vars qw[%FORM $ANKOR %COOKIE $sozai];

require './ealis_cfg.cgi';

package main;

	&form_decode;
	my $logobj = new LogReader;

	# 投稿フォーム無し
	if (defined($FORM{thread})){
		&print_header(' - Thread');
		&print_viewSel;

		if(defined($FORM{max})){ $FORM{show} = $ini::logmax; }
		&print_logpager($logobj,'thread;');
		&thread_main($logobj);
		&print_logpager($logobj,'thread;');
	}elsif(defined($FORM{lapse})){
		&print_header(' - Lapse');
		&print_viewSel(NOSTART);

		my $lapse = &lapse_load($logobj);
		&print_logpager($logobj,'lapse;');
		&lapse_show($lapse,$logobj);
		&print_logpager($logobj,'lapse;');

	# 投稿フォーム必要
	}else{
		&init_cookie;
		$sozai = new SozaiBank \%COOKIE;

		require $ini::leteng;
		require $ini::plug_grad if($ini::plug_grad);
		if($FORM{pick}){
			&print_header(" - msg:$FORM{pick}");
			&print_viewSel;
			&print_articles($logobj);
		}elsif(defined($FORM{dhtml})){
			&print_header(' - DHTML',TRUE);
			&print_oyaForm('dhtml');
			&print_viewSel;
			&print_logpager($logobj,'dhtml;') if($FORM{start});
			&print_articles($logobj);
			&print_logpager($logobj,'dhtml;');
		}else{
			&print_header(undef,TRUE);
			&print_oyaForm;
			&print_viewSel;
			&print_logpager($logobj,undef) if($FORM{start});
			&print_articles($logobj);
			&print_logpager($logobj,undef);
		}
	}
	&print_footer;

exit;


sub print_footer
{
	printf qq!</div>\n<hr class="section" id="see%d">\n\n!,  ++$ANKOR;
	print qq!<div class="footcom">$ini::footcom</div>\n! if($ini::footcom);

	# ↓これは消さないで
	print qq!\n<address>- <a href="https://github.com/wutai3/erialarts/">ealis 3.0.10</a> -</address>\n!;
	print "\n</body>\n</html>";
}



## 順に走査しながらprint
sub print_articles
{
	my($logobj) = @_;
	my $grad = new GradEngine if($ini::plug_grad);	# gdプラグインロード

	my(%cell,$line,$passoya,$oyaflag,$rescnt);
	while($line = $logobj->lread() ) {
		($FORM{pick} && index($line, "\t$FORM{pick}\t" ) != 4 ) && next;

		# 現在の親を把握
		$oyaflag = 0;
		if(substr($line,0,1) eq '*'){ $passoya++; $oyaflag = 1;}
		($FORM{start} < $passoya) || next;	# seek start
		if($oyaflag){
			($ANKOR < $FORM{show}) || last;
			(!$FORM{pick}) || (!$ANKOR) || last;
			($ANKOR) && &leteng_resform(\%cell,$oyaflag,$rescnt);
			$ANKOR++;
			$rescnt = 0;
		}else{
			$rescnt++;
		}

		# データー解析
		%cell = {};
		($cell{seri},$cell{number},$cell{date},$cell{name},$cell{subj},$cell{comment},$cell{color},
			$cell{email},$cell{url},$cell{icon},$cell{edt},$cell{ipaddr},$cell{pwd})
				= split("\t",$line);

		# 各要素を加工
		&touch_article(\%cell);
		($grad) && $grad->encode(\$cell{comment}); #gdタグを処理

		# レタリングエンジンへ渡す
		&leteng_lettering(\%cell,$oyaflag,$rescnt);
	}

	if($ANKOR){
		&leteng_resform(\%cell,$oyaflag,$rescnt);
	}else{
		print '<div class="article"><p>' . (
				($FORM{pick}) ? 'そのスレッドNo.に該当する記事は存在しませんでした (pick err)' :
				($FORM{start} > $logobj->{oyanum}) ? 'そのページ範囲に記事はありません (start err)' :
				'記事はまだ投稿されていません。'
			). "</p></div>\n";
	}
}

# 記事データーをエンコード
sub touch_article
{
	my($in) = @_;

	$in->{name} = qq!<a href="mailto:$in->{email}">$in->{name}</a>! if($in->{email});
	($in->{subj}) ||= '(無題)';
	($in->{url}) &&= sprintf '<a href="http://%s" target="_top" class="web">%s</a>', $in->{url},
				  ($ini::homeicon || $in->{url});

	if($in->{edt}){
		@_ = split(/,/,$in->{edt},2);
		$in->{date} = sprintf '<span class="rewrited" title="再編集: %s">%s *%s</span>',
						pop, $in->{date},shift;
	}
}

## モード切替タブ
sub print_viewSel
{
	my($start) = shift() ? 0 : $FORM{start};	# start値が使えないとき

	print qq!\n<div class="view-select">\n!;
	print qq!\t<span class="label">View <span class="key">M</span>ode : </span>\n!;
	print qq!\t　<a href="$ini::scriptmain?start=$start;show=$FORM{show}" accesskey=M>Normal</a>!;
	print qq! / <a href="$ini::scriptmain?dhtml;start=$start;show=$FORM{show}" accesskey=M>DynamicHTML</a>!;
	print qq! / <a href="$ini::scriptmain?thread;start=$start;show=$FORM{show}" accesskey=M>Thread</a>!;
	print qq! / <a href="$ini::scriptmain?lapse;show=$FORM{show}" accesskey=M>Lapse</a>!;
	print qq!　 : <a href="$ini::plug_chtm?thr;st=$start" accesskey=M>chtml</a>! if($ini::plug_chtm);
	print qq!\n</div>\n!;
}

## ログページャ
sub print_logpager
{
	my($logobj,$arg) = @_;

	print qq!\n<div class="log-pager">\n!;
	print qq!\t<span class="label">Log <span class="key">P</span>ager :</span>　\n!;

	my $current_tab = $FORM{start} / $FORM{show};	# 現在の記事の頁数を測定
	$current_tab = ( $current_tab == int($current_tab) ? $current_tab : int($current_tab + 1) ) +1;

	my $tab = ($current_tab >= 20) ? ($current_tab - 10) : 1;	# 前後10件を表示

	my $gopage;
	for(0 .. 20){
		if($tab == $current_tab){
			print "\t<em>$tab</em>\n";
		}else{
			$gopage = $FORM{show} * ( $tab - 1 );		# 何頁目の記事かを生成
			($gopage < $logobj->{oya_num}) || last;			# 含有する親記事数より多い頁
			printf qq!\t<a href="%s?%sstart=%d;show=%d" accesskey=P>%d</a>\n!,
							$ini::scriptmain,$arg,$gopage,$FORM{show},$tab;
		}
		$tab++;
	}
	print qq!\t<a href="$ini::scriptlog">File</a>\n!  if($ini::pnumfile);

	# ページ記事数切り替え
	my $step = int($ini::show /2);		# 変更幅

	printf "\t　　\@%datc/p(", $FORM{show};
	printf '<a href="%s?%sstart=%d;show=%d">+%d</a> ', $ini::scriptmain,$arg,$FORM{start},$FORM{show}+$step,$step;
	printf '<a href="%s?%sstart=%d;show=%d">-%d</a> ', $ini::scriptmain,$arg,$FORM{start},$FORM{show}-$step,$step  if($FORM{show} > $step);
	printf '<a href="%s?%sstart=%d;show=%d">def</a> ', $ini::scriptmain,$arg,$FORM{start},$ini::show  if($ini::show != $FORM{show});

	if(defined($FORM{thread}) && $logobj->{oya_num} > $FORM{show}){
		print ", <a href=\"$ini::scriptmain?thread;max\">max:$ini::logmax</a>";
	}else{ 
		print ", max:$ini::logmax";
	}

	print ")\n</div>\n\n";
}

## 初期化とか
sub form_decode
{
	# Deny IP Check
	foreach(@ini::deniedaddrs){
		if(index($ENV{REMOTE_ADDR}, $_ ) == 0 && length($_) > 4 ){
			print "Status: 204\n\n";
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
	$FORM{show}  ||= $ini::show;
	$FORM{start} ||= 0;
}

# %COOKIE 代入
sub init_cookie
{
	my($name, $value);
	foreach ( split(/;/,$ENV{HTTP_COOKIE}) ) {
		($name, $value) = split(/=/,$_,2);
		$name =~ tr/ //d;

		($name eq 'EALIS') || next;
		$value =~ s/%(..)/pack('H2',$1)/eg;
		foreach ( split(/,/,$value) ) {
			($name, $value) = split(/:/,$_,2);
			$COOKIE{$name} = $value;
		}
		last;
	}
}


## HTMLのヘッダー
sub print_header	# title,mode
{
	my($title,$viewflag) = @_;

	# lastmodに関わらずカウント
	my($visitor) = do "$ini::plug_cnt" if($ini::plug_cnt && $viewflag && !$FORM{start});

	print "Content-type: text/html; charset=euc-jp\n";
	print "P3P: CP='ONLi COM CUR OUR'\n";
	print &gene_lastmod;

	if($ENV{REQUEST_METHOD} eq 'HEAD'){
		print "\n$logobj->{lastwrite}\n";
		exit;
	}elsif($ini::gzip && $ENV{HTTP_ACCEPT_ENCODING}=~ /gzip/ && (-x $ini::gzip)){
		print "Content-Encoding: gzip\n\n";
		open(STDOUT,"| $ini::gzip -1 -c");
		print ' ' x 2048;	# IEのchunk対策
	}
	print qq|\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n|;
	print qq!<html lang="ja">\n<head>\n!;
	print qq!\t<meta http-equiv="content-type" content="text/html; charset=euc-jp">\n!;
	print qq!\t<meta http-equiv="Content-Style-Type" content="text/css">\n!;
	print qq!\t<meta http-equiv="Content-Script-Type" content="text/javascript">\n!;
	print qq!\t<meta name="robots" content="NOINDEX, NOFOLLOW">\n! if(defined($FORM{dhtml}) ||$FORM{pick});
	print qq!\t<link rel="stylesheet" type="text/css" href="$ini::cssfile" media="screen,projection">\n!;
	print qq!\t<link rel="start" href="$ini::backurl">\n!;
	print qq!\t<link rel="help" href="$ini::scriptsub">\n!;
	print "\t<title>$ini::title$title</title>\n</head>\n\n";

	print qq!<body>\n<div class="headblock">\n!;
	print '<h1 class="main" id="see0">' . ($ini::h1 || $ini::title || 'my ealis') . "</h1>\n\n";

	print qq!<script type="text/javascript"><\!--\n!;
	print " function colsel() { window.open('$ini::scriptsub?pickcolor','colsel','scrollbars=no,status=no,height=300,width=380,resizable=yes'); }\n";
	print " function prevtxt(form) { window.open('$ini::scriptsub?prev_colorj;'+ form ,'prevtxt','scrollbars=yes,status=yes,height=500,width=470,resizable=yes'); }\n";

	# DHTML実現コード
	if(defined($FORM{dhtml})){
		print " function view(obj){\n";
		print "  if(document.getElementById){document.getElementById(obj).style.display=='none'?document.getElementById(obj).style.display='':document.getElementById(obj).style.display='none'}\n";
		print "  else if(document.all){document.all(obj).style.display=='none'?document.all(obj).style.display='':document.all(obj).style.display='none'}\n";
		print " }\n";
	}
	defined(&leteng_jscript) && &leteng_jscript;		#letengの返信窓生成javascript
	print "// --></script>\n\n";

	# head table
	print "<div class=\"menubox\">\n";
	print "\t<p>lastpost : <var>$logobj->{lastwrite}</var> ";
	print ", visitor <var>$visitor</var> " if($visitor);

	print "<br>\n\t<a href=\"$ini::backurl\" accesskey=I>戻る</a>";
	print " <a href=\"$ini::scriptsub?\" accesskey=I>掲示板の使い方</a>";
	print " <a href=\"$ini::scriptsub?find\" accesskey=I>全文検索</a>";
	print " <a href=\"$ini::scriptedt?\" accesskey=I>記事メニュー</a>";
	print " <a href=\"$ini::plug_plus\" accesskey=I>ログ解析</a>"  if ($ini::plug_plus);
	print " <a href=\"$ini::scriptedt?admin\" accesskey=I>管理用</a>";
	print "</p>\n<hr></div>\n</div>\n\n";
	print "<div class=\"bodyblock\">\n\n";
}

# Last-Modified: Sun, 11 Nov 2000 18:33:04 GMT を付ける
sub gene_lastmod
{
	(index($ENV{HTTP_USER_AGENT},'MSIE 5.0') > -1) && return;

	if(defined($FORM{verge})){
		return "Pragma: no-cache\n";
	}else{
		my($secg,$ming,$hourg,$mdayg,$mong,$yearg,$wdayg) = gmtime( (stat($ini::logfile))[9] );
		return sprintf "Last-Modified: %s, %02d %s %04d %02d:%02d:%02d GMT\n",
			('Sun','Mon','Tue','Wed', 'Thu','Fri','Sat')[$wdayg],$mdayg,
			('Jan','Feb','Mar','Apr','May','Jun', 'Jul','Aug','Sep','Oct','Nov','Dec')[$mong],
			$yearg +1900,$hourg,$ming,$secg;
	}
}

## 親記事投稿フォーム
sub print_oyaForm
{
	print qq!<div class="headcom">$ini::headcom</div>\n! if($ini::headcom);
	print <<"EOD";
<form method=POST action="$ini::scriptwri?@{[ shift() ]}" accept-charset="euc-jp" class="oyaform">
<fieldset class="oyaform">
	<legend accesskey=N>新規投稿　　 <var>（@{[ &ins_status ]}）</var></legend>
	<table summary="oya-posting"><tr><td colspan=2>
	<table summary="vars"><tr><th><label class="requisite" for="fmname">Name</label></th>
	<td><input type=text name="name" size=30 value="$COOKIE{name}" class="in" id="fmname"></td>
	<th>Mail</th><td><input type=text name="email" size=28 value="$COOKIE{email}" class="in"></td></tr>
	<tr><th>Title</th><td><input type=text name="subj" size=40 value="" class="in"></td>
	<th>　Key</th><td><input type=text name="pwd" size=10 maxlength=8 value="$COOKIE{pwd}" class="in" style="ime-mode:disabled"><small>(英数字8以内)</small></td></tr>
	<tr><th>URL</th><td colspan=3><input type=text size=76 name="url" value="http://$COOKIE{url}" class="in"></td></tr>
	</table>
	</td></tr><tr><td colspan=2>
	<textarea cols=65 rows=7 name="comment"></textarea><br>
	<div class="list-colors"><script type="text/javascript"><!--
		 document.writeln('<a href="javascript:prevtxt(0)">&lt;color&gt;<\\/a>');
	//--></script>
	<noscript><a href="$ini::scriptsub?prev_color" target="elsprv">&lt;color&gt;</a></noscript>
	@{[ $sozai->iroradio() ]}</div></td></tr>
	<tr><td> @{[ $sozai->icolist() ]} </td>
	<td class="submit">　　<input type=submit value="　　投稿　　"><input type=reset value="消去"></td>
	</tr></table>
</fieldset>
</form>
EOD
}
sub ins_status
{
	return 
	($ini::allowtag ? 'allow tags' : 'deny tags') . 
	($ini::autolink ? ' , autolink': undef) .
	($ini::plug_grad ? ' , gd tag ok': undef) .
	($ini::res_sort ? ' , resup' : undef) . 
	($ini::markquote ? ' , autoquote' : undef);
}


## Thread modeのとき
sub thread_main
{
	my($logobj) = @_;

	print qq!\n<hr class="atclhr">\n\n<div class="article">!;
	print qq!<ul class="thread">\n!;

	my($line,$i,$ankor,$parent,$flag,$rescnt);
	while($line = $logobj->lread() ){
		# 親記事のみを表示
		if(substr($line,0,1) eq '*'){
			if($FORM{start} < $i){
				$ankor++;
				if($ankor > $FORM{show}){ $flag = 1; last; }
				&thread_show(\$parent,$rescnt);
				$rescnt = 0;
			}
			$i++;
			$parent = $line;
		}else{
			($FORM{start} < $i) && $rescnt++;
		}
	}
	($flag) || &thread_show(\$parent,$rescnt);

	print "</ul></div>\n\n";
}
sub thread_show
{
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr)
		 = split("\t",${shift()});
	my($rescnt) = shift() || 0;

	($subj) ||= (substr($seri,0,1) eq '*') ? '(無題)' : ' (response) ';

	$comment =~ s/<br>/\n/igo;
	$comment =~ s/\n[\n]+/\n/go;
	$comment =~ s'<'&lt;'go;
	$comment =~ s'>'&gt;'go;

	# 2行だけ表示
	split(/\n/,$comment,3);
	$comment = join('<br>', shift,shift);
	$comment .= ' ...' if(shift);

	print qq!\t<li><h3><span class="atclno"><a href="$ini::scriptmain?pick=$number">$number</a></span>.<span class="rescnt">$rescnt</span>: <em>$subj</em>\n!;
	print qq!\t\t　　<cite>$name</cite>　　<span class="stamp">($date)</span></h3>\n!;
	print qq!\t\t<p class="msg-each">$comment</p>\n!;
}

## Lapse modeのとき
# ログを読み込む
sub lapse_load
{
	my($logobj) = @_;

	my($p) = {};
	$logobj->{oya_num} = 0;

	# シリアル範囲でhash雛形作成
	my($key);
	for(0 .. ($FORM{show} -1)){
		$key = $logobj->{seri_last} - $FORM{start} - $_ ;
		$key += 1000 if($key < 0);
		($key >= 0) || last;
		$p->{ sprintf '%03d',$key } = '';
	}

	# 雛形に合った記事を読む
	my($seri,$line);
	my($showcnt) = $FORM{show};
	while($line = $logobj->lread() ){
		$logobj->{oya_num}++;				# pagerに必須

		($showcnt > 0) || next;

		$seri = substr($line,1,3);
		if( defined($p->{$seri}) ){
			$p->{$seri} = $line;
			--$showcnt;
		}
	}

	return $p;
}
sub lapse_show
{
	my($hash,$logobj) = @_;

	print qq!\n<hr class="atclhr">\n\n<div class="article">\n!;
	print qq!<ol class="lapse">\n!;

	# seri_last 以上の値は優先度を下げるソート
	my($key);
	foreach $key ( map { $_->[0] } sort { $b->[1] <=> $a->[1] } map { [$_, (($_ > $logobj->{seri_last}) ? ($_ -1000) : $_ )] } keys %{$hash} ) {

		if($hash->{$key}){
			my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr)
				 = split("\t",$hash->{$key});

			($subj) ||= ((substr($seri,0,1) eq '*') ? '(無題)' : ' (response) ');

			print qq!\t<li><h3><span class="atclno"><a href="$ini::scriptmain?pick=$number">$number</a></span> : <em>$subj</em>\n!;
			print qq!\t\t　　<cite>$name</cite>　　<span class="stamp">($date)</span></h3>\n!;
			print qq!\t\t<p class="msg-each" style="color:$color;">$comment</p>\n!;
		}else{
			print qq!\t<li>deleted (#$key)</li>!;
		}
	}

	print "</ol></div>\n\n";
}

###---------
## ログを読む＆ヘッダ情報
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


###---------
## 各種リストデータはバッファリング
package SozaiBank;
sub new
{
	shift;
	# 素材を require
	bless { cook => shift() };
}
# javascript内からのcallは"/"をエンコード
sub enc
{
	my($obj,$func) = @_;

	my $str = &$func($obj); # as $obj->$func;
	$str =~ s'/'\\/'og;

	return $str;
}
sub irolist
{
	my($obj) = @_;
	unless($obj->{irolist}){
		my $b;
		my $arr = \@Sozai::colpalet;

		$b  = '<select name="color2" class="min">';
		for ($_ = 0; $_ < scalar(@{$arr}); $_ +=2) {
			($arr->[$_] ne '*') || next;
			$b .= "<option value=\"$arr->[$_]\">$arr->[$_+1]";
		}
		$b .= "<option value=\"$obj->{cook}->{color}\" selected>Ｃ</option>" if ($obj->{cook}->{color});
		$b .= '<option value="">＃</option></select>';
		$obj->{irolist} = $b;
	}
	return $obj->{irolist};
}

sub iroradio
{
	my($obj) = @_;
	unless($obj->{icoradio}){
		my $b;
		my $arr = \@Sozai::colpalet;

		$b  = "<input type=radio name=\"color\" value=\"$arr->[0]\"";
		$b .= ' checked' unless($obj->{cook}->{color});
		$b .= "><span style=\"color:$arr->[0]\">■</span>";
		for ($_ = 2; $_ < scalar(@{$arr}); $_ +=2) {
			$b .= (($arr->[$_] ne '*') ? qq!<input type=radio name="color" value="$arr->[$_]"><span style="color:$arr->[$_]">■</span>! : '<br>');
		}
		$b .= '<input type=radio name="color" value=""';
		$b .= (($obj->{cook}->{color}) 
				? " checked><span style=\"color:$obj->{cook}->{color}\">■</span>" 
				: '>□');
		$b .= '<small><input type=text name="color2" value="';
		$b .= $obj->{cook}->{color} || '#';
		$b .= '" size=8 class="in" style="ime-mode:disabled"><a href="javascript:colsel()">選択</a></small>';

		$obj->{icoradio} = $b;
	}
	return $obj->{icoradio};
}

sub icolist
{
	scalar(@Sozai::icopalet) || return;

	my($obj) = @_;
	unless($obj->{iconlist}){
		my $b;
		my $arr = \@Sozai::icopalet;
		my $flag;

		$b  = "<a href=\"$ini::scriptsub?prev_ico\" target=\"elsprv\">&lt;icon&gt;</a> ";
		$b .= '<select name="icon">';
		for ($_ = 0; $_ < scalar(@{$arr}); $_ +=2) {
			if($arr->[$_] eq '*'){
				$b .= "<option value=\"\">$arr->[$_+1]";
			}elsif($arr->[$_] eq '**'){
				$b .= '</optgroup>' if($flag);
				$b .= qq!<optgroup label="$arr->[$_+1]"><option class="group" value="*">$arr->[$_+1]!;
				$flag = 1;
			}else{
				$b .= "<option value=\"$arr->[$_]\"";
				$b .= ' selected' if($obj->{cook}->{icon} eq $arr->[$_]);
				$b .= ">$arr->[$_+1]";
			}
		}
		$b .= '</optgroup>' if($flag);
		$b .= '</select>';
		$obj->{iconlist} = $b;
	}
	return $obj->{iconlist};
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
