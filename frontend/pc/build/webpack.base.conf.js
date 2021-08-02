const path = require('path')
const webpack = require('webpack')
const HappyPack = require('happypack')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const CaseSensitivePathsPlugin = require('case-sensitive-paths-webpack-plugin')
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')

const os = require('os')
const happyThreadPool = HappyPack.ThreadPool({size: os.cpus().length})

function resolve (dir) {
    return path.join(__dirname, '..', dir)
}

module.exports = {
    entry: {
        app: './src/main.js'
    },
    output: {
        path: path.resolve(__dirname, '../../../static/'),
        filename: 'assets/js/[name].js',
        publicPath: '/',
        pathinfo: false
    },
    resolve: {
        extensions: ['.js', '.vue', '.json'],
        alias: {
            'vue': 'vue/dist/vue.esm.js',
            '@': path.resolve(__dirname, '../src/'),
            'jquery': 'jquery/dist/jquery.min.js',
            '$': 'jquery/dist/jquery.min.js'
        }
    },
    cache: true,
    module: {
        rules: [
            {
                test: require.resolve('jquery'),
                use: [
                    {
                        loader: 'expose-loader',
                        options: 'jQuery'
                    },
                    {
                        loader: 'expose-loader',
                        options: '$'
                    }
                ]
            },
            {
                test: /\.(js|vue)$/,
                loader: 'eslint-loader',
                enforce: 'pre',
                exclude: /node_modules/,
                options: {
                    formatter: require('eslint-friendly-formatter')
                }
            },
            {
                test: /\.vue$/,
                use: 'vue-loader',
                exclude: /node_modules/
            },
            {
                test: require.resolve('vue'),
                use: [{
                    loader: 'expose-loader',
                    options: 'Vue'
                }]
            },
            {
                test: /\.js$/,
                // loader: 'babel-loader',
                use: ['happypack/loader?id=happy-babel-js'], // 增加新的HappyPack构建loader
                include: [resolve('src'), resolve('node_modules/vue-echarts'), resolve('node_modules/pinyin')]
                // exclude (modulePath) {
                // },
                // HappyPack: plugin for the loader '1' could not be found!
                // https://github.com/amireh/happypack/issues/183
                // https://github.com/amireh/happypack/issues/238
                // query: {
                //     cacheDirectory: './webpack_cache/'
                // }
            },
            {
                test: /\.(png|jpe?g|gif|svg)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    // 3.0.0 版本默认使用 esModule，导致 css 中使用 url 的地方编译后错误输出 [object Module]
                    // 参考 https://github.com/vuejs/vue-loader/issues/1612
                    esModule: false,
                    limit: 55000,
                    name: path.posix.join('assets/img/[name].[hash:7].[ext]')
                }
            },
            {
                test: /\.(mp4|webm|ogg|mp3|wav|flac|aac)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    esModule: false,
                    limit: 10000,
                    name: path.posix.join('assets/media/[name].[hash:7].[ext]')
                }
            },
            {
                test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
                loader: 'url-loader',
                options: {
                    esModule: false,
                    limit: 10000,
                    name: path.posix.join('assets/fonts/[name].[hash:7].[ext]')
                }
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin(),
        new webpack.ProvidePlugin({
            $: 'jquery',
            jQuery: 'jquery',
            'window.jQuery': 'jquery'
        }),
        new MonacoWebpackPlugin({
            languages: ['javascript', 'json']
        }),
        // 严格组件名大小写，避免linux系统上打包报错
        // https://github.com/chemzqm/keng/issues/4
        new CaseSensitivePathsPlugin({debug: false}),
        // moment 优化，只提取本地包
        new webpack.ContextReplacementPlugin(/moment\/locale$/, /zh-cn/),
        // brace 优化，只提取需要的语法
        new webpack.ContextReplacementPlugin(/brace\/mode$/, /^\.\/(json|python|sh|text)$/),
        // brace 优化，只提取需要的 theme
        new webpack.ContextReplacementPlugin(/brace\/theme$/, /^\.\/(monokai)$/),
        new HappyPack({
            id: 'happy-babel-js',
            loaders: ['babel-loader?cacheDirectory=true'],
            threadPool: happyThreadPool
        })
    ]
}
