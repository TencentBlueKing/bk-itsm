const path = require('path')
const { VueLoaderPlugin } = require('vue-loader')
const tsImportPluginFactory = require('ts-import-plugin')
const WebpackBar = require('webpackbar')
const CaseSensitivePathsPlugin = require('case-sensitive-paths-webpack-plugin')

module.exports = {
    entry: {
        main: './src/main.ts'
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, '../src/'),
            'vue': 'vue/dist/vue.esm-bundler.js'
        },
        extensions: ['*', '.js', '.ts', '.vue', '.json']
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader',
                exclude: /node_modules/
            },
            {
                test: /\.(jsx|tsx|js|ts)$/,
                loader: 'ts-loader',
                exclude: /node_modules/,
                options: {
                    transpileOnly: true,
                    getCustomTransformers: () => ({
                        before: [ tsImportPluginFactory( /** options */) ]
                    }),
                    appendTsSuffixTo: [/\.vue$/]
                }
            },
            {
                test: /\.(js|ts|vue)$/,
                loader: 'eslint-loader',
                enforce: 'pre',
                exclude: /node_modules/,
                options: {
                    formatter: require('eslint-friendly-formatter')
                }
            },
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/
            },
            {
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    // 3.0.0 版本默认使用 esModule，导致 css 中使用 url 的地方编译后错误输出 [object Module]
                    // 参考 https://github.com/vuejs/vue-loader/issues/1612
                    esModule: false,
                    limit: 10000,
                    name: '[name].[contenthash:7].[ext]',
                    outputPath: 'images/'
                }
            },
            {
                test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    esModule: false,
                    limit: 10000,
                    name: '[name].[contenthash:7].[ext]',
                    outputPath: 'media/'
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    esModule: false,
                    limit: 10000,
                    name: '[name].[contenthash:7].[ext]',
                    outputPath: 'fonts/'

                }
            }
        ]
    },
    plugins: [
        new CaseSensitivePathsPlugin(),
        new VueLoaderPlugin(),
        new WebpackBar()
    ]
}