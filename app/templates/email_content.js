<script>
// 自定义正文
function custom_content(){
    $('#myModalLabel').text('自定义正文');
    $('#content-area').val($('#content').val());
}
// 不发送邮件
function no_email(){
    $('#myModalLabel').text('不发送邮件');
    $('#content-area').val('<%no_email%>');
}
// 渲染邮件正文
function render_html(){
    $('#myModalLabel').text('渲染邮件正文');
    $('#content-area').val('<%render_html%>');
}
// 自定义渲染邮件正文(jinja2语法)
var base_template = '\
<%custom_render%>\n\
<--! filename: 生成的文件名(不带后缀) -->\n\
<--! tables: (sheetname, dataframe_table) 二元元组列表 -->\n\
\{\% block title \%\}\{\{ filename \}\}\{\% endblock title \%\}\n\
\{\% block body \%\}\n\
    <div>\n\
        \{\% for sheetname, table in  tables \%\}\n\
        	<h2>\{\{ sheetname \}\}</h2>\n\
        	\{\{ table \}\}\n\
        \{\% endfor \%\}\n\
    </div>\n\
\{\% endblock body \%\}\n\
'
function custom_render(){
    $('#myModalLabel').text('自定义渲染邮件正文(jinja2语法)');
    $('#content-area').val(base_template);
}

// submit
function submit(){
    $('#content').val($('#content-area').val());
}


$(document).ready(function(){
    // 绑定模态框
    $('#content').attr({
        'data-toggle': 'modal',
        'data-target': '#content-modal',
        'style': 'cursor:pointer;',
    });
    // 绑定事件
    $('#content-modal').on('shown.bs.modal', function () {
        $('#content-area').val($('#content').val());
    });
});
</script>