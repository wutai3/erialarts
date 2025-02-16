#!/usr/local/bin/perl

# ealis ver.3.0   edit unit
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC 入)

use 5.004;
use Fcntl qw[:flock];
use Time::Local;
use vars qw[%FORM $ADMINFLAG];

require './ealis_cfg.cgi';

package main;
	&form_decode;

	if( defined($FORM{admin}) ) { 
		&print_header('管理メニュー');
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
		&print_header('記事編集モード');
		&MenuView::print_editview;
		&print_footer;
	}elsif( shift(@{$FORM{sel}}) ){
		&error('処理命令が選択されていません');

	}else{
		&print_header( (($ADMINFLAG) ? '記事管理モード' : '記事メニュー') );
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



#■ Locationで元のCGIに戻す
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
	print "<title>$ini::title : 投稿完了</title>\n";
	print "</head>\n<body>\n";
	print "<h1>処理を完了しました</h1>\n";
	print "<p>以下のURLからお戻りください。</p>\n";
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
	print qq!\t<span class="label">Log <span class="key">P</span>ager :</span>　\n!;

	my $current_tab = $FORM{start} / $FORM{show};	# 現在の記事の頁数を測定
	$current_tab = ( $current_tab == int($current_tab) ? $current_tab : int($current_tab + 1) ) +1;
	my $tab = ($current_tab >= 20) ? ($current_tab - 10) : 1;	# 前後10件を表示
	my $arg = "key=$::FORM{key};" if($::ADMINFLAG);

	my($gopage);
	for(0 .. 20){
		if($tab == $current_tab){
			print "\t<em>$tab</em>\n";
		}else{
			$gopage = $FORM{show} * ( $tab - 1 );		# 何頁目の記事かを生成
			($gopage < $logobj->{oya_num}) || last;			# 含有する親記事数より多い頁
			printf qq!\t<a href="%s?%sstart=%d;show=%d" accesskey=P>%d</a>\n!,
							$ini::scriptedt,$arg,$gopage,$FORM{show},$tab;
		}
		$tab++;
	}
	print qq!\t<a href="$ini::scriptlog" accesskey=P>File</a>\n!  if($ini::pnumfile);

	# ページ記事数切り替え
	my $step = int($ini::show /2);		# 変更幅

	print "\t　　\@$FORM{show}atc/p(";
	printf '<a href="%s?%sstart=%d;show=%d" accesskey=P>+%d</a> ', $ini::scriptedt,$arg,$FORM{start},$FORM{show}+$step,$step;
	printf '<a href="%s?%sstart=%d;show=%d" accesskey=P>-%d</a> ', $ini::scriptedt,$arg,$FORM{start},$FORM{show}-$step,$step  if($FORM{show} > $step);
	printf '<a href="%s?%sstart=%d;show=%d" accesskey=P>def</a> ', $ini::scriptedt,$arg,$FORM{start},$ini::show  if($ini::show != $FORM{show});
	print  qq!, <a href="$ini::scriptedt?thread;max" accesskey=P>max:$ini::logmax</a>!;

	print ")\n</div>\n\n";
}


### others
#■ HTMLのヘッダー
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

## エラー処理 
sub error
{
	&print_header('ealis error')  unless($_[1]);

	print qq!<h2>ealisのエラーです</h2>\n!;
	print qq!<div class="infobox"><p>@{[ shift() ]}</p></div>\n!;
	print qq!<hr class="section">\n</body></html>\n!;

	exit;
}

sub form_decode
{
	($ENV{CONTENT_LENGTH} < 51200) || &error('投稿データが大きすぎます。');

	my($buf,$name, $value);
	read(STDIN, $buf, $ENV{CONTENT_LENGTH}) if($ENV{REQUEST_METHOD} eq 'POST');
	$buf .= ';' .$ENV{QUERY_STRING};

	foreach ( split(/[&;]/,$buf) ) {
		($name, $value) = split(/=/, $_,2);
		$value =~ tr/+/ /;
		$value =~ s/%(..)/pack('H2',$1)/eg;
		$value =~ s/\t/    /og;

		if ($name eq 'sel') {
			($value =~ /^[\w\*\-]+$/) || &error("不正な記事選択です。 '$value'");
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
# クッキーをロード
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


## 管理者入室画面
sub print_adminmenu
{
	print qq!<h2>記事管理モード</h2>\n!;
	print qq!<form action="$ini::scriptedt" method=get>\n<div class="infobox">\n!;
	print qq!\t<p>記事の編集・一括削除を行えます。<br>パスワード空欄時は通常の削除モードになります。</p>\n!;
	print qq!\t<p>管理者パスワード： <input type=password name="key" size=11 maxlength=8 value=""><input type=submit value="認証"></p>\n!;
	print qq!</div>\n</form>\n\n!;

	print qq!<h2>システム情報</h2>\n<div class="infobox">\n<ul>\n!;

	{
		my($lines);
		open(IN,$ini::logfile) || die "ログファイル「$ini::logfile」が開けません";
		printf "\t<li><strong>LogHeader</strong>: %s\n", scalar(<IN>);
		while( read(IN,$_,1024) ){ $lines += tr/\n//; }		# ログ行数を取得
		close(IN);

		printf("\t<li><strong>Logfile:</strong> <var>%d</var>KB,<var>%d</var>lines",
					 (-s $ini::logfile)/1024 , $lines );;
		print " (999linesを越えないように\$ini::logmaxを調整すること)\n";
	}

	&main::initLocation;
	print "\t<li><strong>Locate:</strong> $ini::locate\n";

	if($ini::gzip){
		printf "\t<li><strong>Content-Encoding:</strong> %s(%s) , UA is %s\n",
				$ini::gzip,
				((-x $ini::gzip) ? 'found' : 'not found'),
				(($ENV{HTTP_ACCEPT_ENCODING}=~ /gzip/) ? 'ready' : 'non-support');
	}

	open(FL, ">>$ini::lockfile") || die "$ini::lockfile が開けません";
	eval{ flock(FL, 2); };
	printf "\t<li><strong>flock</strong>: %s\n",  @{[ ($@) ? 'error' : 'supported' ]};
	close(FL);

	print qq!\t<li><a href="$ini::scriptlog?check">過去ログ機能動作チェック</a>\n! if($ini::scriptlog);

	print "</ul>\n</div>\n";
}


###---------
##■ 記事選択＆編集画面表示
package MenuView;
## 記事メニュー
sub print_noteMenu
{
	my($cook) = @_;

	print qq!<form action="$ini::scriptedt?" method=GET>\n\n!;
	print qq!<div class="infobox"><p>\n!;

	if($::ADMINFLAG){
		print "\t■管理モードで動作しています。<br>\n";
		print "\t■記事編集時は<strong>一つだけ選択</strong>、記事削除時は<strong>複数選択可能</strong>です。<br>\n";
		print "\t■親記事を削除するとその返信記事も削除されます。\n";
	}else{
		print "\t■記事をチェックし記事キーを入力した後に、必要な処理を選び実行してください。<br>\n";
		print "\t■記事編集が可能なのは投稿から４８時間以内です。<br>\n" if($ini::useredit == 2);
		print "\t■返信の付いた親記事は管理人以外削除できません。\n";
	}
	print "</p></div>\n";


	print qq!<div class="valueinput">\n\t処理：!;
	if($::ADMINFLAG){
		print '<input type=radio name="mode" value="edit" checked>この記事を編集（<strong>単数のみ</strong>）';
		print '<input type=radio name="mode" value="erase">この記事を削除（<strong>複数可能</strong>）';
	}elsif($ini::useredit){
		print '<input type=radio name="mode" value="edit" checked>この記事を編集';
		print '<input type=radio name="mode" value="erase">この記事を削除';
	}else{
		print '<input type=radio name="mode" value="erase" checked>この記事を削除';
	}

	print "\n\t　　";
	print (($::ADMINFLAG)
			? qq!<input type=hidden name="key" value="$::FORM{key}">!
			: qq!<strong>記事キー</strong> <input type=text name="key" size=10 value="$cook->{pwd}" style="ime-mode:disabled">!);

	print qq!\n\t<input type=submit value="実行"><input type=reset value="クリア">\n!;
	print "</div>\n<hr>\n";
}

## ノート一覧
sub print_articles
{
	my($logobj) = @_;

	print qq!\n<div class="article">\n\n<ul class="edtview">\n!;

	my($ankor,$oyaflag,$rescnt,$line,$nowline);
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd);
	while($line = $logobj->lread()){
		$oyaflag = 0;
		# 現在の親を把握
		if(substr($line,0,1) eq '*') { $nowline++; $oyaflag=1;}
		($::FORM{start} >= $nowline) && next;

		($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);

		# 値をエンコード
		$comment =~ s'<br>' 'go;
		$comment = substr($comment,0,58).'...' if(length($comment) > 60);
		$comment =~ s'<'&lt;'go;
		$comment =~ s'>'&gt;'go;

		if($oyaflag){
			$ankor++;
			($ankor > $::FORM{show}) && last;
			if($rescnt == 1){ print "\t\t</ol>\n\t</li>\n"; $rescnt = 0;}
			($subj) ||= '(無題)';

			print "\t<li><h3>";
			print &make_chkbox($seri);

			print qq!\t\t[<span class="atclno"><a href="$ini::scriptmain?pick=$number">$number</a></span>] <em>$subj</em>!;
			print qq!　 From: <cite>$name</cite>　 <span class="stamp">($date)</span><br>\n\t\t $comment !;
			print qq!\n\t\t　<span class="stamp">[$ipaddr]</span>!  if ($::ADMINFLAG);
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
# チェック欄
sub make_chkbox
{
	return sprintf qq!<input type=%s name="sel" value="%s">\n!,
			(($::ADMINFLAG) ? 'checkbox' : 'radio') , shift;
}


##  記事編集画面を表示
sub print_editview
{
	scalar(@{$::FORM{sel}}) || &::error('編集対象記事が指定されていません。',TRUE);
	(scalar(@{$::FORM{sel}}) == 1) || &::error('編集対象記事は一個だけ選んでください。<br>もしくは「編集モード」と「一括削除モード」を間違えてます。',TRUE);

	# 記事をpick
	my $logobj = new LogReader;
	my($line,$hitcnt);
	while($_ = $logobj->lread()){
		(substr($_,0,4) eq ${$::FORM{sel}}[0]) || next;
		$line = $_;
		$hitcnt++;
	}
	($line) || &::error("編集対象記事が見つかりませんでした。(no ${$::FORM{sel}}[0])");
	($hitcnt == 1) || &::error("編集対象記事が複数($hitcnt)マッチしたので、念のため処理を中止しました。");

	# データ抽出
	chomp($line);
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);
	&EditLog::decide_key($pwd,TRUE);		# 消してもいい
	($::ADMINFLAG) || &EditLog::decide_edtlim($date) || &::error('編集期限（初回投稿から４８時間）を過ぎているのでこの記事は編集できません。',TRUE);

	# データ整形
	$comment =~ s/<br>/\n/og;
	$comment =~ s/&/&amp;/og;
	$comment =~ s/<[^>]*>//g  if(!$ini::allowtag);   # 自動リンクや<q>を取る

	($pwd) ||= '&lt;uninputed&gt;';
	($url) &&= "http://$url";


	print <<"EOD";
<script type="text/javascript"><!--
	function colsel() { window.open('$ini::scriptsub?pickcolor','colsel','scrollbars=no,status=no,height=300,width=380,resizable=yes'); }
	function chkin(){
		if(document.forms[0].key.value == ''){
			alert('記事キーが入力されていません');
			return(false);
		}
		return(true);
	}
--></script>

<form action="$ini::scriptedt?mode=rewrite" method=POST accept-charset="euc-jp" onSubmit="return chkin()">
<fieldset class="edtform"><legend>記事修正</legend>
	<table border=0>
		<tr><th><label class="requisite" for="fmname">Name</label></th>
		<td><input type=text name="name" size=30 value="$name" class="in" id="fmname"></td>
		<th>Mail</th><td><input type=text name="email" size=30 value="$email" class="in"></td></tr>
		<tr><th>Title</th>
		<td><input type=text name="subj" size=40 value="$subj" class="in"></td>
		<th>　Key</th><td><var>$pwd</var></td></tr>
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
		<input type=radio name="color" value="" checked><span style="color:$color">■</span><input type=text name="color2" value="$color" size=10 class="in"><a href="javascript:colsel()"><small>選択</small></a>
	</div>
	<p>@{[ &ins_icolist(\$icon) ]}</p>
	<p><!--  記事特定用の内部値(編集厳禁) -->
		投稿日：<input type="hidden" name="date" value="$date"><var>$date</var><br>
		スレッド番号：<var>$number</var>, 
		記事シリアル：<input type="hidden" name="seri" value="$seri"><var>$seri</var><br>
		@{[ ($::ADMINFLAG) ? "IPアドレス：<var>$ipaddr</var>" : undef ]}
	</p>
	<hr>
	<p>@{[ ($::ADMINFLAG) ? '管理人編集モード' : '投稿時の記事キー']} 
		<input type=text name="key" value="$::FORM{key}" size=25 class="in">
	 　　<input type=submit value="　　記事を修正して投稿　　"><input type=reset value="リセット"></p>
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
	$b .= qq!\t\t<option value="$$picon">変更しない　　（@{[ $$picon || 'なし']}）\n!;
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
		$b .= (($arr->[$_] ne '*') ? qq!<input type=radio name="color" value="$arr->[$_]"><span style="color:$arr->[$_]">■</span>! : '<br>');
	}
	return $b;
}





###---------
##■ 実際に編集/削除
package EditLog;

# 記事書換時、入力項目のチェック
sub check_input
{
	($::FORM{key}) || &::error('記事キーが入力されていません。');
	($::ADMINFLAG) || ($ini::useredit) || &::error('一般ユーザーの記事編集は不許可に設定されています。');
	($::FORM{date} && $::FORM{seri}) || &::error('致命的エラー：内部値が不足しています');

	$::FORM{color} ||= $::FORM{color2};

	# 入力項目のチェック
	($::FORM{name})    || &::error('名前が入力されていません。');
	($::FORM{comment}) || &::error('コメントが入力されていません。');
	($::FORM{color}) || &::error('文字色が入力されていません');
	($::FORM{url} && $::FORM{url} !~ s!^http://!!) && &::error('申し訳ありませんが、http://以外のスキーマには対応していません。');

	# 外部参照を排除
	(index($::FORM{icon},'/') < 0 ) || die 'アイコンリストが不正です';
	($::FORM{icon} ne '*') || &::error('アイコンの選択が不正：グループ見出しになってます');

	# EUCじゃないと
	my($key);
	while ($key = each(%::FORM)) {
		&jcode::convert( \$::FORM{$key}, 'euc');

		# ;が無いのに&はおかしい
		$::FORM{$key} =~ s/&/&amp;/og if(index($::FORM{$key},';') < 0);

		unless($ini::allowtag && $key eq 'comment') {
			$::FORM{$key} =~ s/</&lt\;/go;
			$::FORM{$key} =~ s/>/&gt\;/go;
			$::FORM{$key} =~ s/"/&quot;/go;
			$::FORM{$key} =~ s/'/&#39;/go;
		}else{
			(index($::FORM{$key},'<!--#') < 0 ) || &::error('SSIタグ禁止');  #-->
		}
	}

	# 値をエンコード
	if ($ini::allowtag){
		# <がないのに>がある時は引用と見なす
		$::FORM{comment} =~ s'>'&gt;'g  if(index($::FORM{comment},'<') < 0);
	}elsif ($ini::plug_grad){
		# <gd>は許可
		$::FORM{comment} =~ s'&lt;gd&gt;'<gd>'ig;
		$::FORM{comment} =~ s'&lt;/gd&gt;'</gd>'ig;
	}
	$::FORM{comment} =~ s/\x0D\x0A/<br>/og;
	$::FORM{comment} =~ s/\x0D/<br>/og;
	$::FORM{comment} =~ s/\x0A/<br>/og;
	$::FORM{color} =~ tr/A-Z/a-z/;
}

# パスワード照合処理
sub decide_key
{
	my($pwd,$headflag) = @_;

	$pwd =~ tr/\x0D\x0A//d;

	if($::ADMINFLAG) {
		;
	}elsif(!$::FORM{key}){
		&::error('記事キーを入力してください。',$headflag);
	}elsif(!$pwd){
		&::error('この記事には記事キーが設定されていません。',$headflag);
	}else{
		(crypt($::FORM{key}, substr($pwd, ((index($pwd, '$1$') == 0) ? 3 : 0) ,2) ) eq $pwd) || &::error('記事キーが違います。',$headflag);
	}
}


# ログを実際に修正書換
sub rewrite
{
	my $logobj = new LogReader;

	my $fl = new FileLock;
	$fl->lock;
	open(OUT,">$fl->{out}") || die "ロック失敗（$fl->{out}作成失敗）";
	print OUT $logobj->{head};			# ヘッダは手つかず

	# アイコンランダム設定
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

			# hit判定
			(substr($line,0,4) eq $::FORM{seri}) || next;
			($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);
			($date eq $::FORM{date}) || last EDT;		# 他人が変更していないか

			$hitflag = 1;

			# パスワードを照合
			&decide_key($pwd);

			# 編集期限をチェック
			($::ADMINFLAG) || &decide_edtlim($date) || &::error('編集期限を過ぎています');

			# コメント加工
			&mark_quote(\$::FORM{comment}) if($ini::markquote);
			&http_autolink(\$::FORM{comment}) if($ini::autolink);

			# 更新データーを付加
			my($edtcnt,$edttime) = split(/,/,$edt,2);
			$edtcnt++;
			$edttime = &get_nowdate;

			# 書き換え
			$line = "$seri\t$number\t$date\t$::FORM{name}\t$::FORM{subj}\t$::FORM{comment}\t$::FORM{color}\t$::FORM{email}\t$::FORM{url}\t$::FORM{icon}\t" . "$edtcnt,$edttime" ."\t$ipaddr\t$pwd";
			$line =~ tr/\x0D\x0A//d;
			$line .= "\n";
		}

		print OUT $line;
	}
	($hitflag) || &::error("編集対象の記事を発見できませんでした (no  $::FORM{seri})");

	undef($logobj);
	close(OUT);
	$fl->unlock;
}

# ４８時間経過すると編集不可に。OKなら1を返す
sub decide_edtlim
{
	($ini::useredit == 2) || return 1;

	my($date) = @_;
	my($year,$mon,$mday,$hour,$min,$sec) = unpack('A2xA2xA2xA2xA2xA2', $date);
	$year += 2000; $mon--;					# 2100年問題が発生

	my($wtime) = main::timelocal($sec,$min,$hour,$mday,$mon,$year);
	((time - $wtime) < 60*60*48 ) || return 0;
	return 1;
}
# 引用行をピックアップ
sub mark_quote
{
	my($in) = @_;
	(index($$in,'|') > -1) || (index($$in,'＞') > -1) || (index($$in,'&gt;') > -1) || (index($$in,'｜') > -1) || return;

	my($str,$doc,$eol);
	while($$in =~ /(.*?)($|<br>)/gso  ){
		$doc = $1; $eol = $2;
		if($doc =~ /^(\||＞|｜|&gt;)/ ){
			$str .= "<q>$doc</q>$eol";
		}else{
			$str .= $doc . $eol;
		}
	}
	$$in = $str;
}

# 自動リンク  cite:perl-memo
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
# 日時の取得
sub get_nowdate
{
	$ENV{TZ} = 'JST-9';
	my($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time);
	return sprintf('%02d/%02d/%02d %02d:%02d:%02d',
					$year % 100 ,++$mon,$mday,$hour,$min,$sec);
}


# 削除処理実行
sub erase
{
	# check input
	scalar(@{$::FORM{sel}}) || &::error('削除する記事を選択して下さい。');
	($::FORM{key})   || &::error('記事キーが入力モレです。');
	($::ADMINFLAG) || (scalar(@{$::FORM{sel}}) == 1) || &::error('一度に複数の記事を削除することはできません。');

	my $logobj = new LogReader;

	# 親記事カウンタを調整
	foreach (@{$::FORM{sel}}){
		( substr($_,0,1) eq '*' ) && $logobj->{oya_num}--;
	}

	my $fl = new FileLock;
	$fl->lock;
	open(OUT,">$fl->{out}") || die "ロック失敗（$fl->{out}作成失敗）";

	# ヘッダ書き出し
	print OUT "[ealis3],$logobj->{oya_num},$logobj->{oya_last},$logobj->{seri_last},$logobj->{lastwrite}\n";

	# 削除処理
	my($del_num,$verify_pwd,$flag,$line,$oyaflag,$delcnt);
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd);
	while($line = $logobj->lread()) {
		$flag = 0;
		($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) = split("\t",$line);

		foreach (@{$::FORM{sel}}) {
			if ($_ eq $seri) {
				($::ADMINFLAG) || &decide_edtlim($date) || &::error('編集期限を過ぎています');
				$delcnt++;
				$flag = 1;
				$del_num = $number;
				$verify_pwd = $pwd;
				(substr($seri,0,1) eq '*') && ($oyaflag = 1);
			}elsif($oyaflag == 1 && $del_num eq $number) {
				($::ADMINFLAG) || &::error('返信の付いた親記事は管理人しか削除できません。');
				$flag = 1;
			}
		}
		($flag) || print OUT $line;
	}
	close(IN);
	($del_num) || &::error('削除対象記事が見つかりませんでした');
	($delcnt == scalar(@{$::FORM{sel}})) || &::error('削除対象記事のマッチ数が食い違ったので、念のため処理を中止しました。');

	# 削除実行OKか決定
	&decide_key($verify_pwd);

	undef($logobj);
	close(OUT);
	$fl->unlock;
}


### -------------
## ログを読む＆ヘッダ情報
package LogReader;
sub new
{
	my($p) = {};

	open(IN,"$ini::logfile") || die "ログファイル「$ini::logfile」が開けません";
	$_ = scalar(<IN>);
	$p->{head} = $_;
	chomp($_);

	split(/,/,$_,5);
	(shift eq '[ealis3]') || die 'ealis 第３世代のログではありません';
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
## flock&rename でのロック
package FileLock;
# lockfileに対してロック
sub new
{
	(-f "$ini::lockfile") || die "$ini::lockfile は作っておいてねん";

	open(LOCK, "+<$ini::lockfile") || die "$ini::lockfile が開けません";
	eval{ flock(LOCK, 2); };
	truncate(LOCK, 0);
	print LOCK  scalar(time) . " ($$)";

	bless {};
}
# tempを作成
sub lock
{
	my($obj) = @_;

	$obj->{out} = "$ini::logdir/$$\.tmp";
	open(OUT,">$obj->{out}") || die "temporary file 作成失敗（permission？）";
	close(OUT);
	chmod 0666,$obj->{out};
}
sub unlock
{
	my($obj) = @_;

	REN:{
		# tempをリネーム
		rename($obj->{out},"$ini::logfile") || last REN;
		(! -f $obj->{out}) || last REN;

		close(LOCK);
		return;
	}
	&::error("リネームに失敗しました(MS-IIS?)。<br>.tmpとして失敗したログがあるかもしれません。<blockquote> $!</blockquote>");
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
