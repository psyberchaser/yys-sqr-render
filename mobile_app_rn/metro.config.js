const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Reduce file watching to prevent EMFILE errors
config.watchFolders = [];
config.resolver.platforms = ['ios', 'android', 'native', 'web'];

// Reduce the number of watched files
config.watcher = {
  additionalExts: ['cjs', 'mjs'],
  watchman: {
    deferStates: ['hg.update'],
  },
};

module.exports = config;