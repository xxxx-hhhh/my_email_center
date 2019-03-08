{% if type!="email_mission" %}
<script>

var comment_set = new Set()

function get_status(){
    var temp = function(){
        $.ajax({
            type : "post",
            url : '/api/mission_status',
            data : JSON.stringify({{ mission_comments }}),
            contentType : "application/json",
            dataType : "json",
            success :
                function(obj){
                    $('td[status="running"]').each(
                        function(){
                            if (!(this.id in obj)){
                                location.reload();
                                return
                            };
                        });
                    for (comment in obj){
                            if (!(comment in comment_set)){
                                var elem = $('#'+comment);
                                if(elem.attr('id') == comment){
                                    elem.attr('status', 'running');
                                    elem.children('img').show();
                                    elem.children('p').hide();
                                    comment_set.add(comment);
                            };
                        };
                    };
                }
            })
    };
    // 延时递增到10s保持频率
    temp()
    setTimeout(function(){
        temp();
        setTimeout(function(){
            temp();
            setTimeout(function(){
                temp();
                setTimeout(function(){
                    temp();
                    setInterval(temp, 10000);
                }, 8000);
            }, 5000);
        }, 2000);
    }, 1000)
}

$(document).ready(function(){
    get_status()
});
</script>
{% endif %}