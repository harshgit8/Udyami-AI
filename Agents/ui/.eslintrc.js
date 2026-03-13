module.exports = {
  extends: [
    'react-app',
    'react-app/jest'
  ],
  rules: {
    // Disable unused variable warnings for development
    '@typescript-eslint/no-unused-vars': 'warn',
    // Allow console statements in development, warn in production
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    // Disable exhaustive deps warning for useEffect
    'react-hooks/exhaustive-deps': 'warn',
  },
  overrides: [
    {
      files: ['**/*.ts', '**/*.tsx'],
      rules: {
        // TypeScript specific rules
        '@typescript-eslint/no-unused-vars': ['warn', { 
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_' 
        }],
      }
    }
  ]
};