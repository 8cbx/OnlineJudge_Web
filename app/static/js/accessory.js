var s_now, s_init, s_end;
var t = document.getElementById("contest_bar"); //创建时间节点
document.getElementById("contest_bar").parentNode.appendChild(t);
function set_globle (sec_now, sec_init, sec_end) {
      s_now = sec_now, s_init = sec_init, s_end = sec_end;
}
var intermin = setInterval("setting_contest_time(s_now, s_init, s_end)", 1000);
function setting_contest_time (sec_now, sec_init, sec_end) {
    var sec_pass = sec_now - sec_init;
    var sec_whole = sec_end - sec_init;
    var sec_remain = sec_end - sec_now;
    var percent = (sec_pass / sec_whole) * 100;
    var sec_string = (percent).toFixed(2);
    if(percent<=0.0)
    {
    	$("div").children(".progress-bar").removeClass("progress-bar-striped active");
    	$("div").children(".progress-bar").attr("style", "width: 100%");
    	document.getElementById("contest_bar").innerHTML="pending";
    }
    else
    {
        $("div").children(".progress-bar").addClass("progress-bar-striped active");
        var disp = "width: " + sec_string + "%";
        $("div").children(".progress-bar").attr("style", disp);
        if(percent>95.0){
            $("div").children(".progress-bar").attr("style", disp);
            $("div").children(".progress-bar").addClass("progress-bar-danger");
        }
        var h = Math.floor(sec_remain/3600);
        var m = Math.floor(sec_remain%3600/60);
        var s = sec_remain % 60;
        var result;
        if (h < 1) {
             result = m + " m ";
        }
        else {
             result = h + " h " + m + " m ";
        }
        t.innerHTML = result + s + " s"; //更新时间
    }
    sec_now = sec_now + 1;
    if (sec_now >= sec_end) {
        intermin = window.clearInterval(intermin);
        $("div").children(".progress-bar").attr("style", "width: 100%");
        $("div").children(".progress-bar").removeClass("progress-bar-striped active");
        document.getElementById("contest_bar").innerHTML="finished";
        return ;
    };
    s_now = sec_now, s_init = sec_init, s_end = sec_end;
 }
