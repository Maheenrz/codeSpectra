/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        pixelify: ['Pixelify Sans', 'cursive'],
      },
      colors: {
        primary: '#9333ea',
        'primary-dark': '#7e22ce',
        'primary-light': '#c084fc',
      },
      keyframes: {
        fadeInUp: {
          '0%':   { opacity: '0', transform: 'translateY(30px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%':   { opacity: '0' },
          '100%': { opacity: '1' },
        },
        iconAppear: {
          '0%':   { transform: 'scale(0) rotate(-180deg)', opacity: '0' },
          '60%':  { transform: 'scale(1.2) rotate(10deg)' },
          '100%': { transform: 'scale(1) rotate(0deg)', opacity: '1' },
        },
        dotBounce: {
          '0%, 80%, 100%': { transform: 'scale(0.8)', opacity: '0.5' },
          '40%':           { transform: 'scale(1.2)', opacity: '1' },
        },
        badgePulse: {
          '0%, 100%': { boxShadow: '0 0 0 0 #c084fc' },
          '50%':      { boxShadow: '0 0 0 15px transparent' },
        },
      },
      animation: {
        'fade-in-up':  'fadeInUp 1s ease-out forwards',
        'fade-in':     'fadeIn 1s ease-out 0.5s forwards',
        'icon-appear': 'iconAppear 0.8s ease-out forwards',
        'dot-bounce':  'dotBounce 1.4s ease-in-out infinite',
        'dot-bounce-2':'dotBounce 1.4s ease-in-out 0.2s infinite',
        'dot-bounce-3':'dotBounce 1.4s ease-in-out 0.4s infinite',
        'badge-pulse': 'badgePulse 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};