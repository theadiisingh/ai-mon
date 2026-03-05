/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      // Refined spacing scale - Notion-level discipline
      spacing: {
        '0.5': '2px',
        '1': '4px',
        '1.5': '6px',
        '2': '8px',
        '2.5': '10px',
        '3': '12px',
        '3.5': '14px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '7': '28px',
        '8': '32px',
        '9': '36px',
        '10': '40px',
        '11': '44px',
        '12': '48px',
        '14': '56px',
        '16': '64px',
        '20': '80px',
      },
      boxShadow: {
        // Layered depth - quiet confidence
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.25)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px -1px rgba(0, 0, 0, 0.25)',
        'elevated': '0 4px 6px -1px rgba(0, 0, 0, 0.35), 0 2px 4px -2px rgba(0, 0, 0, 0.2)',
        'floating': '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.25)',
        'input': 'inset 0 1px 2px 0 rgba(0, 0, 0, 0.2)',
        // No glow effects - intentionally removed for restraint
      },
      colors: {
        // Pure black base theme
        surface: {
          DEFAULT: '#000000',      // Pure black - primary background
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#1F1F1F',          // Card background - very dark gray
          750: '#1A1A1A',
          800: '#141414',          // Elevated surfaces
          850: '#0F0F0F',
          900: '#0A0A0A',
          950: '#050505',
        },
        // Refined accent - muted intelligence blue
        accent: {
          DEFAULT: '#4A6FA5',      // Muted steel blue - professional
          light: '#6B8CC4',        // Lighter variant
          dark: '#345385',         // Darker variant
          dim: '#2D4A6F',          // Dimmed for backgrounds
          50: '#F0F4F8',
          100: '#E1E8F0',
          200: '#C3D1E1',
          300: '#A5BAD2',
          400: '#87A3C3',
          500: '#6B8CB4',
          600: '#4A6FA5',
          700: '#3A5590',
          800: '#2A4075',
          900: '#1A2A55',
        },
        // Primary action - restrained blue
        primary: {
          DEFAULT: '#3B82F6',      // Professional blue
          light: '#60A5FA',
          dark: '#2563EB',
          muted: '#1D4ED8',        // Muted for hover states
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        // Status colors - serious, not flashy
        success: {
          DEFAULT: '#10B981',     // Emerald - stable
          light: '#34D399',
          dark: '#059669',
          muted: '#065F46',       // Darker for backgrounds
          subtle: '#052E33',       // Very subtle backgrounds
          50: '#ECFDF5',
          100: '#D1FAE5',
          200: '#A7F3D0',
          300: '#6EE7B7',
          400: '#34D399',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
          800: '#065F46',
          900: '#064E3B',
        },
        warning: {
          DEFAULT: '#D97706',     // Amber - more serious tone
          light: '#FBBF24',
          dark: '#B45309',
          muted: '#78350F',
          subtle: '#451A03',
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
        },
        danger: {
          DEFAULT: '#DC2626',     // Red - serious alerts
          light: '#EF4444',
          dark: '#B91C1C',
          muted: '#7F1D1D',
          subtle: '#450A0A',
          50: '#FEF2F2',
          100: '#FEE2E2',
          200: '#FECACA',
          300: '#FCA5A5',
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
          700: '#B91C1C',
          800: '#991B1B',
          900: '#7F1D1D',
        },
        // Text hierarchy - refined clarity
        content: {
          primary: '#E2E8F0',     // Slate-200 - primary text (softer)
          secondary: '#64748B',    // Slate-500 - secondary text
          tertiary: '#475569',    // Slate-600 - muted text
          inverse: '#0A0E17',     // For light backgrounds
        },
        // Border colors - subtle and intentional
        border: {
          DEFAULT: 'rgba(148, 163, 184, 0.1)',     // Very subtle
          light: 'rgba(148, 163, 184, 0.06)',       // Lighter
          strong: 'rgba(148, 163, 184, 0.15)',      // Stronger
          accent: 'rgba(74, 111, 165, 0.3)',       // Accent border
        },
        // Keep zinc for compatibility
        zinc: {
          50: '#fafafa',
          100: '#f4f4f5',
          200: '#e4e4e7',
          300: '#d4d4d8',
          400: '#a1a1aa',
          500: '#71717a',
          600: '#52525b',
          700: '#3f3f46',
          800: '#27272a',
          900: '#18181b',
          950: '#09090b',
        },
      },
      // Typography scale - intentional hierarchy
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],   // 10px
        'xs': ['0.75rem', { lineHeight: '1rem' }],           // 12px
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],      // 14px
        'base': ['1rem', { lineHeight: '1.5rem' }],          // 16px
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],       // 18px
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],         // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }],           // 24px
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],       // 30px
      },
      // Motion system - engineered feel (120-160ms)
      animation: {
        'fade-in': 'fadeIn 0.14s ease-out',
        'fade-in-slow': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.14s ease-out',
        'slide-up-medium': 'slideUp 0.2s ease-out',
        'slide-in-left': 'slideInLeft 0.14s ease-out',
        'subtle-scale': 'subtleScale 0.12s ease-out',
        // Subtle lift on hover
        'lift': 'lift 0.2s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(3px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-6px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        subtleScale: {
          '0%': { opacity: '0', transform: 'scale(0.98)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        lift: {
          '0%': { transform: 'translateY(0)' },
          '100%': { transform: 'translateY(-2px)' },
        },
      },
      transitionDuration: {
        '100': '100ms',
        '120': '120ms',
        '140': '140ms',
        '160': '160ms',
        '200': '200ms',
      },
      transitionTimingFunction: {
        // Engineered, not playful
        'engineered': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'subtle': 'cubic-bezier(0.4, 0, 0.6, 1)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass': 'linear-gradient(135deg, rgba(255,255,255,0.02) 0%, rgba(255,255,255,0.005) 100%)',
// Pure black atmospheric gradient - flat black
        'atmosphere': 'linear-gradient(180deg, #000000 0%, #000000 50%, #000000 100%)',
      },
      borderRadius: {
        // Restrained corners
        'sm': '3px',
        'DEFAULT': '4px',
        'md': '5px',
        'lg': '6px',
        'xl': '8px',
        '2xl': '10px',
      },
      // Custom backdrop blur
      backdropBlur: {
        'xs': '2px',
      },
    },
  },
  plugins: [],
}

