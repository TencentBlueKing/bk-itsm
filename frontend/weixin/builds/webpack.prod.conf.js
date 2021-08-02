const path = require('path')
const merge = require('webpack-merge')
const webpackBase = require('./webpack.base.conf')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const TerserPlugin = require('terser-webpack-plugin')
// const CopyWebpackPlugin = require('copy-webpack-plugin')

// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin


module.exports = merge(webpackBase, {
    mode: 'production',
    output: {
        path: path.resolve(__dirname, '../../../static/weixin/'),
        filename: 'js/[name].[contenthash:10].js',
        publicPath: '{{WEIXIN_STATIC_URL}}'
    },
    module: {
        rules: [{
            test: /\.(css|postcss)$/,
            use: [
                {
                    loader: MiniCssExtractPlugin.loader,
                    options: {
                        publicPath: '../'
                    }
                },
                'css-loader',
                'postcss-loader'
            ]
        }]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: 'index.html',
            filename: 'index_mobile.html'
        }),
        new MiniCssExtractPlugin({
            filename: path.posix.join('css/[name].[hash:10].css')
        }),
        // new CopyWebpackPlugin({
        //     patterns: [{
        //         from: path.resolve(__dirname, '../src/static'),
        //         to: path.resolve(__dirname, '../../static/weixin/')
        //     }]
        // })
        // new BundleAnalyzerPlugin()
    ],
    optimization: {
        minimizer: [
            new TerserPlugin({
                cache: true,
                parallel: true,
                sourceMap: false,
                extractComments: false
            })
        ],
        splitChunks: {
            cacheGroups: {
                vueLib: {
                    test: /[\\/]node_modules[\\/](vue|vue-router|vuex)[\\/]/,
                    name: 'vue-lib',
                    priority: 10,
                    chunks: 'initial'
                },
                axios: {
                    test: /[\\/]node_modules[\\/]axios[\\/]/,
                    name: 'axios',
                    priority: 10,
                    chunks: 'initial'
                }
            }
        },
        runtimeChunk: {
            name: 'manifest'
        }
    }
})