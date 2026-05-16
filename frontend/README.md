# AI Ops Platform — Frontend

Next.js 14 frontend for the AI Autonomous Company Operations Platform.

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.local.example .env.local
   ```
   Fill in:
   - `NEXT_PUBLIC_SUPABASE_URL` — from Supabase dashboard
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY` — from Supabase dashboard (anon/public key)
   - `NEXT_PUBLIC_API_URL` — your backend URL (e.g. https://your-backend.onrender.com)

3. **Run development server**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000)

## Deploy to Vercel

```bash
npx vercel
```

Set env vars in Vercel dashboard under Project Settings > Environment Variables.

## Project Structure

```
app/
├── (auth)/login, signup       # Auth pages
├── (dashboard)/               # Protected pages with sidebar
│   ├── dashboard/             # Main overview + agent status
│   ├── employees/             # Employee list + detail
│   ├── tasks/                 # Task management
│   ├── leaves/                # Leave requests (AI-powered)
│   ├── meetings/              # Meeting records + AI summaries
│   ├── payroll/               # Payroll records
│   ├── reports/               # Report generation
│   ├── procurement/           # Procurement requests
│   │   ├── vendors/           # Vendor intelligence
│   │   └── trends/            # Market trend intelligence
│   └── settings/              # User settings

components/
├── agents/AgentStatusPanel    # Live agent health monitor
├── shared/StatsCard           # KPI cards
├── shared/ActivityFeed        # Agent event log
└── shared/DataTable           # Reusable table

lib/
├── supabase/client.ts         # Browser Supabase client
├── supabase/server.ts         # Server Supabase client
├── api.ts                     # Axios API client (auto-attaches JWT)
├── hooks/                     # Custom React hooks
└── types/                     # TypeScript interfaces
```

## Notes

- Auth is handled via Supabase (email/password)
- JWT tokens are automatically attached to all API requests
- Supabase Realtime is used for live notifications
- Agent status polls the `/health` endpoint every 5 seconds
