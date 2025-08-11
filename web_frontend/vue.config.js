const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 禁用ESLint检查以避免编译错误
  lintOnSave: false,
  
  // 开发服务器配置
  devServer: {
    port: 8080,
    host: '0.0.0.0',
    open: true,
    // 代理配置，避免跨域问题
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      }
    }
  },
  
  // 生产环境构建配置
  publicPath: process.env.NODE_ENV === 'production' ? './' : '/',
  outputDir: 'dist',
  assetsDir: 'static',
  
  // PWA配置
  pwa: {
    name: 'ETC申办系统',
    themeColor: '#409EFF',
    msTileColor: '#409EFF'
  },
  
  // 性能优化
  configureWebpack: {
    optimization: {
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            name: 'chunk-vendors',
            test: /[\\/]node_modules[\\/]/,
            priority: 10,
            chunks: 'initial'
          },
          elementUI: {
            name: 'chunk-element-plus',
            priority: 20,
            test: /[\\/]node_modules[\\/]element-plus[\\/]/
          }
        }
      }
    }
  }
}) 