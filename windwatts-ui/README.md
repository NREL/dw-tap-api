
# WindWatts Frontend App

This project is a React application built with Vite, using Yarn as the package manager and Material-UI for the UI components.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- You have installed [Node.js](https://nodejs.org/) (which includes npm). Optionally suggest using `nvm` node version manager.
- You have installed [Yarn](https://yarnpkg.com/)

## Getting Started

To get a local copy up and running, follow these steps:

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/NREL/dw-tap-api.git
    ```

2. Navigate to the project directory:
    ```bash
    cd frontend
    ```

3. Install the dependencies:
    ```bash
    yarn install
    ```

### Configure Environment Files

Create two environment files, `.env.development` and `.env.production`, in the root of the project directory (./frontend/). These files will contain the necessary environment variables for the development and production environments.

#### .env.development
```shell
VITE_API_BASE_URL=http://windwatts-proxy:80
VITE_MAP_API_KEY=YOUR_GOOGLE_MAPS_API_KEY
VITE_MAP_ID=YOUR_MAP_ID
```

#### .env.production
```shell
VITE_API_BASE_URL=https://dw-tap.nrel.gov/
VITE_MAP_API_KEY=YOUR_GOOGLE_MAPS_API_KEY
VITE_MAP_ID=YOUR_MAP_ID
```

Replace `YOUR_GOOGLE_MAPS_API_KEY` and `YOUR_MAP_ID` with your actual Google Maps API key and map ID.


### Running the App

To start the development server, run:
```bash
yarn dev
```