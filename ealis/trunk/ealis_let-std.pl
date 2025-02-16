# ealis ver.3.0   Lettering engine
#  --  "neo ealis-std" type
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC入)

@leteng_contains = ();

sub leteng_lettering
{
	my($ATC,$oyaflag,$rescnt) = @_;

	if($oyaflag){
		print qq!\n<hr class="atclhr">\n\n<div class="article">\n!;

		print "\t<h3>";
		printf( '<span class="pageing"><a href="#see%d">∧</a><a href="#see%d" accesskey="%1d">∨</a></span>',
				$ANKOR -1 , $ANKOR +1 , $ANKOR -1 ) unless($FORM{pick});
		print "\n";
		print qq!\t\t<span class="atclno" id="see$ANKOR">$ATC->{number}</span> : <em>$ATC->{subj}</em>　\n!;
		print qq!\t\t/ <cite class="name">$ATC->{name}</cite>　<span class="stamp">($ATC->{date})</span>　!;
		print qq!$ATC->{url}</h3>\n\n!;

		print qq!\t\t<div class="atclbody">\n!;
		print qq!\t<img src="$ini::imgpath$ATC->{icon}" align=right class="ico" alt="$ATC->{icon}">\n! if($ATC->{icon});
		print qq!\t<p class="msg-oya" style="color: $ATC->{color}">$ATC->{comment}</p>\n!;


	}else{
		if($rescnt == 1) { print qq!\n\t<ul class="msg-res">\n!;}

		print qq!\t\t<li style="color:$ATC->{color}"><cite>$ATC->{name}</cite>&gt;!;
		print qq! $ATC->{comment} <span class="stamp">($ATC->{date})</span></li>\n!;
	}
}


sub leteng_resform
{
	my($ATC,$rescnt) = @_;

	print "\t</ul>\n" if($rescnt);
	print "\t</div>\n";

	print qq!\t<div class="reslink">!;
	print qq!<a href="javascript:view('NO$ATC->{number}');" accesskey=R>レス欄生成▼</a>! if(defined($FORM{dhtml}));
	print "</div>\n</div>\n";

	# pick mode
	if (defined($FORM{pick})){
		print qq!<form method=POST action="$ini::scriptwri?resno=$ATC->{number};thread" class="resform" accept-charset="euc-jp">\n!;

		print qq!\t<table summary="res $ATC->{number}" border=0><tbody><tr>\n!;
		print qq!\t<td><label class="requisite">Name <input type=text name="name" size=12 value="$COOKIE{name}" class="in"></label>　　\n!;
		print qq!\t\tkey <input type=text name="pwd" size=9 maxlength=8 value="$COOKIE{pwd}" class="in" style="ime-mode:disabled">\n!;
		print qq!\t</td>\n!;
		print qq!\t<td class="submit"><input type=submit value="　返信　"></td></tr>\n!;
		print qq!\t<tr><td colspan=2>\n!;
		print qq!\t<textarea cols=70 rows=7 name="comment" wrap=soft accesskey=R></textarea><br>\n!;

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
		printf qq|<script type="text/javascript"><!--\n\t dhtmlres(%d,%d);\n// --></script>\n|
				,$ATC->{number},$ANKOR-1;

	# Normal mode
	}else{
		print qq!<form method=POST action="$ini::scriptwri?resno=$ATC->{number}" class="resform" accept-charset="euc-jp">\n!;
		print qq!\t<table summary="res $ATC->{number}" border=0><tbody>\n!;
		print qq!\t<tr>\n!;
		print qq!\t\t<th><span class="requisite">Name</span></th>\n!;
		print qq!\t\t<td><input type=text name="name" size=8 value="$COOKIE{name}" class="in"></td>\n!;
		print qq!\t\t<td rowspan=2><textarea cols=68 rows=3 name="comment" accesskey=R></textarea></td>\n!;

		printf "\t\t<td>@{[ $sozai->irolist() ]}</td>\n";

		print qq!\t</tr><tr>\n!;
		print qq!\t\t<th>key</th>\n!;
		print qq!\t\t<td><input type=text name="pwd" size=8 maxlength=8 value="$COOKIE{pwd}" class="in" style="ime-mode:disabled"></td>\n!;
		print qq!\t\t<td class="submit"><input type=submit value=" 返信 "></td>\n!;
		print qq!\t</tr></tbody></table>\n!;
		print qq!</form>\n\n!;
	}
}



sub leteng_jscript
{
	defined($FORM{dhtml}) || return;

	printf <<'EOM' ,$ini::scriptwri,$COOKIE{name},$COOKIE{pwd},  $sozai->enc('iroradio');

 function dhtmlres(num,form){
	document.writeln('<div class="resform" style="display:none" id="NO'+ num +'">');
	document.writeln('<form method=POST action="%s?resno='+ num +';dhtml" class="resform" accept-charset="euc-jp">');
	document.writeln('<table summary="res" border=0><tbody><tr>');
	document.writeln('<td><label class="requisite">Name <input type=text name="name" size=12 value="%s" class="in"><\/label>　　');
	document.writeln('key <input type=text name="pwd" size=9 maxlength=8 value="%s" class="in" style="ime-mode:disabled">');
	document.writeln('<\/td>');
	document.writeln('<td class="submit"><input type=submit value="　返信　"><\/td><\/tr>');
	document.writeln('<tr><td colspan=2>');
	document.writeln('<textarea cols=70 rows=7 name="comment" wrap=soft><\/textarea><br>');
	document.writeln('<div class="list-colors">');
	document.writeln('<a href="javascript:prevtxt(' + form + ')">&lt;color&gt;<\/a>');
	document.writeln('%s');
	document.writeln('<\/div><\/td><\/tr>');
	document.writeln('<\/table><\/form><\/form><\/div>');
 }

EOM
}

1;
