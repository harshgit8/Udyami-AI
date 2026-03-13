/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'system': ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'SF Pro Text', 'Helvetica Neue', 'Arial', 'sans-serif'],
        'mono': ['SF Mono', 'Monaco', 'Menlo', 'monospace'],
      },
      colors: {
        // Pure Black & White System - macOS Inspired
        'pure': {
          'black': '#000000',
          'white': '#FFFFFF',
        },
        'mono': {
          '50': '#FAFAFA',   // Lightest gray
          '100': '#F5F5F5',  // Ultra light
          '200': '#E8E8E8',  // Very light
          '300': '#D1D1D1',  // Light
          '400': '#B4B4B4',  // Medium-light
          '500': '#8E8E8E',  // Medium
          '600': '#6E6E6E',  // Medium-dark
          '700': '#4A4A4A',  // Dark
          '800': '#2C2C2C',  // Very dark
          '900': '#1A1A1A',  // Ultra dark
        }
      },
      boxShadow: {
        'minimal': '0 1px 2px rgba(0, 0, 0, 0.04)',
        'sm': '0 1px 3px rgba(0, 0, 0, 0.06)',
        'md': '0 2px 8px rgba(0, 0, 0, 0.08)',
        'lg': '0 4px 16px rgba(0, 0, 0, 0.10)',
        'focus': '0 0 0 3px rgba(0, 0, 0, 0.15)',
      },
      borderRadius: {
        'minimal': '4px',
        'sm': '6px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.25s ease-out',
        'pulse-subtle': 'pulseSubtle 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.6' },
        },
      },
    },
  },
  plugins: [],
}