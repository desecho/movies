const webpack = require('webpack');
const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const basePath = path.resolve(__dirname, 'src', 'moviesapp');
const jsPath = path.join(basePath, 'js');
const vendorPackages = ['vue-toast-notification/dist/theme-default.css',
  'bootstrap/dist/css/bootstrap.min.css', 'axios-progress-bar/dist/nprogress.css', 'popper.js/dist/umd/popper.min.js',
  'bootstrap-social/bootstrap-social.css', 'jquery/dist/jquery.min.js',
  'retinajs/dist/retina.min.js', 'raty-js/lib/jquery.raty.css',
];

function getBundle(filename) {
  return [path.join(jsPath, 'init.js'), path.join(jsPath, filename), path.join(jsPath, 'set_axios_settings.js')];
}

function getBundleWithRaty(filename) {
  const bundle = ['raty-js/lib/jquery.raty.js'];
  return bundle.concat(getBundle(filename));
}

function getListBundle() {
  const bundle = ['raty-js/lib/jquery.raty.js', 'bootstrap/dist/js/bootstrap.min.js'];
  return bundle.concat(getBundle('list.js'));
}

function getFeedBundle() {
  const bundle = getBundleWithRaty('feed.js');
  return bundle.concat([path.join(jsPath, 'empty_app.js')]);
}

function getBundleWithEmptyApp(filename) {
  const bundle = getBundle(filename);
  return bundle.concat([path.join(jsPath, 'empty_app.js')]);
}

module.exports = {
  entry: {
    search: getBundle('search.js'),
    list: getListBundle(),
    gallery: getBundle('gallery.js'),
    // recommendations: getBundleWithRaty('recommendations.js'),
    registration: getBundleWithEmptyApp('registration.js'),
    passwordChange: getBundleWithEmptyApp('password_change.js'),
    feed: getFeedBundle(),
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
