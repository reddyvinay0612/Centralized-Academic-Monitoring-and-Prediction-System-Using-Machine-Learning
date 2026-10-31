/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#14213d',
        sidebar: '#10243f',
        page: '#eef2f6',
        surface: '#ffffff',
        line: '#d9e1ea',
        muted: '#5b6b82',
        accent: {
          DEFAULT: '#2f6bff',
          hover: '#2456cc',
        },
        risk: {
          low: '#0f9d8a',
          medium: '#d89a06',
          high: '#d9445a',
        },
        dark: {
          page: '#0b1522',
          surface: '#122033',
          line: '#223650',
          text: '#e8eef7',
          muted: '#93a3ba',
          accent: '#6f95ff',
        },
      },
      fontFamily: {
        heading: ['"Bricolage Grotesque"', 'sans-serif'],
        body: ['"Instrument Sans"', 'sans-serif'],
      },
      fontSize: {
        'display': ['28px', { lineHeight: '1.25', fontWeight: '700' }],
        'heading': ['18px', { lineHeight: '1.35', fontWeight: '600' }],
        'body': ['15px', { lineHeight: '1.5', fontWeight: '400' }],
        'caption': ['13px', { lineHeight: '1.4', fontWeight: '400' }],
      },
      borderRadius: {
        card: '14px',
        input: '10px',
        pill: '9999px',
      },
      boxShadow: {
        subtle: '0 1px 3px 0 rgba(20, 33, 61, 0.05)',
        card: '0 2px 6px 0 rgba(20, 33, 61, 0.04)',
      },
    },
  },
  plugins: [],
};
