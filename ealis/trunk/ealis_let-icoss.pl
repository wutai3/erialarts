# ealis ver.3.0   Lettering engine
#  --  "iconboard with ressubj" steppost type.
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC 入)

@leteng_contains = ('icon','subj');

sub leteng_lettering	#let-icoと同じ
{
	my($ATC,$oyaflag,$rescnt) = @_;

	# アイコン非選択時
	$ATC->{icon} ||= 'undef.png';

	if($oyaflag){
		print qq!\n<hr class="atclhr">\n\n<div class="article">\n!;

		print "\t<h3>";
		printf( '<span class="pageing"><a href="#see%d">∧</a><a href="#see%d" accesskey="%1d">∨</a></span>',
				$ANKOR -1 , $ANKOR +1 , $ANKOR -1 ) unless($FORM{pick});
		print "\n";
		print qq!\t\t<span class="atclno" id="see$ANKOR">$ATC->{number}</span> : <em>$ATC->{subj}</em>　\n!;
		print qq!\t\t/ <cite>$ATC->{name}</cite>　<span class="stamp">($ATC->{date})</span>　$ATC->{url}</h3>\n\n!;

		print qq!\t<div class="atclbody">\n!;
		print qq!\n\t<table class="msg-oya" summary="article $ATC->{number}"><colgroup><col class="ico"><col class="msg"></colgroup>\n!;
		print qq!\t\t<tr><td><img src="$ini::imgpath$ATC->{icon}" alt="$ATC->{icon}"></td>!;
		print qq!<td style="color: $ATC->{color}">$ATC->{comment}</td></tr></table>\n!;

	}else{
		if($rescnt == 1) { print qq!\n\t<table class="msg-res" summary="res for $ATC->{number}"><colgroup><col class="ico"><col class="msg"></colgroup>\n!;}

		print qq!\t\t<tr><td><img src="$ini::imgpath$ATC->{icon}" alt="$ATC->{icon}"></td>!;
		print qq!<td><h4>ο　<em class="subj">$ATC->{subj}</em>　/ <cite>$ATC->{name}</cite>　<span class="stamp">($ATC->{date})</span>　$ATC->{url}</h4>!;
		print qq!<p class="msg-res" style="color:$ATC->{color}">$ATC->{comment}</p></td></tr>\n!;
	}
}



sub leteng_resform
{
	my($ATC,$oyaflag,$rescnt) = @_;

	print "\t</table>\n" if($rescnt);
	print "\t</div>\n";

	print qq!\t<div class="reslink">!;
	if(defined($FORM{dhtml})){
		print qq!<a href="javascript:view('NO$ATC->{number}');">レス欄生成▼</a>!;
	}elsif(!$FORM{pick}){
		print qq!<a href="$ini::scriptmain?normal;pick=$ATC->{number}">記事に返信▼</a>!;
	}
	print "</div>\n</div>\n\n";


	# pick/step mode
	if ($FORM{pick}){
		print qq!<form method=POST action="$ini::scriptwri?resno=$ATC->{number};!;
		print 'thread' if(!defined($FORM{normal}));
		print qq!" class="resform" accept-charset="euc-jp">\n!;

		print qq!\t<table summary="res"><tbody><tr>\n!;
		print qq!\t<td><span class="requisite">Name</span> <input type=text name="name" size=12 value="$COOKIE{name}" class="in">　\n!;
		print qq!\tTitle <input type=text name="subj" size=40 value="" class="in">　\n!;
		print qq!\tkey <input type=text name="pwd" size=9 maxlength=8 value="$COOKIE{pwd}" class="in" style="ime-mode:disabled"></td>!;

		print qq!\t<td class="submit"><input type=submit value="　返信　"></td></tr>\n!;
		print qq!\t<tr><td colspan=2>\n!;
		print qq!\t<textarea cols=70 rows=6 name="comment" wrap=soft></textarea><br>\n!;
		print qq!\t Mail <input type=text name="email" size=28 value="$COOKIE{email}" class="in" style="ime-mode:disabled"> !;
		print qq!\tURL <input type=text name="url" size=28 value="http://$COOKIE{url}" class="in" style="ime-mode:disabled">　@{[ $sozai->icolist() ]}!;

		print qq!\t<div class="list-colors">\n!;

		print qq|<script type="text/javascript"><!--\n\t\t|;
		print q! document.writeln('<a href="javascript:prevtxt(0)">&lt;color&gt;</a>');!;
		print qq!\n\t//--></script>!;
		print qq!<noscript><a href="$ini::scriptsub?prev_color" target="elsprv">&lt;color&gt;</a></noscript>!;

		print $sozai->iroradio();
		print qq!\t</div></td></tr>\n!;
		print qq!\t</table>\n!;

		print qq!</form>\n\n!;


	# DHTML mode
	}elsif(defined($FORM{dhtml})){
		printf qq!<script type="text/javascript"><\!--\n\t dhtmlres(%d,%d);\n// --></script>\n!
				,$ATC->{number},$ANKOR-1;

	# Normal mode
	}else{
		;
	}
}

sub leteng_jscript
{
	# dhtml時のみ有効
	defined($FORM{dhtml}) || return;

	printf <<'EOM' ,$ini::scriptwri,$COOKIE{name},$COOKIE{pwd},$COOKIE{email},$COOKIE{url}, $sozai->enc('icolist'), $sozai->enc('iroradio');

 function dhtmlres(num,form){
	document.writeln('<div class="resform" style="display:none" id="NO'+ num +'">');
	document.writeln('<form method=POST action="%s?resno='+ num +';dhtml" class="resform" accept-charset="euc-jp">');
	document.writeln('<table summary="res"><tbody><tr>');
	document.writeln('<td><label class="requisite">Name <input type=text name="name" size=12 value="%s" class="in"><\/label>　');
	document.writeln('Title <input type=text name="subj" size=40 value="" class="in">');
	document.writeln('key <input type=text name="pwd" size=9 maxlength=8 value="%s" class="in" style="ime-mode:disabled"><\/td>');
	document.writeln('<td class="submit"><input type=submit value="　返信　"><\/td><\/tr>');
	document.writeln('<tr><td colspan=2>');
	document.writeln('<textarea cols=70 rows=6 name="comment" wrap=soft><\/textarea><br>');
	document.writeln('Mail <input type=text name="email" size=28 value="%s" class="in" style="ime-mode:disabled">');
	document.writeln('URL <input type=text name="url" size=28 value="http://%s" class="in" style="ime-mode:disabled">');
	document.writeln('%s');
	document.writeln('<div class="list-colors">');
	document.writeln('<a href="javascript:prevtxt(' + form + ')">&lt;color&gt;<\/a>');
	document.writeln('%s');
	document.writeln('<\/div><\/td><\/tr>');
	document.writeln('<\/table><\/form><\/div>');
 }

EOM
}


sub leteng_pwrite_jikken
{
	my $obj = shift;
	my($seri,$number,$date,$name,$subj,$comment,$color,$email,$url,$icon,$edt,$ipaddr,$pwd) 
		= split("\t",${shift()});
	my($oyaflag) = ((substr($seri,0,1) eq '*') ? 1 : 0 );

	($subj) ||= '(無題)';
	($url) &&= qq!<a href="http://$url" target="_top" class="web">[url]</a>!;
	($email) && ($name = qq!<a href="mailto:$email">$name</a>!);
	($ini::autolink) && &PastLog::http_autolink(\$comment);

	if( $oyaflag ){
		# 複数の親子記事群を吐く際に必要
		if($obj->{appentflag}){
			print PLOG qq!\t</ul>\n</div>\n<hr class="atclhr">\n!;
		}else{
			$obj->{appentflag} = 1;
		}

		print PLOG qq!\t<h3 id="msg$number">XX<span class="atclno">$number</span> : <em>$subj</em>　!;
		print PLOG qq!/ <cite>$name</cite>　<span class="stamp">($date)</span>　$url </h3>!;
		print PLOG qq!<div class="atclbody">!;
		print PLOG qq!<p style="color: $color" class="msg-oya">$comment</p>\n!;

		print PLOG qq!\t<ul class="msg-res">\n!;
	}else{
		print PLOG qq!\t\t<li style="color: $color"><cite>$name</cite>&gt; !;
		print PLOG qq!$comment <span class="stamp">($date)</span></li>\n!;
	}
}
1;