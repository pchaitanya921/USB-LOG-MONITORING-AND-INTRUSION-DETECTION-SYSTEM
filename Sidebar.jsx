import { NavLink } from 'react-router-dom'
import {
  FiHome,
  FiHardDrive,
  FiSearch,
  FiBell,
  FiSettings,
  FiShield
} from 'react-icons/fi'

const Sidebar = ({ unreadAlerts = 0 }) => {
  const navItems = [
    { to: '/', icon: <FiHome size={20} />, label: 'Dashboard' },
    { to: '/devices', icon: <FiHardDrive size={20} />, label: 'USB Devices' },
    { to: '/scans', icon: <FiSearch size={20} />, label: 'Scan History' },
    {
      to: '/alerts',
      icon: <FiBell size={20} />,
      label: 'Alerts',
      badge: unreadAlerts > 0 ? unreadAlerts : null
    },
    { to: '/settings', icon: <FiSettings size={20} />, label: 'Settings' },
  ]

  return (
    <div className="w-64 bg-gradient-to-b from-primary-900 to-primary-800 text-white flex flex-col slide-in-left">
      <div className="p-6 flex items-center space-x-3 border-b border-primary-700/50">
        <div className="p-2 rounded-lg bg-primary-700/50 neon-border">
          <FiShield size={28} className="text-primary-300 neon-icon" />
        </div>
        <h1 className="text-xl font-bold neon-text">USB Monitor</h1>
      </div>

      <nav className="flex-1 mt-6">
        <ul className="space-y-1">
          {navItems.map((item, index) => (
            <li key={item.to} className="px-4 stagger-item">
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center p-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-700/70 text-white neon-border'
                      : 'text-primary-100 hover:bg-primary-700/50 hover:translate-x-1'
                  }`
                }
              >
                <span className={`mr-3 transition-transform duration-300 ${item.to === '/scans' ? 'icon-scan' : ''}`}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
                {item.badge && (
                  <span className="ml-auto bg-danger-500 text-white text-xs font-semibold px-2 py-1 rounded-full pulse">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="p-6 text-sm text-primary-300 border-t border-primary-700/50">
        <div className="typing-code w-full overflow-hidden whitespace-nowrap">
          <p>USB Log Monitoring and</p>
          <p>Intrusion Detection System</p>
        </div>
        <div className="flex items-center mt-3 justify-between">
          <p>v1.0.0</p>
          <div className="flex space-x-1">
            <span className="h-2 w-2 bg-green-500 rounded-full"></span>
            <span className="h-2 w-2 bg-primary-500 rounded-full animate-pulse"></span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar
