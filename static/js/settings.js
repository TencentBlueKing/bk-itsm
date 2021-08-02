//-----------------------------------------------------------
/**
 * 调试配置，请只在这个地方进行设置，不要动其他代码
 */
var debug = true; // 是否是调试模式，注意：在上传代码的时候，要改为false
//-----------------------------------------------------------

//以下公用代码区域，使用范围非常广，请勿更改--------------------------------
document.write(" <script lanague=\"javascript\" src=\""+static_url+"assets/artdialog/jquery.artDialog.js?skin=simple\"> <\/script>");
//csrftoken
document.write(" <script lanague=\"javascript\" src=\""+static_url+"js/csrftoken.js\"> <\/script>");
/**
 * ajax全局设置
 */
// 在这里对ajax请求做一些统一公用处理
$.ajaxSetup({
//	timeout: 8000,
	statusCode: {
	    401: function(xhr) {
	    	//ajax 请求 未登录
	    	window.location.reload();
	    },
	    402: function(xhr) {
	    	// 功能开关
	    	var _src = xhr.responseText;
	    	ajax_content = '<iframe name="403_iframe" frameborder="0" src="'+_src+'" style="width:570px;height:400px;"></iframe>';
			art.dialog({
			    title: "提示",
			    lock: true,
			    content: ajax_content
			});
	    	return;
	    },
	    500: function(xhr, textStatus) {
	    	// 异常
	    	if(debug){
	    		alert("系统出现异常("+xhr.status+'):' + xhr.responseText);
	    	}
	    	else{
	    		alert("系统出现异常, 请记录下错误场景并与开发人员联系, 谢谢!");
	    	}
	    }
	}
});
