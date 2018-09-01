var path = require("path")
var BundleTracker = require('webpack-bundle-tracker')

module.exports = {
    context: __dirname,

    devtool: 'source-map',

    entry: {
        "menu": ["./static/pokemon/js/menu.js"],
        "docs": ["./static/pokemon/js/docs.js"],
        "explore_graphql": ["./static/pokemon/js/explore_graphql.js"]
    },

    output: {
        path: path.resolve('./static/bundles/'),
        filename: "[name]-[hash].js",
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
    ],

    module: {
        rules: [
            {
                test: [/\.js$/, /\.jsx$/],
                loader: 'babel-loader',
                exclude: /node_modules/
            },
            // {
            //     test: /\.js/,
            //     enforce: 'pre',
            //     use: ['remove-flow-types-loader']
            // },
            {
                test: /\.mjs$/,
                include: /node_modules/,
                type: "javascript/auto",
            }
        ],
    },

    // resolve: {
    //     extensions: ['.wasm', '.mjs', '.js', '.jsx', '.json']
    // },
}
