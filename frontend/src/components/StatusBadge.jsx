import React from 'react';

export default function StatusBadge({ status }) {
  const stLower = (status || 'open').toLowerCase();
  let badgeClass = 'badge-status-open';

  if (stLower === 'investigating') badgeClass = 'badge-status-investigating';
  else if (stLower === 'resolved') badgeClass = 'badge-status-resolved';

  return (
    <span className={`badge ${badgeClass}`}>
      {status || 'Open'}
    </span>
  );
}
