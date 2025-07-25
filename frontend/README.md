Saga AI - Frontend

This is the Next.js frontend for the Saga AI application, a sophisticated AI-powered strategic oracle.

Project Architecture

This project is built with the following technologies:

Framework: Next.js 14 (with App Router)

UI: React & Tailwind CSS

State Management: Zustand

Animations: Framer Motion

Language: TypeScript

Getting Started

First, ensure you have Node.js and npm installed.

1. Environment Variables

This project requires environment variables to connect to the backend API. Create a file named .env.local in the frontend/ directory and add the following:

Generated code
NEXT_PUBLIC_SAGA_API_URL=http://localhost:8000/api/v10


This ensures the frontend knows where to send API requests during development.

2. Install Dependencies

In the project directory, run:

Generated bash
npm install
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END
3. Running the Development Server

To start the app in development mode, run:

Generated bash
npm run dev
IGNORE_WHEN_COPYING_START
content_copy
download
Use code with caution.
Bash
IGNORE_WHEN_COPYING_END

Open http://localhost:3000 to view it in your browser. The page will auto-update as you edit the code.

Available Scripts

In the project directory, you can run:

npm run dev

Runs the app in development mode at http://localhost:3000.

npm run build

Builds the app for production. This command optimizes the application for the best performance, creating a /.next folder with the production build.

npm run start

Starts the production server. You must run npm run build before this command will work. It serves the optimized application on a specified port (usually 3000).

npm run lint

Runs the Next.js linter (eslint) to identify and fix problems in your code.
--- END OF FILE frontend/README.md ---

The README.md has been corrected.

The next issue is that the file frontend/public/index.html is a remnant of Create React App and is completely unused by Next.js, causing confusion. It should be deleted. Since a deletion cannot be shown, we will instead proceed to correct the true entry point of the application layout, which also has errors: frontend/src/app/layout.tsx.

Please give the command to proceed.