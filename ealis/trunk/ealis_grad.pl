# ealis ver.3.0   gradation plugin
# ---  erialarts : https://github.com/wutai3/erialarts/
# (EUC 入)

package GradEngine;
sub new
{
	srand;
	bless { num => int(scalar(@Sozai::colpalet)/2) };
}
sub encode
{
	my($obj,$str) = @_;
	(index($$str, '</gd>' ) > -1) || return;

	$$str =~ s/<br>/\n/igo;
	if($ini::autolink && index($$str,'http://') > -1){
		$str =~ s!([^=^\"]|^)(http\:[\w\.\~\-/\?\&\+\=\:\@\%\;\#]+)!$1</gd><a href="$2" target="_top"><gd>$2</gd></a><gd>!g;
	}
	$$str =~ s!(\G(?:[\x00-\x7F]|[\x8E\xA1-\xFE][\xA1-\xFE]|\x8F[\xA1-\xFE][\xA1-\xFE])*?)<gd>([^<][^<]+)</gd>!$1 . '<span class="grad">' . $obj->engine(\$2) . '</span>'!eg;
	$$str =~ s/\n/<br>/g;

}
sub engine
{
	my($obj,$str) = @_;
	(length($$str) < 512) || return sprintf '&lt;gd&gt;%s&lt;/gd&gt;',$$str;

	my(@input) = $$str =~ /([\x00-\x7F]|[\x8E\xA1-\xFE][\xA1-\xFE]|\x8F[\xA1-\xFE][\xA1-\xFE])/og;

	# in/outを決定
	my($in_col) = (@Sozai::colpalet)[int(rand($obj->{num}))*2];
	my($out_col);
	RND:{
		$out_col = (@Sozai::colpalet)[int(rand($obj->{num}))*2];
		($out_col ne $in_col) || redo RND;
	}

	#(red,green,blue)と展開
	my @in   = map { hex($_)} unpack('xA2A2A2',$in_col);
	my @step = map { hex($_)} unpack('xA2A2A2',$out_col);
	for(0 .. 2){
		$step[$_] = ( $step[$_] - $in[$_] )/$#input;
	}

	my($char_out,$i);
	foreach (@input){
		$_ =~ s'<'&lt\;'go;
		$_ =~ s'>'&gt\;'go;
		if($_ eq ' ' || $_ eq '　' || $_ eq "\n"){
			$char_out .= $_;
		}else{
			$char_out .= sprintf '<font color="#%02X%02X%02X">%s</font>',
				$step[0] * $i + $in[0],
				$step[1] * $i + $in[1],
				$step[2] * $i + $in[2],
				$_;
		}
		$i++;
	}

	return $char_out;
}
1;
