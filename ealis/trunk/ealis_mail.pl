# ealis ver.3.0   mail plugin
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC 入)

package PlugMail;

# ここを設定。
$ini::mailto = 'hogehoge@foobar.ne.jp';
$ini::sendmail = '/usr/bin/sendmail';


sub send
{
	my($form,$nowdate) = @_;

	($ini::mailto ne $form->{email}) || return;		# 自分の投稿は通知しない
	(-x $ini::sendmail) || &::error("$ini::sendmailがありません。");

	# ヘッダを作成
	my($mail_head) = {
		To				=> $ini::mailto,
		From			=> &encode_jmime($ini::title) . " <$ini::mailto>",
		'Reply-To'		=> $ini::mailto ,
		Subject			=> '[bbsnew] ' . &encode_jmime( &format_subj($form) ),
		'X-Mailer'		=> 'ealis mailunit v3.0',
		Type			=> 'text/plain; charset="iso-2022-jp"',
		'Content-Transfer-Encoding' => '7bit'
	};

	# 送信開始！
	open(MAIL,"| $ini::sendmail $ini::mailto") || &::error('sendmailが開けません');
	while (($name, $value) = each(%{$mail_head})) {
		printf MAIL "%s: %s\n",  $name, $value;
	}
	print MAIL "\n";
	print MAIL &format_honbun($form,$nowdate);
	close(MAIL);
}


# private class ------------
sub format_subj
{
	my($form) = @_;

	# 親記事の時
	if(!$form->{resno}){
		return ($form->{subj} || '無題');
	# 返信記事の時
	}else{
		return ($form->{subj}) ? "$form->{subj}: (re:$form->{resno})" : "Res Message: $form->{resno}";
	}
}
sub format_honbun
{
	my($form,$nowdate) = @_;

	my($msg) = $form->{comment};
	$msg =~ s/<br>/\n/ig;
	$msg =~ s'\&lt\;'<'ig;
	$msg =~ s'\&gt\;'>'ig;

	my($info);
	$info  = qq!『$ini::title』に投稿がありました\n!;
	$info .= qq! -> $ini::locate\n!;
	$info .= qq!----------------------------------------------------------------\n!;
	$info .= qq!TIME : $$nowdate\n!;
	$info .= qq!NAME : $form->{name}\n!;
	$info .= qq!TITLE: @{[ &format_subj  ]} \n!;
	$info .= qq!----------\n\n!;

	return jcode::jis( $info . $msg );
}

sub encode_jmime
{
	my($in) = @_;

	&jcode::euc2jis(\$in);

	$in =~ s/\x1b\x28\x42/\x1b\x28\x4a/g;
	$in = &base64encode($in);

	return '=?iso-2022-jp?B?' . $in . '?=';
}
sub base64encode
{
	my($xx, $yy, $zz, $i);
	my($base) = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

	$xx = unpack('B*', shift);
	for ($i = 0; $yy = substr($xx, $i, 6); $i += 6) {
		$zz .= substr($base, ord(pack('B*', '00' . $yy)), 1);
		$zz .= ((length($yy) == 2) ? '==' : (length($yy) == 4) ? '='  : undef);
	}
	return $zz;
}
1;