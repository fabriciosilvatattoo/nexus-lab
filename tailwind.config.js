
/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                nexus: {
                    900: '#0f0a1e', // Dark Violet Logic
                    800: '#1a142d',
                    500: '#8b5cf6', // Violet
                    400: '#a78bfa',
                }
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
