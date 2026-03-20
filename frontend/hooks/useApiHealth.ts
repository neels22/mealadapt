'use client';

import { useCallback, useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { ApiHealthStatus } from '@/lib/types';

export function useApiHealth() {
  const [health, setHealth] = useState<ApiHealthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const result = await api.getApiHealth();
      setHealth(result);
      setError(null);
    } catch (err) {
      setHealth(null);
      setError(err instanceof Error ? err.message : 'Unable to reach API');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { health, loading, error, refresh };
}
