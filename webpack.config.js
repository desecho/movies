const webpack = require('webpack');
const path = require('path');
const ExtractTextPlugin = require('extract-text-webpack-plugin');

const basePath = path.resolve(__dirname, 'src', 'moviesapp');
const jsPath = path.join(basePath, 'js');
const loaderFontOptions = {
  outputPath: 'font/',
};
const vendorPackages = ['font-awesome-webpack', 'vue-flash-message/dist/vue-flash-message.min.css',
  'bootstrap/dist/css/bootstrap.min.css', 'bootstrap/dist/js/bootstrap.min.js',
  'axios-progress-bar/dist/nprogress.css', 'popper.js/dist/umd/popper.min.js',
  'bootstrap-social/bootstrap-social.css', 'jquery/dist/jquery.min.js',
  'retinajs/dist/retina.min.js', 'raty-js/lib/jquery.raty.js', 'raty-js/lib/jquery.raty.css',
  'autosize/dist/autosize.min.js',
];


module.exports = {
  entry: {
    init: path.join(jsPath, 'init.js'),
    search: path.join(jsPath, 'search.js'),
    list: path.join(jsPath, 'list.js'),
    gallery: path.join(jsPath, 'gallery.js'),
    recommendations: path.join(jsPath, 'recommendations.js'),
    registration: path.join(jsPath, 'registration.js'),
    passwordChange: path.join(jsPath, 'password_change.js'),
    feed: path.join(jsPath, 'feed.js'),
    setAxiosSettings: path.join(jsPath, 'set_axios_settings.js'),
    style: path.join(basePath, 'styles', 'styles.scss'),
    vendor: vendorPackages,
  },
  watchOptions: {
    poll: true,
  },
  resolve: {
    alias: {
      vue: 'vue/dist/vue.js',
    },
  },
  output: {
    filename: 'js/[name].js',
    path: path.join(basePath, 'static'),
  },
  module: {
    rules: [{
      test: /\.css$/,
      use: ExtractTextPlugin.extract({
        fallback: 'style-loader',
        use: 'css-loader',
      }),
    },
    {
      test: /\.scss$/,
      loader: ExtractTextPlugin.extract({
        fallback: 'style-loader',
        use: [{
          loader: 'css-loader',
        }, {
          loader: 'sass-loader',
        }],
      },

      ),
    },
    {
      test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
      loader: 'url-loader?limit=10000&mimetype=application/font-woff',
      options: loaderFontOptions,
    },
    {
      test: /\.(ttf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
      loader: 'file-loader',
      options: loaderFontOptions,
    },
    ],
  },
  plugins: [
    new ExtractTextPlugin('[name].css'),
    new webpack.ProvidePlugin({
      '$': 'jquery',
      'jQuery': 'jquery',
      'window.jQuery': 'jquery',
      'Tether': 'tether',
      'Popper': 'popper.js',
      'window.Tether': 'tether',
      'autosize': 'autosize',
      'Alert': 'exports-loader?Alert!bootstrap/js/dist/alert',
      'Button': 'exports-loader?Button!bootstrap/js/dist/button',
      'Carousel': 'exports-loader?Carousel!bootstrap/js/dist/carousel',
      'Collapse': 'exports-loader?Collapse!bootstrap/js/dist/collapse',
      'Dropdown': 'exports-loader?Dropdown!bootstrap/js/dist/dropdown',
      'Modal': 'exports-loader?Modal!bootstrap/js/dist/modal',
      'Popover': 'exports-loader?Popover!bootstrap/js/dist/popover',
      'Scrollspy': 'exports-loader?Scrollspy!bootstrap/js/dist/scrollspy',
      'Tab': 'exports-loader?Tab!bootstrap/js/dist/tab',
      'Tooltip': 'exports-loader?Tooltip!bootstrap/js/dist/tooltip',
      'Util': 'exports-loader?Util!bootstrap/js/dist/util',
    }),
    new webpack.optimize.CommonsChunkPlugin({
      name: 'commons',
      filename: 'js/commons.js',
      minChunks: 2,
      minSize: 0,
    }),
  ],
};
