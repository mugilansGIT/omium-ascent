-- SEED DATA FOR SCALERS CORP (STARK INDUSTRIES DIVISION)

-- 1. Create Employees (Managers First)
-- Management
INSERT INTO employees (full_name, email, role, designation, status)
VALUES ('Tony Stark', 'tony@stark.com', 'admin', 'CEO', 'active')
ON CONFLICT (email) DO NOTHING;

-- Get Tony's ID for reference
DO $$
DECLARE
    tony_id UUID;
    engineering_dept UUID;
    hr_dept UUID;
    finance_dept UUID;
    pepper_id UUID;
    happy_id UUID;
BEGIN
    SELECT id INTO tony_id FROM employees WHERE email = 'tony@stark.com';
    SELECT id INTO engineering_dept FROM departments WHERE name = 'Engineering';
    SELECT id INTO hr_dept FROM departments WHERE name = 'HR';
    SELECT id INTO finance_dept FROM departments WHERE name = 'Finance';

    -- 2. LEAVE POLICIES
    INSERT INTO leave_policies (id, name, leave_type, description)
    VALUES ('annual', 'Annual Leave', 'vacation', 'Standard yearly paid leave')
    ON CONFLICT (id) DO NOTHING;

    -- 3. Pepper Potts (COO / Management / Reports to Tony)
    INSERT INTO employees (full_name, email, role, designation, department_id, manager_id, status)
    VALUES ('Pepper Potts', 'pepper@stark.com', 'admin', 'COO', (SELECT id FROM departments WHERE name = 'Management'), tony_id, 'active')
    ON CONFLICT (email) DO NOTHING;
    
    SELECT id INTO pepper_id FROM employees WHERE email = 'pepper@stark.com';

    -- 3. Happy Hogan (Head of Security / Reports to Tony)
    INSERT INTO employees (full_name, email, role, designation, department_id, manager_id, status)
    VALUES ('Happy Hogan', 'happy@stark.com', 'employee', 'Head of Security', engineering_dept, tony_id, 'active')
    ON CONFLICT (email) DO NOTHING;

    -- 4. Bruce Banner (Head of R&D / Engineering / Reports to Tony)
    INSERT INTO employees (full_name, email, role, designation, department_id, manager_id, status)
    VALUES ('Bruce Banner', 'bruce@stark.com', 'employee', 'Chief Scientist', engineering_dept, tony_id, 'active')
    ON CONFLICT (email) DO NOTHING;

    -- 5. Natasha Romanoff (HR Lead / Reports to Pepper)
    INSERT INTO employees (full_name, email, role, designation, department_id, manager_id, status)
    VALUES ('Natasha Romanoff', 'natasha@stark.com', 'employee', 'HR Director', hr_dept, pepper_id, 'active')
    ON CONFLICT (email) DO NOTHING;

    -- 6. Engineering Team (Report to Bruce)
    INSERT INTO employees (full_name, email, role, designation, department_id, manager_id, status)
    VALUES 
    ('Peter Parker', 'peter@stark.com', 'employee', 'Junior Engineer', engineering_dept, (SELECT id FROM employees WHERE email = 'bruce@stark.com'), 'active'),
    ('Harley Keener', 'harley@stark.com', 'employee', 'Systems Intern', engineering_dept, (SELECT id FROM employees WHERE email = 'bruce@stark.com'), 'active')
    ON CONFLICT (email) DO NOTHING;

    -- 7. PROJECTS
    INSERT INTO projects (name, description, manager_id)
    VALUES ('Arc Reactor 2.0', 'Clean energy initiative', tony_id)
    ON CONFLICT (name) DO NOTHING;

    -- 8. TASKS
    INSERT INTO tasks (title, description, project_id, assigned_to, priority, status, due_date)
    VALUES 
    ('Thermal Shielding', 'Improve heat dissipation for the core', (SELECT id FROM projects WHERE name = 'Arc Reactor 2.0'), (SELECT id FROM employees WHERE email = 'peter@stark.com'), 'high', 'in_progress', NOW() + INTERVAL '2 days'),
    ('Security Audit', 'Scan all lab perimeters', NULL, (SELECT id FROM employees WHERE email = 'happy@stark.com'), 'medium', 'todo', NOW() + INTERVAL '5 days')
    ON CONFLICT DO NOTHING;

    -- 9. LEAVE BALANCES
    INSERT INTO leave_balances (employee_id, policy_id, total_days, used_days)
    SELECT id, 'annual', 25, 5 FROM employees
    ON CONFLICT (employee_id, policy_id) DO NOTHING;

END $$;
