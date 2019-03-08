<script src="https://cdn.bootcss.com/echarts/4.2.1-rc1/echarts-en.common.js"></script>
<script type="text/javascript">

function summary(system_status){
    // 基于准备好的dom，初始化echarts实例
    var myChart = echarts.init(document.getElementById('chart'));
    option = {
        title: {
            text: "内存总体使用情况",
        },
        tooltip: {
            trigger: 'item',
            formatter: "{b} : <br/>{c}MB ({d}%)"
        },
        legend: {
            orient: 'vertical',
            x: 'right',
            data:['剩余内存大小','已使用内存大小']
        },
        series: [
            {
                name:'内存总体使用情况',
                type:'pie',
                radius: ['50%', '70%'],
                avoidLabelOverlap: false,
                label: {
                    normal: {
                        show: false,
                        position: 'center'
                    },
                    emphasis: {
                        show: true,
                        textStyle: {
                            fontSize: '15',
                            fontWeight: 'bold'
                        }
                    }
                },
                labelLine: {
                    normal: {
                        show: false
                    }
                },
                data:[
                    {value: system_status['available'], name: '剩余内存大小'},
                    {value: system_status['used'], name: '已使用内存大小'},
                ]
            }
        ]
    };
    // 使用刚指定的配置项和数据显示图表。
    myChart.setOption(option);
};

function detail(mission_status){
    var content = '';
    for (st in mission_status){
        var st = mission_status[st];
        content += '<tr>\
                       <td>' + st[0] + '</td>\
                       <td>\
                          <div class="progress progress-striped">\
                              <div class="progress-bar" style="width: ' + st[1] + '%;">\
                                    <p style="color: black;">' + st[1] + '%</p>\
                              </div>\
                          </div>\
                       </td>\
                       <td>\
                          <a class="attention" href="javascript:;" onclick="if(confirm(\'确定杀死进程吗\')){location.href=\'/api/kill_mission?comment=' + st[0] + '\';}">杀死进程</a>\
                       </td>\
                    </tr>';
        }
    $('#tbody').html(function(i, ot){
        return content;
    });
};

function top5_mp(mp){
    var content = '';
    for (pi in mp){
        var process = mp[pi];
        content += '<tr>\
                       <td>' + process[0] + '</td>\
                       <td class="cmd-omit" title="' + process[1] + '">' + process[1] + '</td>\
                       <td>\
                          <div class="progress progress-striped">\
                              <div class="progress-bar" style="width: ' + process[2] + '%;">\
                                    <p style="color: black;">' + process[2] + '%</p>\
                              </div>\
                          </div>\
                       </td>\
                       <td>' + process[3] + '</td>\
                    </tr>';
        }
    $('#top5>table>tbody').html(content);
};


function set_content(){
    var temp = function(){
         $.ajax({
            type : "post",
            url : '/api/system_status',
            data : {},
            dataType : "json",
            success : function(data){
                summary(data['system_status']);
                detail(data['mission_status']);
                top5_mp(data['top5_memory_percent'])
            }
         });
    };
    temp();
    setInterval(temp, 3000);
}

$(document).ready(function(){
    set_content();
});

</script>