// .eslintrc.js
module.exports = {
  env: {
    browser: true,
    // es2021: true,        // ❌ 错误：旧版本 ESLint 不识别
    es2020: true,           // ✅ 推荐：Vue 2 兼容
    // es6: true,           // ✅ 也可用（等价于 es2015）
    node: true
  },
  parserOptions: {
    ecmaVersion: 11,        // ✅ 明确指定 ECMAScript 版本（ES2020 = 版本 11）
    sourceType: 'module'
  },
  extends: [
    'eslint:recommended',
    // 如果你使用 Vue，确保添加：
    'plugin:vue/essential'  // Vue 2 推荐
  ],
  // ✅ 在这里配置规则，而不是在代码中 disable
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
    'no-unused-vars': 'warn'
  }
}