const webpack = require('webpack');
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const basePath = path.resolve(__dirname, 'src', 'moviesapp');
const jsPath = path.join(basePath, 'js');
const vendorPackages = ['vue-toast-notification/dist/theme-default.css',
  'bootstrap/dist/css/bootstrap.min.css', 'axios-progress-bar/dist/nprogress.css', 'popper.js/dist/umd/popper.min.js',
  'bootstrap-social/bootstrap-social.css', 'jquery/dist/jquery.min.js',
];

function getBundle(filename) {
  return [
    'bootstrap/dist/js/bootstrap.min.js',
    path.join(jsPath, 'menu.js'),
    path.join(jsPath, filename),
  ];
}

function getBundleWithEmptyApp(filename) {
  const bundle = getBundle(filename);
  return bundle.concat([path.join(jsPath, 'empty_app.js')]);
}

module.exports = {
  entry: {
    search: getBundle('search.js'),
    trending: getBundle('trending.js'),
    list: getBundle('list.js'),
    gallery: getBundle('gallery.js'),
    registration: getBundleWithEmptyApp('registration.js'),
    passwordChange: getBundleWithEmptyApp('password_change.js'),
    emptyApp: [path.join(jsPath, 'init.js'), path.join(jsPath, 'empty_app.js')],
    style: path.join(basePath, 'styles', 'styles.scss'),
    vendor: vendorPackages,
  },
  watchOptions: {
    poll: true,
  },
  output: {
    filename: 'js/[name].js',
    path: path.join(basePath, 'static'),
  },
  module: {
    rules: [
      // {
      //   test: /\.(ttf|eot|svg|woff|woff2)$/,
      //   loader: 'file-loader',
      //   options: {outputPath: 'font'},
      // },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader'],
      },
      {
        test: /\.scss$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader'],
      },
    ],
  },
  plugins: [
    new MiniCssExtractPlugin(),
    new webpack.DefinePlugin({
      __VUE_OPTIONS_API__: true,
      __VUE_PROD_DEVTOOLS__: false,
    }),
    new webpack.ProvidePlugin({
      '$': 'jquery',
      'jQuery': 'jquery',
      'window.jQuery': 'jquery',
      'Tether': 'tether',
      'Popper': 'popper.js',
      'window.Tether': 'tether',
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
  ],
  optimization: {
    splitChunks: {
      minSize: 0,
    },
  },
};
