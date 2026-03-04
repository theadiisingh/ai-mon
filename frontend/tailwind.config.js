/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['IBM Plex Sans', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      boxShadow: {
        // Subtle, restrained shadows only
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'elevated': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)',
        'input': 'inset 0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        // No glow effects - intentionally removed
      },
      colors: {
        // Refined Slate-based palette (Notion/Linear style)
        surface: {
          DEFAULT: '#0F172A',      // Deep charcoal - main background
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',          // Muted slate - primary text
          600: '#475569',
          700: '#334155',
          800: '#1E293B',          // Card background
          900: '#0F172A',
          950: '#020617',
        },
        // Muted accent - professional, not flashy
        accent: {
          DEFAULT: '#64748B',      // Slate-500 - muted blue-gray
          light: '#94A3B8',        // Slate-400
          dark: '#475569',         // Slate-600
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#CBD5E1',
          400: '#94A3B8',
          500: '#64748B',
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
        },
        // Primary action - subtle blue
        primary: {
          DEFAULT: '#3B82F6',      // Blue-500 - professional blue
          light: '#60A5FA',        // Blue-400
          dark: '#2563EB',         // Blue-600
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
        // Status colors - muted and professional
        success: {
          DEFAULT: '#10B981',     // Emerald-500
          light: '#34D399',       // Emerald-400
          dark: '#059669',        // Emerald-600
          muted: '#065F46',       // Darker for backgrounds
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
          DEFAULT: '#F59E0B',     // Amber-500
          light: '#FBBF24',       // Amber-400
          dark: '#D97706',        // Amber-600
          muted: '#78350F',       // Darker for backgrounds
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
          DEFAULT: '#EF4444',     // Red-500
          light: '#F87171',       // Red-400
          dark: '#DC2626',        // Red-600
          muted: '#7F1D1D',      // Darker for backgrounds
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
        // Text hierarchy
        content: {
          primary: '#F8FAFC',     // Slate-50 - main text
          secondary: '#94A3B8',   // Slate-400 - secondary text
          tertiary: '#64748B',    // Slate-500 - muted text
          inverse: '#0F172A',     // For light backgrounds
        },
        // Border colors
        border: {
          DEFAULT: 'rgba(148, 163, 184, 0.12)',     // Subtle slate border
          light: 'rgba(148, 163, 184, 0.08)',
          strong: 'rgba(148, 163, 184, 0.2)',
        },
        // Keep some zinc for compatibility
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
      animation: {
        // Subtle, professional animations only
        'fade-in': 'fadeIn 0.2s ease-out',
        'slide-up': 'slideUp 0.2s ease-out',
        'slide-in-left': 'slideInLeft 0.2s ease-out',
        // Removed: pulse-slow, glow-pulse, float, counter (flashy animations)
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(-8px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      transitionDuration: {
        '150': '150ms',
        '200': '200ms',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass': 'linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%)',
      },
      borderRadius: {
        // More restrained corners
        'DEFAULT': '6px',
        'sm': '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '10px',
      },
    },
  },
  plugins: [],
}

