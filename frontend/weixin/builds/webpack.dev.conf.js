const path = require('path')
const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const merge = require('webpack-merge')
const webpackBase = require('./webpack.base.conf')

module.exports = merge(webpackBase, {
    mode: 'development',
    output: {
        path: path.resolve(__dirname, '../../static/weixin/'),
        publicPath: '/',
        filename: 'js/[name].[hash:10].js'
    },
    module: {
        rules: [{
            test: /\.(css|postcss)$/,
            use: [
                'style-loader',
                'css-loader',
                'postcss-loader'
            ]
        }]
    },
    plugins: [
        new webpack.NamedModulesPlugin(),
        new webpack.HotModuleReplacementPlugin(),
        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'index-dev.html',
            inject: true
        })
    ],
    devtool: 'inline-source-map',
    devServer: {
        contentBase: '/',
        host: '${host}',
        disableHostCheck: true,
        port: 8005,
        https: false,
        hot: true,
        open: false,
        overlay: true,
        proxy: {
            '/t/itsm/weixin/api': {
                target: '${host}',
                changeOrigin: true,
                secure: false
            },
            '/api': {
                target: '${host}',
                changeOrigin: true,
                secure: false
            },
        },
        stats: {
            children: false,
            entrypoints: false,
            modules: false
        }
    }
})
