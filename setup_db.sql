-- INITIALIZE TABLES FOR AI OPS PLATFORM

-- 1. Departments
CREATE TABLE IF NOT EXISTS departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    manager_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Employees
CREATE TABLE IF NOT EXISTS employees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_user_id UUID UNIQUE,
    employee_code TEXT UNIQUE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    department_id UUID REFERENCES departments(id),
    role TEXT NOT NULL DEFAULT 'employee',
    designation TEXT,
    employment_type TEXT DEFAULT 'full_time',
    status TEXT DEFAULT 'active',
    salary_base DECIMAL(12,2),
    join_date DATE DEFAULT CURRENT_DATE,
    manager_id UUID REFERENCES employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Projects (New - required by TaskAgent)
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    manager_id UUID REFERENCES employees(id),
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    project_id UUID REFERENCES projects(id),
    assigned_to UUID REFERENCES employees(id),
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'todo',
    due_date TIMESTAMP WITH TIME ZONE,
    completion_percent INTEGER DEFAULT 0,
    estimated_hours DECIMAL(6,2),
    actual_hours DECIMAL(6,2),
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Leave Policies
CREATE TABLE IF NOT EXISTS leave_policies (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    leave_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Leaves (Required by HRAgent)
CREATE TABLE IF NOT EXISTS leaves (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    leave_type TEXT NOT NULL DEFAULT 'casual',
    policy_id TEXT REFERENCES leave_policies(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days DECIMAL(4,1),
    reason TEXT,
    status TEXT DEFAULT 'pending',
    rejection_reason TEXT,
    ai_decision JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Leave Balances (New - required by HRAgent)
CREATE TABLE IF NOT EXISTS leave_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    policy_id TEXT REFERENCES leave_policies(id),
    total_days DECIMAL(4,1) NOT NULL,
    used_days DECIMAL(4,1) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, policy_id)
);

-- 7. Vendors
CREATE TABLE IF NOT EXISTS vendors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    category TEXT,
    rating DECIMAL(3,2),
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Procurement Requests
CREATE TABLE IF NOT EXISTS procurement_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requester_id UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    product_name TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    estimated_budget DECIMAL(12,2),
    urgency TEXT DEFAULT 'normal',
    category TEXT,
    status TEXT DEFAULT 'pending',
    selected_vendor_id UUID REFERENCES vendors(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. Agent Events (Used across agents)
CREATE TABLE IF NOT EXISTS agent_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB,
    status TEXT DEFAULT 'processing',
    result JSONB,
    error_message TEXT,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. Meetings
CREATE TABLE IF NOT EXISTS meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    organizer_id UUID REFERENCES employees(id),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location TEXT,
    meeting_url TEXT,
    status TEXT DEFAULT 'scheduled',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 11. Product Trends
CREATE TABLE IF NOT EXISTS product_trends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_name TEXT UNIQUE NOT NULL,
    category TEXT,
    trend_score DECIMAL(3,2),
    longevity_estimate TEXT,
    sustainability_score DECIMAL(3,2),
    summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 12. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipient_id UUID REFERENCES employees(id),
    type TEXT NOT NULL,
    title TEXT,
    body TEXT,
    data JSONB,
    sent_via TEXT[] DEFAULT ARRAY['in_app'],
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AUTOMATIC EMPLOYEE CREATION TRIGGER
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.employees (auth_user_id, full_name, email, role, status)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email), NEW.email, 'admin', 'active');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'on_auth_user_created') THEN
        CREATE TRIGGER on_auth_user_created
        AFTER INSERT ON auth.users
        FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
    END IF;
END $$;

-- INITIAL DATA SEED
INSERT INTO departments (name) VALUES ('Management'), ('Engineering'), ('HR'), ('Finance'), ('Sales'), ('Product') ON CONFLICT DO NOTHING;
