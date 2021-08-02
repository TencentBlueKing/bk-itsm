/**
 * @file 蓝鲸前端代码 ESLint 规则 Vue
 * bkfe
 */

module.exports = {
    parser:  'vue-eslint-parser',
    parserOptions: {
        parser: '@typescript-eslint/parser',
        ecmaVersion: 2018,
        sourceType: 'module',
        extraFileExtensions: ['.vue'],
        ecmaFeatures: {
            jsx: true,
            modules: true
        }
    },
    extends: [
        'plugin:vue/vue3-recommended',
        '@tencent/eslint-config-tencent',
        '@tencent/eslint-config-tencent/ts'
    ],
    env: {
        browser: true,
        node: true,
        commonjs: true,
        es6: true
    },
    globals: {},
    // add your custom rules hered
    rules: {
        "vue/max-attributes-per-line": ["error", {
            "singleline": 4
        }],
        "vue/html-closing-bracket-newline": ["error", {
            "singleline": "never",
            "multiline": "never"
        }],
        "vue/singleline-html-element-content-newline": "off",
        "comma-dangle": ["error", "never"],
        'semi': ['error', 'never'],
        "camelcase": ['error', {'properties': 'never'}],
        'linebreak-style': ["off", "windows"],
        "no-param-reassign": [2, { "props": false }],
        "newline-per-chained-call": ["warn", { "ignoreChainWithDepth": 5 }],
        'camelcase': ["off"],
        // ts
        "@typescript-eslint/indent": ['error', 2],
        "@typescript-eslint/semi": ["error", "never"],
        "@typescript-eslint/naming-convention": ["off"]
    }
}
