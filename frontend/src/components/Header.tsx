import React from 'react';

interface HeaderProps {
  status: 'online' | 'offline' | 'warning';
}

const Header: React.FC<HeaderProps> = ({ status }) => {
  const statusText = {
    online: 'All systems operational',
    offline: 'System offline',
    warning: 'Limited availability'
  };

  const statusColor = {
    online: 'bg-status-online',
    offline: 'bg-status-offline',
    warning: 'bg-status-warning'
  };

  return (
    <header className="border-b border-border">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-foreground flex items-center justify-center">
              <span className="text-background text-xl font-semibold">L</span>
            </div>
            <h1 className="text-xl font-semibold">Logo Studio</h1>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${statusColor[status]}`} />
            <span className="text-sm text-muted-foreground">{statusText[status]}</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
