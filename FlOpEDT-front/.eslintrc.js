module.exports = {
  env: {
    node: true,
  },
  root: true,
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
  },
  extends: ['plugin:vue/vue3-strongly-recommended', 'eslint:recommended', '@vue/typescript/recommended', 'prettier'],
  plugins: ['@typescript-eslint', 'prettier'],
  rules: {
    'prettier/prettier': 'error',
  },
}
