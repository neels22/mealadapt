'use client';
import { memo } from 'react';


import { useApiHealth } from '@/hooks/useApiHealth';

function ApiStatusCard() {
  const { health, loading, error, refresh } = useApiHealth();

  if (loading) {
    return (
      <div className="card">
        <p className="text-sm text-(--text-secondary)">Checking API status...</p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold mb-1">Backend Status</h3>
          {health ? (
            <p className="text-sm text-(--text-secondary)">
              {health.service} is {health.status} (v{health.version})
            </p>
          ) : (
            <p className="text-sm text-red-600">Unavailable: {error ?? 'Unknown error'}</p>
          )}
        </div>
        <button
          type="button"
          onClick={refresh}
          className="px-3 py-1.5 rounded-md border text-sm hover:bg-gray-50"
        >
          Refresh
        </button>
      </div>
    </div>
  );
}

export default memo(ApiStatusCard);
