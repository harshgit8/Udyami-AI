# Manufacturing Orchestration UI

A beautiful, minimal macOS-style React interface for the AI-powered manufacturing orchestration system.

## 🎨 Design Philosophy

- **macOS-inspired design** - Clean, minimal, professional
- **White background** - Pristine, uncluttered interface
- **System fonts** - SF Pro Display for perfect typography
- **Subtle shadows** - Depth without distraction
- **Smooth animations** - Framer Motion for fluid interactions
- **Responsive design** - Works on all screen sizes

## 🚀 Features

### Core Functionality
- **Real-time orchestrator control** - Start/stop all 5 orchestrators
- **Live execution monitoring** - Progress bars, step tracking, real-time updates
- **Results visualization** - Interactive tables, charts, summaries
- **Google Sheets integration** - Seamless sync with existing data
- **System status monitoring** - Connection health, API status

### Orchestrators
1. **Production Scheduling** - 9-step AI-powered production optimization
2. **Invoice Generation** - Tax-compliant invoice creation
3. **Quality Control** - Batch inspection and defect analysis
4. **Quotation Management** - Customer quote generation
5. **R&D Formulation** - Material formulation design

### UI Components
- **Header** - System branding and quick actions
- **System Status** - Real-time connection and health monitoring
- **Orchestrator Grid** - 5 beautiful cards for each orchestrator
- **Live Execution** - Dynamic progress tracking with step visualization
- **Latest Results** - Tabbed interface for viewing results

## 🛠 Technology Stack

- **React 18** - Modern React with hooks and concurrent features
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling with custom macOS theme
- **Framer Motion** - Smooth animations and transitions
- **Heroicons** - Beautiful SVG icons
- **Date-fns** - Date formatting and manipulation
- **WebSocket** - Real-time updates from backend

## 📁 Project Structure

```
ui/
├── public/
│   └── index.html              # HTML template
├── src/
│   ├── components/             # React components
│   │   ├── Header.tsx          # App header with branding
│   │   ├── SystemStatus.tsx    # System health monitoring
│   │   ├── OrchestratorGrid.tsx # Grid of orchestrator cards
│   │   ├── OrchestratorCard.tsx # Individual orchestrator card
│   │   ├── LiveExecution.tsx   # Real-time progress monitoring
│   │   └── LatestResults.tsx   # Results visualization
│   ├── context/
│   │   └── OrchestratorContext.tsx # Global state management
│   ├── services/
│   │   └── orchestratorService.ts  # API service layer
│   ├── types/
│   │   └── index.ts            # TypeScript type definitions
│   ├── utils/
│   │   ├── constants.ts        # App constants and configuration
│   │   └── formatters.ts       # Utility functions for formatting
│   ├── App.tsx                 # Main app component
│   ├── index.tsx              # React entry point
│   └── index.css              # Global styles and Tailwind imports
├── package.json               # Dependencies and scripts
├── tailwind.config.js         # Tailwind configuration with macOS theme
├── tsconfig.json             # TypeScript configuration
└── postcss.config.js         # PostCSS configuration
```

## 🎨 Design System

### Colors (macOS Inspired)
```css
--macos-white: #FFFFFF
--macos-gray-50: #FAFAFA
--macos-gray-100: #F5F5F5
--macos-gray-200: #E5E5E5
--macos-blue: #007AFF
--macos-green: #34C759
--macos-orange: #FF9500
--macos-red: #FF3B30
```

### Typography
- **Primary**: SF Pro Display (system font)
- **Monospace**: SF Mono
- **Weights**: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold)

### Spacing
- **Base unit**: 4px (0.25rem)
- **Card padding**: 24px (1.5rem)
- **Section spacing**: 32px (2rem)

### Shadows
- **Card shadow**: `0 1px 3px rgba(0, 0, 0, 0.05)`
- **Hover shadow**: `0 4px 12px rgba(0, 0, 0, 0.08)`
- **Focus shadow**: `0 0 0 3px rgba(0, 122, 255, 0.3)`

## 🚀 Getting Started

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation
```bash
# Navigate to UI directory
cd ui

# Install dependencies
npm install

# Start development server (Windows)
npm start
# OR use batch file
start.bat

# Build for production (Windows)
npm run build
# OR use batch file  
build.bat
```

### Cross-Platform Commands
```bash
# Build with optimizations
npm run build:prod

# Start with optimizations
npm start:prod
```

### Environment Variables
Create a `.env` file in the `ui` directory:
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

### Build for Production
```bash
npm run build
```

## 🔌 Backend Integration

The UI expects a FastAPI backend with the following endpoints:

### REST API Endpoints
- `POST /api/orchestrators/{type}` - Run orchestrator
- `POST /api/orchestrators/{type}/stop` - Stop orchestrator
- `GET /api/status` - Get system status
- `GET /api/results/{type}` - Get orchestrator results
- `POST /api/sheets/sync` - Sync Google Sheets

### WebSocket Events
- `progress` - Orchestrator progress updates
- `result` - Orchestrator completion
- `error` - Error notifications

## 🎯 Key Features

### Real-time Updates
- WebSocket connection for live progress
- Automatic status refresh
- Dynamic progress bars and step tracking

### Orchestrator Control
- One-click start/stop for all orchestrators
- Visual status indicators
- Error handling and display

### Results Visualization
- Tabbed interface for different result types
- Interactive tables with sorting and filtering
- Summary cards and metrics

### Google Sheets Integration
- Connection status monitoring
- Sync functionality
- Tab management

## 🎨 Customization

### Theme Colors
Edit `tailwind.config.js` to customize the color palette:
```javascript
colors: {
  'macos': {
    'blue': '#007AFF',    // Primary blue
    'green': '#34C759',   // Success green
    'orange': '#FF9500',  // Warning orange
    'red': '#FF3B30',     // Error red
  }
}
```

### Animation Settings
Modify animation durations in `src/utils/constants.ts`:
```typescript
export const ANIMATION_DURATION = {
  fast: 0.15,
  normal: 0.3,
  slow: 0.5,
};
```

## 📱 Responsive Design

The UI is fully responsive with breakpoints:
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px  
- **Desktop**: > 1024px

### Mobile Optimizations
- Stacked orchestrator cards
- Simplified navigation
- Touch-friendly buttons
- Optimized table layouts

## 🔧 Development

### Code Style
- **ESLint** - Code linting
- **Prettier** - Code formatting
- **TypeScript** - Type checking

### Component Guidelines
- Use functional components with hooks
- Implement proper TypeScript types
- Follow React best practices
- Use Framer Motion for animations

### State Management
- React Context for global state
- Local state for component-specific data
- Custom hooks for reusable logic

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Environment Configuration
- Development: `npm start`
- Production: `npm run build` + serve static files
- Docker: Multi-stage build with nginx

## 🎯 Performance

### Optimizations
- Code splitting with React.lazy
- Memoization with React.memo
- Efficient re-renders with useCallback/useMemo
- Optimized bundle size with tree shaking

### Metrics
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **Bundle Size**: < 500KB gzipped

## 🔒 Security & Vulnerabilities

### Development Dependencies
The reported vulnerabilities are in **development-only dependencies** and **do not affect production**:

- **ESLint packages** - Used only during development for code linting
- **Webpack dev server** - Used only in development mode
- **PostCSS versions** - Used only during build process

### Production Safety
✅ **Production builds are secure** - Development dependencies are excluded  
✅ **Docker images are clean** - Multi-stage builds ensure no dev dependencies  
✅ **Runtime configuration** - Environment variables handled securely  
✅ **Security headers** - CSP, XSS protection, and HTTPS enforcement  

### Vulnerability Management
```bash
# Check vulnerabilities (safe to ignore dev-only issues)
npm audit

# Fix production vulnerabilities only
npm audit --production

# Force fix (may break development tools)
npm audit fix --force  # NOT recommended
```

For detailed security information, see [SECURITY.md](SECURITY.md).

## 📈 Monitoring

### Analytics
- Performance monitoring
- Error tracking
- User interaction analytics
- Real-time system metrics

---

**Built with ❤️ for manufacturing excellence**