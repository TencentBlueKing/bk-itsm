const webpack = require('webpack')
const merge = require('webpack-merge')
const webpackBase = require('./webpack.base.conf')
const TerserJSPlugin = require("terser-webpack-plugin")
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const OptimizeCSSAssetsPlugin = require("optimize-css-assets-webpack-plugin")
const HtmlWebpackPlugin = require('html-webpack-plugin')
const { CleanWebpackPlugin } = require('clean-webpack-plugin')
// const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin

module.exports = merge(webpackBase, {
    mode: 'production',
    devtool: process.env.SOURCE_MAP === 'true' ? 'source-map' : false,
    output: {
        filename: 'assets/js/[name].[contenthash:7].js',
        publicPath: '{{BK_STATIC_URL}}'
    },
    module: {
        rules: [
            {
                test: /\.(css|scss|sass)$/,
                use: [
                    {
                        loader: MiniCssExtractPlugin.loader,
                        options: {
                            publicPath: '../../'
                        }
                    },
                    'css-loader',
                    'sass-loader'
                ]
            }
        ]
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'assets/css/[name].[contenthash:7].css'
        }),
        new webpack.HashedModuleIdsPlugin(),
        new HtmlWebpackPlugin({
            filename: 'assets/index.html',
            template: 'index.html',
            inject: true
        }),
        new CleanWebpackPlugin({
            cleanOnceBeforeBuildPatterns: ['./assets/**'],
            verbose: true
        })
    ],
    optimization: {
        minimizer: [
            new TerserJSPlugin({
                extractComments: false,
                cache: true,
                parallel: true
            }),
            new OptimizeCSSAssetsPlugin({
                cssProcessorOptions: {
                    // map: {  // css 文件 sourcemap
                    //     inline: false,
                    //     annotation: true
                    // },
                    safe: true
                }
            })
        ],
        runtimeChunk: 'single',
        splitChunks: {
            cacheGroups: {
                vueLib: {
                    test: /[\\/]node_modules[\\/](vue|vue-router|vuex)[\\/]/,
                    name: 'vue-lib',
                    chunks: 'initial'
                },
                highlight: {
                    test: /[\\/]node_modules[\\/]highlight.js[\\/]/,
                    name: 'highlight',
                    chunks: 'all'
                },
                brace: {
                    test: /[\\/]node_modules[\\/]brace[\\/]/,
                    name: 'brace',
                    chunks: 'initial'
                },
                'monaco-editor': {
                    test: /[\\/]node_modules[\\/]monaco-editor[\\/]/,
                    name: 'monaco-editor',
                    chunks: 'initial'
                }
            }
        }
    },
    stats: {
        children: false,
        entrypoints: false
    }
})
