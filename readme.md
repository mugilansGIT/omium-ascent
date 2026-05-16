What it does
This is an AI-powered company operations platform where most routine decisions — approving leaves, assigning tasks, summarizing meetings, finding vendors, drafting purchase orders — are handled autonomously by AI agents instead of humans.

The Big Picture: How Agents Talk to Each Other
The backbone is an event-driven architecture. Nothing calls anything directly. Instead, every action publishes an event to a Redis Stream, and the right agent picks it up and processes it.
The flow looks like this:

User submits leave request → API publishes event → Orchestrator reads it → routes to HR Agent → HR Agent calls Gemini → decision written to Supabase → Notification Agent emails the employee

This means agents are completely decoupled. You can add or remove agents without touching anything else.

The Orchestrator
Think of this as the traffic cop. It subscribes to all top-level events and has a routing table that maps each event type to the agent that should handle it. It doesn't do any AI reasoning itself — it just routes and delegates.
It also runs scheduled work: every morning at 9AM it triggers a trend scan and checks for overdue tasks.

The Individual Agents
HR Agent handles two things. When a leave request comes in, it fetches the employee's balance, checks how many teammates are already on leave, then sends all of that to Gemini with a policy prompt. Gemini returns a JSON decision — auto-approve, reject, or escalate — and the agent updates the database and notifies the employee automatically.
Task Agent watches for overdue tasks. When one is found, it asks Gemini to assess the risk level and suggest next steps, then notifies the assigned employee.
Meeting Agent takes a raw transcript (uploaded after a meeting), sends it to Gemini, and gets back a structured summary — key decisions, action items with owners, sentiment. It creates action item records in the database automatically.
Trend Agent is the intelligence gatherer. It hits Reddit's public JSON API and Google Trends RSS, collects titles, feeds them to Gemini, and gets back a list of trending products with scores for virality, longevity, and sustainability. These are stored in the product_trends table.
Vendor Agent does two things. When a procurement request comes in, it fetches matching vendors from the database and asks Gemini to rank the top 3 based on price, reliability, and quality. It also reacts to new trends by updating vendor scores — so if AI chips are trending, vendors in that category get re-evaluated.
Procurement Agent picks up after the Vendor Agent. It takes the top vendor recommendation, calls Gemini to draft a professional procurement email (introducing your company, specifying requirements, asking about pricing/certifications), and creates a Purchase Order record in "draft" status. A human can then review and click send.
Notification Agent is the delivery layer. It stores every notification in the database (for the in-app feed) and also sends an email via Resend to the recipient's address.

The Database (Supabase)
The schema mirrors the domain closely:

Employees & Departments — core people data, with manager hierarchies
Attendance & Leave — daily check-ins, leave policies, balances, requests with AI decisions stored as JSONB
Tasks & Projects — full task lifecycle with update history
Meetings — scheduled meetings, attendees, transcripts, AI summaries, action items
Payroll — periods and per-employee records with AI-generated notes
Vendors & Products — vendor catalog with AI-computed scores
Procurement & Purchase Orders — full procurement pipeline with AI-drafted emails
Product Trends — trend intelligence with scores
Agent Events — every single thing an agent does is logged here, so you have a full audit trail
Notifications — per-user notification inbox

Row Level Security is enabled so employees can only see their own data.

The API Layer
Standard FastAPI REST endpoints. Every route that kicks off an AI workflow follows the same pattern:

Write the record to Supabase with status: pending
Publish an event to Redis
Return immediately with "AI is processing your request"

The frontend gets the result either by polling or through Supabase Realtime (WebSocket subscription on the notifications table).

The Frontend Connection
The Next.js frontend connects directly to Supabase for real-time updates — so when an agent writes a notification or updates a leave request status, the UI updates instantly without polling. The AgentStatusPanel component polls /health every 5 seconds to show which agents are running.

Deployment

Backend on Render — one render.yaml file, connect your GitHub repo, set env vars, done. The uvicorn process starts all agents as async background tasks within the same process.
Frontend on Vercel — standard Next.js deploy.
Database on Supabase — managed Postgres, free tier works for a hackathon.
Redis on Upstash — serverless Redis, free tier handles the event bus fine.


The Data Flow for a Full Procurement Example
To make it concrete, here's what happens when someone requests 100 laptops:

Employee fills form → POST /api/v1/procurement/request
API creates record, publishes procurement:requested
Orchestrator routes it to Vendor Agent
Vendor Agent fetches vendors from DB, asks Gemini to rank them, stores recommendation
Vendor Agent publishes procurement:vendor_analyzed
Orchestrator routes to Procurement Agent
Procurement Agent picks the top vendor, asks Gemini to write a formal email, creates a draft Purchase Order
Publishes procurement:po_draft_ready
Notification Agent emails the requester: "Your PO draft is ready"
Requester reviews the email draft in the UI, clicks Send
POST /api/v1/procurement/purchase-orders/{id}/send-email fires the actual email to the vendor