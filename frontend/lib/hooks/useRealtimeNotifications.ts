"use client"
import { useEffect } from "react"
import { createClient } from "@/lib/supabase/client"

export function useRealtimeNotifications(employeeId: string, onNotification: (n: any) => void) {
  const supabase = createClient()

  useEffect(() => {
    if (!employeeId) return

    const channel = supabase
      .channel("notifications")
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "notifications",
          filter: `recipient_id=eq.${employeeId}`,
        },
        (payload) => onNotification(payload.new)
      )
      .subscribe()

    return () => { supabase.removeChannel(channel) }
  }, [employeeId])
}
