#!/usr/local/bin/perl

# ealis ver.3.0   sub unit
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC 入)

use 5.004;
use vars qw[%FORM];

require './ealis_cfg.cgi';

package main;

	if(!$ENV{QUERY_STRING}){
		&print_header('掲示板のつかいかた');
		&show_readme;

	}elsif($ENV{QUERY_STRING} eq 'pickcolor'){ 
		&pickcolor;
		exit;
	}elsif($ENV{QUERY_STRING} eq 'nullimg'){ 
		&out_nullimg;
		exit;

	}elsif ($ENV{QUERY_STRING} eq 'prev_ico') { 
		&print_header('アイコン一覧',1);
		&preview_icon;
	}elsif ($ENV{QUERY_STRING} eq 'prev_color') { 
		&print_header('文字色一覧',1);
		&preview_color;
	}elsif ($ENV{QUERY_STRING} =~ /^prev_colorj;/) { 
		&print_header('文字色一覧 by java',1);
		&preview_color_jscript;

	## 検索
	}else{
		&print_header('全文検索モード');

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
#■ 検索関連
sub read_pcount
{
	($ini::pnumfile) || return;

	open(PNUM,$ini::pnumfile) || die "「$ini::pnumfile」が開けません";
	$_ = scalar(<PNUM>);
	close(PNUM);

	return $_;
}

sub print_findMenu
{
	my($pnum_cnt) = @_;

	# チェックされている場所を決める
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
	<legend accesskey=F>記事検索フォーム</legend>
	<p>検索したい<strong>キーワード</strong>を入力し、検索領域を選択して「検索ボタン」を押してください。</p>
	<p>キーワード： <input type=text name="word" size=30 value="$value" accesskey=Q class="in"></p>
	<p>検索条件
		<input type=radio name="cond" value="and"$checks[0] accesskey=A>全ての語を含む　
		<input type=radio name="cond" value="or"$checks[1] accesskey=O>いずれかの語を含む　
		<input type=checkbox name="caps" value="TRUE"$checks[6]>Capsを同一視しない（高速）
	</p>

	<p>検索範囲
		<input type=radio name="zone" value="now"$checks[2]>現行ログ　
	@{[ ($pnum_cnt)
		 ?	qq!\t<input type=radio name="zone" value="past"$checks[4]>過去ログ(#$pnum_cnt)　\n!
			 . qq!\t\t<input type=radio name="zone" value="all"$checks[5]>全てのログ\n!
		 : undef ]}
	</p>
	<div class="valueinput">
		<input type=submit value="検索する">
		<input type=button onclick="javascript:fm_reset()" onkeypress ="javascript:fm_reset()" value="クリア">
	</div>
</fieldset>
</form>
EOD
}

## ここから実際の検索分岐
sub find_main
{
	my($pnum_cnt) = @_;

	# ヒット判別obj
	my $findkey = new FindKeyword \%FORM;

	# 現行ログについて検索
	if($FORM{zone} eq 'all' || $FORM{zone} eq 'now'){
		print "<h2>現行ログ検索結果</h2>\n";
		print qq!<div class="article">\n<ol class="findresult">\n!;
		&find_nowLog($findkey);
		print "</ol></div>\n";
	}

	# 過去ログについて検索
	if($FORM{zone} eq 'all' || $FORM{zone} eq 'past'){
		print "<h2>過去ログ検索結果</h2>\n";
		while($pnum_cnt >= 1 ) {
			&find_pastLog($findkey,$pnum_cnt);
			$pnum_cnt--;
		}
	}
}


## 現行ログからの検索ルーチン
sub find_nowLog
{
	my($findkey) = @_;

	# ファイルを読み込み
	open(DB,"$ini::logfile") || die "「$ini::logfile」が開けません";
	scalar(<DB>);	#ヘッダを切る

	# 検索処理
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd);
	my($line);
	while ($line = <DB>) {
		$findkey->decide(\$line) || next;

		($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);

		$subj = (substr($seri,0,1) eq '-') ? '　<small>response</small>' : ($subj || '(無題)') ;
		$name = qq!<a href="mailto:$email">$name</a>! if($email);
		($url) &&= qq!　<a href="http://$url" target="_top">http://$url</a>!;

		# 結果を表示
		print qq!\t<li><h3><span class="atclno"><a href="$ini::scriptmain?pick=$number">$number</a></span>:\n!;
		print qq!\t <em class="subj">$subj</em>　　<cite>$name</cite>　<span class="stamp">on $date $url </span></h3>\n!;
		print qq!\t<p style="color:$color">$comment</p>　\n\n!;
	}
	close(DB);
}

## 過去ログからの検索ルーチン
sub find_pastLog
{
	my($findkey,$pastno) = @_;

	unless(-e "$ini::pastdir/$pastno\.html"){
		print "<h3>「$ini::pastdir/$pastno\.html」が開けませんでした</h3>\n";
		return;
	}

	# 過去ログファイルを読み込み
	open(DB,"$ini::pastdir/$pastno\.html") || die "過去ログ $ini::pastdir/$pastno\.html が存在しない";

	# seek <body>
	while (index(scalar(<DB>),'<body') < 0) { ; }

	my $http_this = ($ini::pasthttp || "$ini::pastdir/") . $pastno . '.html';

	my($flag,$line);
	while ($line = <DB>) {
		$findkey->decide(\$line) || next;

		# 親対策
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
		
		$line .= '</div>' if($line =~ s!</div><font!</div><div class="doc"><font!og); # ちょっと不安

		# 初めてのヒットならインデクス作成
		if(!$flag){
			$flag = 1;
			print qq!\n<hr class="atclhr">\n\n<div class="article">\n!;
			printf qq!<h2>過去ログ<a href="%s%d\.html">No.%d</a>の検索結果</h2>\n!,
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
#■ 掲示板の使い方
sub show_readme
{
	print <<"EOM";
<div class="infobox">
	<h3>４つの表示モードを持っています</h3>
	<ul>
		<li><strong>Normal Mode</strong><br>
			通常はこのモードで使用すると思います。</li>
		<li><strong>DynamicHTML Mode</strong> <em>(after MSIE 4.x,Mozilla/Gecko)</em><br>
			返信欄を出し入れできるので表示がすっきりしています。<br>
			コメント欄を大きく取っているので長文も入力しやすいです。</li>
		<li><strong>Thread View</strong><br>
			親記事の冒頭の部分のみを表示します。返信が巨大になったときに見渡しがききます。</li>
		<li><strong>Lapse View</strong><br>
			発言を時系列順に表示します。親記事・返信記事混合。</li>
	</ul>
	<h3>書き込み時の注意点</h3>
	<ul>
		<li>記事を投稿する上での必須入力項目は<strong>Name</strong>と<strong>記事</strong>です。</li>
		<li>記事には、<strong>半角カナは一切使用しないで下さい。</strong>文字化けの原因となります。</li>
		<li>投稿時に<strong>記事キー</strong>（英数字で8文字以内）を入れておくと、その記事は次回記事キーによって<strong>削除</strong>することができます。</li>
		<li>記事の保持件数は<strong>最大 $ini::logmax 件</strong>です。それを超えると古い順に<strong>@{[ $ini::pnumfile ? '過去ログに移動' : '自動削除' ]}</strong>されます。</li>
		<li>管理者が著しく不利益と判断する記事や他人を誹謗中傷する記事は予告なく削除することがあります。</li>
	</ul>
	<h3>Tips</h3>
	<ul>
		<li>返信フォームの色指定欄で<strong>＃</strong>を選択すると好きな文字色を指定できます。<br>
			１６進コードでもカラー名（hotpink,whitesmokeなど）でも入力可能です。<br>
			また一度指定するとクッキーされ、<strong>Ｃ</strong>でクッキー色した文字色を使用できます。</li>
		<li>JavaScriptが有効な場合、<strong>&lt;color&gt;</strong>ボタンは記事プレビューを兼ねています。ご利用下さい。</li>
		<li>以下のaccesskeyが設定されています。
			<ul>
				<li><strong>Alt + I</strong>:　機能メニュー</li>
				<li><strong>Alt + N</strong>:　新規投稿フォーム</li>
				<li><strong>Alt + [0-9]</strong>:　ｎつ目の返信フォーム</li>
				<li><strong>Alt + M</strong>:　View Mode</li>
				<li><strong>Alt + P</strong>:　Log Pager</li>
			</ul></li>
	</ul>
</div>
EOM
}

#■ 色選択ウインドウ 
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

// 値ステップ,セルのサイズ,パターン開始,終了
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
			document.write('Win&Mac共通 6x6x6=126');
		}
	}
}
</script></head>

<body style="margin-top:0">
<form action="javascript:">

<div style="font:10pt Verdana,sans-serif; background: #E6F2F2; color:#333;">
	ealis color manager　
	<select name="pal" style="font-size:9pt; position:absolute; top:0; right:1px;" onchange="changeLst(this.value);">
		<script type="text/javascript">
		writeList();
		</script>
	</select>
</div>

<table border=1 cellpadding=4 cellspacing=0 bgcolor="white" align=center>
	<tr><td align=middle style="font-size: 9pt;">
	<div class="date">　　<strong>value:</strong> <big>#</big>
		<input name="COLOR" maxlength=6 size=9 type=text onChange="setColor(this.value);" style="ime-mode:disabled">
		←手動入力時はTabで確定</div>

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

# 透明の1x1のgif
sub out_nullimg
{
	print "Last-Modified: Sat, 28 Apr 2001 15:52:09 GMT\n";
	print "Content-type: image/gif\n\n";
	print pack('H*', '4749463839610100010080000000000000000021F90403000000002C00000000010001000002024401003B');
}


###---------
#■ HTMLのヘッダー
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

## フォームデコード
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
#■ プレビュー機能
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
				'消える飛行機雲　追いかけて追いかけて<br>この丘を越えたあの日から変わらずいつまでも<br>真っ直ぐに僕たちはあるように<br>わたつみのような強さを守れるよきっと';
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
	print qq!  showText = "消える飛行機雲　追いかけて追いかけて<br>この丘を越えたあの日から変わらずいつまでも<br>真っ直ぐに僕たちはあるように<br>わたつみのような強さを守れるよきっと";\n!;
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
	## colがrand時の対策
	print q!  document.writeln("<p><a href=\"javascript:setCol('" + col_code[i] + "')\">" + col_name[i] + '</a>：　');! . "\n";
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
#■ キーワード判別
package FindKeyword;
sub new
{
	shift;
	my $form = shift;

	my($p) = {};
	$p->{cond} = $form->{cond};
	$p->{caps} = $form->{caps};

	# 入力内容を消化
	my($word) = $form->{word};
	$word =~ s'<'&lt;'go;
	$word =~ s'>'&gt;'go;
	$word =~ s'　' 'go;
	$word =~ s'\t' 'go;
	@{ $p->{words} } = split(/\s/,$word);

	bless $p;
}
sub decide
{
	my($obj,$line) = @_;

	my($result,$query);
	foreach $query (@{ $obj->{words} }){
		# 判定部
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

		# and/or振分
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
