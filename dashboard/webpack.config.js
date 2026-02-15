const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development';

  return {
    entry: './src/index.js',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isDevelopment ? '[name].js' : '[name].[contenthash].js',
      clean: true,
      publicPath: '/',
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
          },
        },
        {
          test: /\.css$/,
          use: ['style-loader', 'css-loader'],
        },
      ],
    },
    resolve: {
      extensions: ['.js', '.jsx'],
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: './public/index.html',
        favicon: false,
      }),
    ],
    devServer: {
      static: {
        directory: path.join(__dirname, 'public'),
      },
      compress: true,
      port: 8080,
      host: '0.0.0.0', // Listen on all network interfaces
      hot: true,
      historyApiFallback: true,
      open: false, // Don't auto-open browser since we're using custom hostname
      allowedHosts: 'all', // Allow access from any hostname including pat.local
    },
    devtool: isDevelopment ? 'eval-source-map' : false,
    optimization: {
      splitChunks: {
        chunks: 'all',
      },
    },
  };
};
