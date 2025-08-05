module.exports = {
  apps: [{
    name: 'yys-sqr-expo',
    script: 'npx',
    args: 'expo start --tunnel --non-interactive',
    cwd: '/Users/parallel/encoded/yys-sqr/mobile_app_rn',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'development'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};