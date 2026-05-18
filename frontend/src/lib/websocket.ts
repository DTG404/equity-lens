'use client';

import { useEffect, useRef, useState } from 'react';

interface LiveQuote {
  symbol: string;
  price: number;
  change_percent: number;
  provider: string;
  previous_close: number | null;
}

interface WSMessage {
  type: 'quotes' | 'info' | 'error';
  data?: LiveQuote[];
  message?: string;
  timestamp?: number;
}

export function useLiveQuotes() {
  const [quotes, setQuotes] = useState<LiveQuote[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = process.env.NEXT_PUBLIC_WS_URL || `${protocol}//localhost:8000`;
    const ws = new WebSocket(`${host}/ws/quotes`);

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);
        if (msg.type === 'quotes' && msg.data) {
          setQuotes(msg.data);
        }
      } catch { /* ignore parse errors */ }
    };

    wsRef.current = ws;
    return () => { ws.close(); };
  }, []);

  return { quotes, connected };
}
