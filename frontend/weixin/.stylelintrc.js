module.exports = {
    extends: ["stylelint-config-standard", "stylelint-config-recess-order"],
    plugins: [
		"stylelint-order"
	],
    rules: {
        "order/order": [
            "custom-properties",
            "declarations"
        ],
        "color-hex-case": [ "lower", {
            message: "色值请使用小写字母"
        }],
        "indentation": [ 4, {
            except: ["block"],
            message: "请使用4个空格进行缩进",
            severity: "warning"
        }],
        "max-empty-lines": [5, {
            message: "css规则间隔不能超过两行" 
        }],
        "rule-empty-line-before": null
    }
}