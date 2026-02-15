module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        browsers: ['last 2 versions', 'not dead', '> 0.2%'],
      },
      modules: false,
    }],
    ['@babel/preset-react', {
      runtime: 'automatic',
    }],
  ],
};
