package com.example.planner;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;

public final class PlannerStore {
    private final List<Map<String, Object>> sessions = new ArrayList<>();

    public synchronized void addSession(Map<String, Object> session) {
        this.sessions.addFirst(session);
        while (this.sessions.size() > 8) {
            this.sessions.removeLast();
        }
    }

    public synchronized List<Map<String, Object>> recentSessions() {
        return new ArrayList<>(this.sessions);
    }
}
