'use client';

import React, { useEffect, useState } from 'react';
import {
  fetchAlertRules,
  fetchAlertEvents,
  fetchUnreadAlertCount,
  markAlertRead,
  markAllAlertsRead,
  createAlertRule,
  deleteAlertRule,
  type AlertRule,
  type AlertEvent,
} from '@/lib/api';

const severityColors: Record<string, string> = {
  info: '#3b82f6',
  warning: '#f59e0b',
  critical: '#ef4444',
};

const alertTypeIcons: Record<string, string> = {
  price: '$',
  news: 'N',
  signal: 'S',
  risk: 'R',
};

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffDay > 0) return `${diffDay}d ago`;
  if (diffHour > 0) return `${diffHour}h ago`;
  if (diffMin > 0) return `${diffMin}m ago`;
  return 'just now';
}

export default function AlertCenter() {
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [events, setEvents] = useState<AlertEvent[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [showAddRule, setShowAddRule] = useState(false);
  const [newSymbol, setNewSymbol] = useState('');
  const [newAlertType, setNewAlertType] = useState('price');
  const [newCondition, setNewCondition] = useState('above');
  const [newThreshold, setNewThreshold] = useState('');

  const loadAlerts = async () => {
    try {
      const [rulesData, eventsData, countData] = await Promise.all([
        fetchAlertRules(),
        fetchAlertEvents(),
        fetchUnreadAlertCount(),
      ]);
      setRules(rulesData);
      setEvents(eventsData);
      setUnreadCount(countData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load alerts');
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleMarkRead = async (id: number) => {
    try {
      await markAlertRead(id);
      setEvents((prev) =>
        prev.map((ev) => (ev.id === id ? { ...ev, read: true } : ev)),
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark read');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllAlertsRead();
      setEvents((prev) => prev.map((ev) => ({ ...ev, read: true })));
      setUnreadCount(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to mark all read');
    }
  };

  const handleAddRule = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol.trim() || !newThreshold) return;
    try {
      await createAlertRule(
        newSymbol.trim().toUpperCase(),
        newAlertType,
        newCondition,
        parseFloat(newThreshold),
      );
      setNewSymbol('');
      setNewThreshold('');
      setShowAddRule(false);
      const updated = await fetchAlertRules();
      setRules(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add rule');
    }
  };

  const handleDeleteRule = async (id: number) => {
    try {
      await deleteAlertRule(id);
      setRules((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete rule');
    }
  };

  return (
    <div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 12,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <h3 style={{ fontSize: 15, fontWeight: 600, margin: 0 }}>Alerts</h3>
          {unreadCount > 0 && (
            <span
              style={{
                background: '#ef4444',
                color: '#fff',
                fontSize: 11,
                fontWeight: 700,
                padding: '2px 6px',
                borderRadius: 10,
                minWidth: 18,
                textAlign: 'center',
              }}
            >
              {unreadCount}
            </span>
          )}
        </div>
        {unreadCount > 0 && (
          <button
            type="button"
            onClick={handleMarkAllRead}
            style={{
              background: 'transparent',
              border: '1px solid var(--border)',
              borderRadius: 4,
              padding: '4px 10px',
              fontSize: 12,
              cursor: 'pointer',
              color: 'var(--text-secondary)',
            }}
          >
            Mark all read
          </button>
        )}
      </div>

      {error && (
        <p style={{ color: 'var(--accent-red)', fontSize: 13, marginBottom: 8 }}>
          {error}
        </p>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 12 }}>
        {events.length === 0 ? (
          <p style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
            No alerts yet.
          </p>
        ) : (
          events.slice(0, 5).map((event) => (
            <div
              key={event.id}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 8,
                padding: '8px 0',
                borderBottom: '1px solid var(--border)',
                opacity: event.read ? 0.6 : 1,
              }}
            >
              <span
                style={{
                  width: 22,
                  height: 22,
                  borderRadius: '50%',
                  background: severityColors[event.severity] || '#6b7280',
                  color: '#fff',
                  fontSize: 11,
                  fontWeight: 700,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  marginTop: 2,
                }}
              >
                {alertTypeIcons[event.alert_type] || '?'}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: event.read ? 400 : 600,
                    color: 'var(--text-primary)',
                    wordBreak: 'break-word',
                  }}
                >
                  {event.message}
                </div>
                <div
                  style={{
                    fontSize: 11,
                    color: 'var(--text-secondary)',
                    marginTop: 2,
                    display: 'flex',
                    justifyContent: 'space-between',
                  }}
                >
                  <span>
                    {event.symbol} · {event.severity}
                  </span>
                  <span>{formatRelativeTime(event.triggered_at)}</span>
                </div>
              </div>
              {!event.read && (
                <button
                  type="button"
                  onClick={() => handleMarkRead(event.id)}
                  style={{
                    background: 'transparent',
                    border: '1px solid var(--border)',
                    borderRadius: 4,
                    padding: '2px 8px',
                    fontSize: 11,
                    cursor: 'pointer',
                    color: 'var(--text-secondary)',
                    flexShrink: 0,
                  }}
                >
                  Mark read
                </button>
              )}
              {event.read && (
                <span
                  style={{
                    fontSize: 11,
                    color: 'var(--text-secondary)',
                    flexShrink: 0,
                    padding: '2px 8px',
                  }}
                >
                  read
                </span>
              )}
            </div>
          ))
        )}
      </div>

      <button
        type="button"
        onClick={() => setShowAddRule((prev) => !prev)}
        style={{
          background: 'transparent',
          border: '1px solid var(--border)',
          borderRadius: 4,
          padding: '6px 12px',
          fontSize: 13,
          cursor: 'pointer',
          color: 'var(--text-secondary)',
          marginBottom: showAddRule ? 8 : 0,
        }}
      >
        {showAddRule ? 'Cancel' : 'Add Rule'}
      </button>

      {showAddRule && (
        <form
          onSubmit={handleAddRule}
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            padding: 12,
            border: '1px solid var(--border)',
            borderRadius: 6,
            background: 'var(--bg-card)',
          }}
        >
          <input
            type="text"
            placeholder="Symbol"
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            style={{
              padding: '6px 10px',
              borderRadius: 4,
              border: '1px solid var(--border)',
              background: 'var(--bg-secondary)',
              color: 'var(--text-primary)',
              fontSize: 13,
            }}
          />
          <div style={{ display: 'flex', gap: 8 }}>
            <select
              value={newAlertType}
              onChange={(e) => setNewAlertType(e.target.value)}
              style={{
                flex: 1,
                padding: '6px 10px',
                borderRadius: 4,
                border: '1px solid var(--border)',
                background: 'var(--bg-secondary)',
                color: 'var(--text-primary)',
                fontSize: 13,
              }}
            >
              <option value="price">price</option>
              <option value="news">news</option>
              <option value="signal">signal</option>
              <option value="risk">risk</option>
            </select>
            <select
              value={newCondition}
              onChange={(e) => setNewCondition(e.target.value)}
              style={{
                flex: 1,
                padding: '6px 10px',
                borderRadius: 4,
                border: '1px solid var(--border)',
                background: 'var(--bg-secondary)',
                color: 'var(--text-primary)',
                fontSize: 13,
              }}
            >
              <option value="above">above</option>
              <option value="below">below</option>
            </select>
          </div>
          <input
            type="number"
            placeholder="Threshold"
            value={newThreshold}
            onChange={(e) => setNewThreshold(e.target.value)}
            style={{
              padding: '6px 10px',
              borderRadius: 4,
              border: '1px solid var(--border)',
              background: 'var(--bg-secondary)',
              color: 'var(--text-primary)',
              fontSize: 13,
            }}
          />
          <button
            type="submit"
            style={{
              padding: '6px 12px',
              borderRadius: 4,
              border: 'none',
              background: 'var(--accent-blue, #3b82f6)',
              color: '#fff',
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Create Rule
          </button>
        </form>
      )}

      {rules.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <h4
            style={{
              fontSize: 13,
              fontWeight: 600,
              marginBottom: 8,
              color: 'var(--text-secondary)',
            }}
          >
            Active Rules
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {rules.map((rule) => (
              <div
                key={rule.id}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '6px 8px',
                  borderRadius: 4,
                  border: '1px solid var(--border)',
                  background: 'var(--bg-card)',
                }}
              >
                <span style={{ fontSize: 12 }}>
                  {rule.symbol} {rule.alert_type} {rule.condition} ${rule.threshold}
                </span>
                <button
                  type="button"
                  onClick={() => handleDeleteRule(rule.id)}
                  style={{
                    background: 'transparent',
                    border: '1px solid var(--border)',
                    borderRadius: 4,
                    padding: '2px 8px',
                    fontSize: 11,
                    cursor: 'pointer',
                    color: 'var(--text-secondary)',
                  }}
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
