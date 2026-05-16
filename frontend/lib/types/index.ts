export interface Employee {
  id: string
  employee_code: string
  full_name: string
  email: string
  phone?: string
  role: string
  designation?: string
  employment_type: string
  status: string
  salary_base?: number
  join_date: string
  department_id?: string
  departments?: { name: string }
  created_at: string
}

export interface Task {
  id: string
  title: string
  description?: string
  project_id?: string
  assigned_to?: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'todo' | 'in_progress' | 'review' | 'done' | 'blocked'
  due_date?: string
  completion_percent: number
  created_at: string
}

export interface LeaveRequest {
  id: string
  employee_id: string
  start_date: string
  end_date: string
  total_days: number
  reason?: string
  status: 'pending' | 'ai_approved' | 'approved' | 'rejected' | 'escalated'
  ai_decision?: {
    decision: string
    confidence: number
    reason: string
    notify_manager: boolean
  }
  created_at: string
}

export interface Meeting {
  id: string
  title: string
  organizer_id: string
  meeting_type: string
  scheduled_at: string
  duration_minutes: number
  status: string
  ai_summary?: string
  action_items?: any[]
  created_at: string
}

export interface Vendor {
  id: string
  name: string
  email?: string
  category?: string
  country?: string
  reliability_score?: number
  quality_score?: number
  price_competitiveness?: number
  verified: boolean
}

export interface ProcurementRequest {
  id: string
  product_name: string
  description?: string
  quantity: number
  estimated_budget?: number
  urgency: string
  status: string
  ai_recommendation?: any
  created_at: string
}

export interface ProductTrend {
  id: string
  product_name: string
  category?: string
  trend_score: number
  longevity_estimate: string
  sustainability_score: number
  ai_analysis?: string
  identified_at: string
}

export interface AgentEvent {
  id: string
  agent_name: string
  event_type: string
  status: string
  processing_time_ms?: number
  error_message?: string
  created_at: string
}
