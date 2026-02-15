# CasaPAT IoT Dashboard

A modern React-based web application for monitoring IoT devices including air quality sensors and door sensors.

## Features

- Real-time device status monitoring
- Historical data visualization with charts
- Responsive design for mobile and desktop
- Automatic data refresh and caching
- Modern Material-UI interface

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Access to CasaPAT API at http://pat.local:5000

## Installation

```bash
npm install
```

## Development

Start the development server with hot module replacement:

```bash
npm start
```

The application will open automatically at http://localhost:8080

## Build

Create a production build:

```bash
npm run build
```

The optimized build will be in the `dist/` directory.

## Testing

Run all tests:

```bash
npm test
```

Run tests in watch mode:

```bash
npm run test:watch
```

Run tests with coverage:

```bash
npm run test:coverage
```

Run property-based tests only:

```bash
npm run test:properties
```

## Configuration

### API Base URL

The default API base URL is `http://pat.local:5000`. To change this for different environments, modify the API client configuration in `src/api/casapatApi.js`.

## Technology Stack

- React 18
- Material-UI v5
- Recharts 2.x
- TanStack Query v5
- React Router v6
- Axios
- Webpack 5
- Babel

## Project Structure

```
dashboard/
├── public/           # Static files
├── src/
│   ├── api/         # API client
│   ├── components/  # Reusable components
│   ├── hooks/       # Custom React hooks
│   ├── pages/       # Page components
│   ├── utils/       # Utility functions
│   ├── App.js       # Root component
│   └── index.js     # Entry point
├── webpack.config.js
├── babel.config.js
└── package.json
```

## License

MIT
