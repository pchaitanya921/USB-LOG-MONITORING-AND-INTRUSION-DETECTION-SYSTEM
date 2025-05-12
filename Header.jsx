import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { FiRefreshCw, FiMoon, FiSun, FiShield } from 'react-icons/fi'
import { refreshDevices } from '../api/devices'
import { toast } from 'react-toastify'

const Header = ({ darkMode, toggleDarkMode }) => {
  const location = useLocation()
  const [title, setTitle] = useState('Dashboard')
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    // Set page title based on current route
    const path = location.pathname

    if (path === '/') {
      setTitle('Dashboard')
    } else if (path.startsWith('/devices')) {
      if (path === '/devices') {
        setTitle('USB Devices')
      } else {
        setTitle('Device Details')
      }
    } else if (path.startsWith('/scans')) {
      if (path === '/scans') {
        setTitle('Scan History')
      } else {
        setTitle('Scan Details')
      }
    } else if (path === '/alerts') {
      setTitle('Alerts')
    } else if (path === '/settings') {
      setTitle('Settings')
    }
  }, [location])

  const handleRefresh = async () => {
    if (isRefreshing) return

    setIsRefreshing(true)

    try {
      await refreshDevices()
      toast.success('Devices refreshed successfully')
    } catch (error) {
      toast.error('Error refreshing devices')
      console.error('Error refreshing devices:', error)
    } finally {
      setIsRefreshing(false)
    }
  }

  return (
    <header className={`${darkMode ? 'glass' : 'bg-white'} shadow slide-in-down`}>
      <div className="flex justify-between items-center px-6 py-4">
        <div className="flex items-center">
          <FiShield className={`mr-3 text-2xl ${darkMode ? 'text-primary-400 neon-icon' : 'text-primary-600'}`} />
          <h1 className={`text-2xl font-semibold ${darkMode ? 'text-white' : 'text-gray-800'} ${darkMode ? 'neon-text' : ''}`}>
            {title}
          </h1>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={toggleDarkMode}
            className={`flex items-center p-2 rounded-full ${
              darkMode
                ? 'bg-gray-700 text-yellow-300 hover:bg-gray-600'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            } transition-colors duration-200`}
            aria-label="Toggle dark mode"
          >
            {darkMode ? <FiSun className="text-xl" /> : <FiMoon className="text-xl" />}
          </button>

          <button
            onClick={handleRefresh}
            className={`flex items-center px-3 py-2 text-sm font-medium rounded-md ${
              darkMode
                ? 'text-gray-200 bg-gray-700 hover:bg-gray-600 neon-border'
                : 'text-gray-700 bg-gray-100 hover:bg-gray-200'
            } focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all duration-200`}
            disabled={isRefreshing}
          >
            <FiRefreshCw className={`mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh Devices
          </button>
        </div>
      </div>
    </header>
  )
}

export default Header
