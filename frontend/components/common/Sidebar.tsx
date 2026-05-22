'use client';

export default function Sidebar({ 
  activeTab, 
  onTabChange 
}: { 
  activeTab: string, 
  onTabChange: (t: string) => void 
}) {
  const tabs = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard' },
    { id: 'agent', icon: '🤖', label: 'Agent Activity' },
    { id: 'routines', icon: '🏋️', label: 'Routines' },
    { id: 'calendar', icon: '📅', label: 'Calendar' },
    { id: 'analytics', icon: '📈', label: 'Analytics' },
    { id: 'settings', icon: '⚙️', label: 'Settings' },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">⚡</div>
        <span className="logo-text">ErgoFlow AI</span>
      </div>

      <nav className="sidebar-nav">
        {tabs.map((tab) => (
          <button 
            key={tab.id}
            className={`nav-item ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => onTabChange(tab.id)}
          >
            <span className="nav-icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="user-badge">
          <div className="user-avatar">AN</div>
          <div className="user-info">
            <div className="user-name">Aditya Nadamuni</div>
            <div className="user-role">Software Engineer</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
