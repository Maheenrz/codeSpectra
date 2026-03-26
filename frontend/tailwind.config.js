/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        pixelify: ['Pixelify Sans', 'cursive'],
        sans: ['DM Sans', 'system-ui', 'sans-serif'],
        mono: ['DM Mono', 'monospace'],
      },
      colors: {
        orange:  { DEFAULT: '#CF7249', light: '#FEF3EC', dark: '#B85E38' },
        teal:    { DEFAULT: '#2D6A6A', light: '#EBF4F4', dark: '#245757' },
        rose:    { DEFAULT: '#C4827A', light: '#FAEDEC', dark: '#A8655D' },
        slate:   { DEFAULT: '#8B9BB4', light: '#EFF2F7', dark: '#6B7F9A' },
        cream:   { DEFAULT: '#F7F3EE', dark: '#F0EBE3' },
        ink:     { DEFAULT: '#1A1714', mid: '#6B6560', light: '#A8A29E' },
        border:  { DEFAULT: '#E8E1D8', light: '#F0EBE3' },
      },
      keyframes: {
        'pulse-ring': {
          '0%':   { boxShadow: '0 0 0 0 rgba(207,114,73,0.4)' },
          '70%':  { boxShadow: '0 0 0 10px rgba(207,114,73,0)' },
          '100%': { boxShadow: '0 0 0 0 rgba(207,114,73,0)' },
        },
        fadeInUp: {
          '0%':   { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
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
          '0%, 100%': { boxShadow: '0 0 0 0 #c5c9f8' },
          '50%':      { boxShadow: '0 0 0 15px transparent' },
        },
      },
      animation: {
        'pulse-ring':   'pulse-ring 2s ease-in-out infinite',
        'fade-in-up':   'fadeInUp 0.6s ease-out forwards',
        'fade-in':      'fadeInUp 1s ease-out 0.5s forwards',
        'icon-appear':  'iconAppear 0.8s ease-out forwards',
        'dot-bounce':   'dotBounce 1.4s ease-in-out infinite',
        'dot-bounce-2': 'dotBounce 1.4s ease-in-out 0.2s infinite',
        'dot-bounce-3': 'dotBounce 1.4s ease-in-out 0.4s infinite',
        'badge-pulse':  'badgePulse 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};
