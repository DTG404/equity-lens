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
  info: 'bg-blue-400',
  warning: 'bg-amber-400',
  critical: 'bg-red-400',
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
      <div className="flex justify-between items-center mb-3">
        <div className="flex items-center gap-2">
          <h3 className="text-xs uppercase tracking-wider text-white/40 m-0 font-semibold">
            Alerts
          </h3>
          {unreadCount > 0 && (
            <span className="bg-red-500 text-white text-[0.6rem] font-bold px-1.5 py-0.5 rounded-full min-w-[18px] text-center leading-none">
              {unreadCount}
            </span>
          )}
        </div>
        {unreadCount > 0 && (
          <button
            type="button"
            onClick={handleMarkAllRead}
            className="glass-badge-amber text-xs"
          >
            Mark all read
          </button>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-400 mb-2">{error}</p>
      )}

      <div className="flex flex-col gap-2 mb-3">
        {events.length === 0 ? (
          <p className="text-xs text-white/25">No alerts yet.</p>
        ) : (
          events.slice(0, 5).map((event) => (
            <div
              key={event.id}
              className={`flex items-start gap-2 py-2 border-b border-white/[0.06] ${event.read ? 'opacity-50' : ''}`}
            >
              <span
                className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${severityColors[event.severity] || 'bg-gray-500'}`}
              />
              <div className="flex-1 min-w-0">
                <div className="text-xs text-[#f0f6fc] break-words">
                  {event.message}
                </div>
                <div className="flex justify-between text-white/30 text-[0.65rem] mt-0.5">
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
                  className="glass-badge-cyan text-[0.55rem] shrink-0"
                >
                  Mark read
                </button>
              )}
              {event.read && (
                <span className="text-white/40 text-[0.55rem] shrink-0 px-1 py-0.5">
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
        className={`glass-badge-cyan text-xs ${showAddRule ? 'mb-2' : ''}`}
      >
        {showAddRule ? 'Cancel' : 'Add Rule'}
      </button>

      {showAddRule && (
        <form
          onSubmit={handleAddRule}
          className="flex flex-col gap-2 p-3 rounded-lg border border-white/[0.06] bg-white/[0.03]"
        >
          <input
            type="text"
            placeholder="Symbol"
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            className="rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#f0f6fc] placeholder-white/25 outline-none transition-colors focus:border-cyan-400/30"
          />
          <div className="flex gap-2">
            <select
              value={newAlertType}
              onChange={(e) => setNewAlertType(e.target.value)}
              className="flex-1 rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#f0f6fc] outline-none transition-colors focus:border-cyan-400/30"
            >
              <option value="price">price</option>
              <option value="news">news</option>
              <option value="signal">signal</option>
              <option value="risk">risk</option>
            </select>
            <select
              value={newCondition}
              onChange={(e) => setNewCondition(e.target.value)}
              className="flex-1 rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#f0f6fc] outline-none transition-colors focus:border-cyan-400/30"
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
            className="rounded-lg border border-white/[0.06] bg-white/[0.03] px-3 py-2 text-sm text-[#f0f6fc] placeholder-white/25 outline-none transition-colors focus:border-cyan-400/30"
          />
          <button
            type="submit"
            className="glass-badge-cyan rounded-lg px-4 py-2 text-xs font-semibold uppercase tracking-wider"
          >
            Create Rule
          </button>
        </form>
      )}

      {rules.length > 0 && (
        <div className="mt-3">
          <h4 className="text-xs uppercase tracking-wider text-white/40 mb-2 font-semibold">
            Active Rules
          </h4>
          <div className="flex flex-col gap-1.5">
            {rules.map((rule) => (
              <div
                key={rule.id}
                className="flex justify-between items-center px-2 py-1.5 rounded border border-white/[0.06] bg-white/[0.03]"
              >
                <span className="text-xs font-mono text-white/60">
                  {rule.symbol} {rule.alert_type} {rule.condition} ${rule.threshold}
                </span>
                <button
                  type="button"
                  onClick={() => handleDeleteRule(rule.id)}
                  className="glass-badge-red text-[0.55rem]"
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
