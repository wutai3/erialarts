# ealis ver.3.0   configuration  (02/03/10)
# (EUC 入)

package ini;

## ■基本設定

	$title = 'my ealis';		# TITLEタグ
	$h1 = ' - my ealis -';

	$backurl = 'http://www.barfoo.ne.jp/~hogehoge/';		# "戻る"のURL
	$cssfile = 'http://www.barfoo.ne.jp/~hogehoge/cgi-bin/ealis/ealis.css';	# (絶対パス)
 	$locate  = 'http://www.barfoo.ne.jp/~hogehoge/cgi-bin/ealis/';

	$allowtag = 1;				# タグの許可(0or1)
	$pass = 'foobar';			# 管理者用マスタパスワード(英数字)

	$imgpath = 'img/';			# アイコンを置くDIR(http指定可)

## ■システム設定

	$res_sort = 1;				# 返信がつくと親記事を最初に (0or1)
	$autolink = 1;				# 自動リンク (0or1)
	$refcheck = 0;				# 他サイトから投稿排除する時に指定 (0or1)
	$useredit = 2;				# ユーザーによる記事修正を許可
								#  0:off 1:on 2:４８時間以内
	$markquote = 1;				# 引用行をマークアップ

	$logmax = 50;				# 親記事の最大記事数 (あまり多くすると危険)
	$show = 8;					# １page当たりの記事表示数 (親記事)

	# 拒否するip（前方一致検索）
	@deniedaddrs = ('');

#	$gzip = '/bin/gzip';

	$logdir = '.';				# このDIRは[777]に設定
	$lockfile = "$logdir/ealis.lock";	
	$logfile = "$logdir/ealis.log";

	# 過去ログ設定
#	$pnumfile = "$logdir/ealis_log.db";		# NOファイル（過去ログ不要時空欄）
	$pastdir = '.';				# 過去ログDIR（最後の/は不要）
	$pastsize = '100';					# 過去ログ１ファイルのサイズ（*1024byte）
#	$pasthttp = 'http://homepage1.nifty.com/member/…/';		# @niftyなど

	# call list
	$scriptmain = 'ealis.cgi';
	$scriptwri = 'ealis_wri.cgi';
	$scriptsub = 'ealis_sub.cgi';
	$scriptedt = 'ealis_edt.cgi';
	$scriptlog = 'ealis_log.cgi';

	$leteng = './ealis_let-std.pl';

#	$plug_plus = './ealis_plus.cgi';
#	$plug_cnt = './ealis_cnt.pl';
#	$plug_mail = './ealis_mail.pl';
#	$plug_grad = './ealis_grad.pl';
#	$plug_chtm = './ealis-i.cgi';

#	$homeicon = 'web';

	# ページ上コメント
	$headcom = '';

	# ページ末コメント
	$footcom = '';


## ■素材設定
package Sozai;
# 文字色リスト （コード、名前）の順に。改行は"*"2つペア
@colpalet = qw[
	#38689E 浅標
	#56638f 藍鼠
	#9381BC 藤色
	#C92F93 牡丹
	#EE7C9A 撫子

	#99A279 抹茶
	#747474 銀鼠
	#7D9174 川鼠
	#5A5B59 薄墨
	#23693D 常磐

	#7BB595 千草
	#6999ae 錆葱
];#ここまで

##	# アイコンリスト （ファイル名、名前）の順に。空は"*",グループは"**",ランダムは*RAND*
##	@icopalet = qw[
##		*				なし
##		saus3_01.gif	落ち葉うさ
##		saihusa1.gif	読書うさ
##		saiusa3.gif		子猫とうさ
##	];#ここまで
