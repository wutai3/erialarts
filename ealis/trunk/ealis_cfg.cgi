# ealis ver.3.0   configuration  (02/03/10)
# (EUC ��)

package ini;

## ����������

	$title = 'my ealis';		# TITLE����
	$h1 = ' - my ealis -';

	$backurl = 'http://www.barfoo.ne.jp/~hogehoge/';		# "���"��URL
	$cssfile = 'http://www.barfoo.ne.jp/~hogehoge/cgi-bin/ealis/ealis.css';	# (���Хѥ�)
 	$locate  = 'http://www.barfoo.ne.jp/~hogehoge/cgi-bin/ealis/';

	$allowtag = 1;				# �����ε���(0or1)
	$pass = 'foobar';			# �������ѥޥ����ѥ����(�ѿ���)

	$imgpath = 'img/';			# ����������֤�DIR(http�����)

## �������ƥ�����

	$res_sort = 1;				# �ֿ����Ĥ��ȿƵ�����ǽ�� (0or1)
	$autolink = 1;				# ��ư��� (0or1)
	$refcheck = 0;				# ¾�����Ȥ�������ӽ�������˻��� (0or1)
	$useredit = 2;				# �桼�����ˤ�뵭�����������
								#  0:off 1:on 2:�������ְ���
	$markquote = 1;				# ���ѹԤ�ޡ������å�

	$logmax = 50;				# �Ƶ����κ��絭���� (���ޤ�¿������ȴ�)
	$show = 8;					# ��page������ε���ɽ���� (�Ƶ���)

	# ���ݤ���ip���������׸�����
	@deniedaddrs = ('');

#	$gzip = '/bin/gzip';

	$logdir = '.';				# ����DIR��[777]������
	$lockfile = "$logdir/ealis.lock";	
	$logfile = "$logdir/ealis.log";

	# ��������
#	$pnumfile = "$logdir/ealis_log.db";		# NO�ե�����ʲ������׻������
	$pastdir = '.';				# ����DIR�ʺǸ��/�����ס�
	$pastsize = '100';					# �������ե�����Υ�������*1024byte��
#	$pasthttp = 'http://homepage1.nifty.com/member/��/';		# @nifty�ʤ�

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

	# �ڡ����女����
	$headcom = '';

	# �ڡ�����������
	$footcom = '';


## ���Ǻ�����
package Sozai;
# ʸ�����ꥹ�� �ʥ����ɡ�̾���ˤν�ˡ����Ԥ�"*"2�ĥڥ�
@colpalet = qw[
	#38689E ��ɸ
	#56638f ����
	#9381BC ƣ��
	#C92F93 ��ð
	#EE7C9A ���

	#99A279 ����
	#747474 ����
	#7D9174 ����
	#5A5B59 ����
	#23693D ����

	#7BB595 ����
	#6999ae ��Ǭ
];#�����ޤ�

##	# ��������ꥹ�� �ʥե�����̾��̾���ˤν�ˡ�����"*",���롼�פ�"**",�������*RAND*
##	@icopalet = qw[
##		*				�ʤ�
##		saus3_01.gif	����դ���
##		saihusa1.gif	�ɽ񤦤�
##		saiusa3.gif		��ǭ�Ȥ���
##	];#�����ޤ�
