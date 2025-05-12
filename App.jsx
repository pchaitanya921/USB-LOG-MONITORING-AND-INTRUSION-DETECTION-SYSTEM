import { useState, useEffect } from 'react'
import { Routes, Route } from 'react-router-dom'
import { io } from 'socket.io-client'
import { toast } from 'react-toastify'

// Components
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import ParticleBackground from './components/ParticleBackground'

// Pages
import Dashboard from './pages/Dashboard'
import Devices from './pages/Devices'
import DeviceDetail from './pages/DeviceDetail'
import Scans from './pages/Scans'
import ScanDetail from './pages/ScanDetail'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'

// API
import { fetchUnreadAlertCount } from './api/alerts'

function App() {
  const [socket, setSocket] = useState(null)
  const [unreadAlerts, setUnreadAlerts] = useState(0)
  const [darkMode, setDarkMode] = useState(true) // Default to dark mode

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io()
    setSocket(newSocket)

    // Socket event listeners
    newSocket.on('connect', () => {
      console.log('Connected to server')
    })

    newSocket.on('usb_connected', (data) => {
      toast.warning(`USB Device Connected: ${data.device.product_name || 'Unknown Device'}`)
      fetchAlertCount()
    })

    newSocket.on('usb_disconnected', (data) => {
      toast.info(`USB Device Disconnected: ${data.device.product_name || 'Unknown Device'}`)
      fetchAlertCount()
    })

    newSocket.on('scan_completed', (data) => {
      if (data.scan.infected_files > 0 || data.scan.suspicious_files > 0) {
        toast.error(`Scan detected ${data.scan.infected_files} malicious and ${data.scan.suspicious_files} suspicious files on ${data.device.product_name || 'Unknown Device'}`)
      } else {
        toast.success(`Scan completed on ${data.device.product_name || 'Unknown Device'}: No threats found`)
      }
      fetchAlertCount()
    })

    newSocket.on('scan_error', (data) => {
      toast.error(`Scan error on ${data.device.product_name || 'Unknown Device'}: ${data.error}`)
      fetchAlertCount()
    })

    // Fetch initial unread alert count
    fetchAlertCount()

    // Cleanup on unmount
    return () => {
      newSocket.disconnect()
    }
  }, [])

  const fetchAlertCount = async () => {
    try {
      const count = await fetchUnreadAlertCount()
      setUnreadAlerts(count)
    } catch (error) {
      console.error('Error fetching unread alert count:', error)
    }
  }

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  // Particle background options
  const particleOptions = {
    particleCount: 50,
    particleColor: darkMode ? '#0ea5e9' : '#0284c7',
    connectParticles: true,
    lineColor: darkMode ? 'rgba(14, 165, 233, 0.2)' : 'rgba(2, 132, 199, 0.1)',
    lineDistance: 150
  }

  return (
    <div className={`flex h-screen ${darkMode ? 'dark-theme animated-bg-subtle' : 'bg-gray-100'}`}>
      {/* Particle Background */}
      {darkMode && <ParticleBackground options={particleOptions} />}

      <Sidebar unreadAlerts={unreadAlerts} />

      <div className="flex flex-col flex-1 overflow-hidden">
        <Header darkMode={darkMode} toggleDarkMode={toggleDarkMode} />

        <main className="flex-1 overflow-y-auto p-4 animate-fade-in">
          <Routes>
            <Route path="/" element={<Dashboard socket={socket} darkMode={darkMode} />} />
            <Route path="/devices" element={<Devices socket={socket} darkMode={darkMode} />} />
            <Route path="/devices/:id" element={<DeviceDetail socket={socket} darkMode={darkMode} />} />
            <Route path="/scans" element={<Scans darkMode={darkMode} />} />
            <Route path="/scans/:id" element={<ScanDetail darkMode={darkMode} />} />
            <Route path="/alerts" element={<Alerts onAlertRead={fetchAlertCount} darkMode={darkMode} />} />
            <Route path="/settings" element={<Settings darkMode={darkMode} toggleDarkMode={toggleDarkMode} />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
