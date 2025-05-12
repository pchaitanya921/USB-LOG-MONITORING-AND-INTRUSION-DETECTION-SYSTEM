import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FiHardDrive, FiShield, FiAlertTriangle, FiBell, FiSearch } from 'react-icons/fi'
import { fetchConnectedDevices } from '../api/devices'
import { fetchScans } from '../api/scans'
import { fetchAlerts } from '../api/alerts'
import StatCard from '../components/StatCard'
import DeviceCard from '../components/DeviceCard'
import AlertItem from '../components/AlertItem'

const Dashboard = ({ socket }) => {
  const [connectedDevices, setConnectedDevices] = useState([])
  const [recentAlerts, setRecentAlerts] = useState([])
  const [stats, setStats] = useState({
    totalDevices: 0,
    connectedDevices: 0,
    totalScans: 0,
    totalThreats: 0,
  })
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    // Load initial data
    fetchDashboardData()
    
    // Set up socket event listeners
    if (socket) {
      socket.on('usb_connected', () => {
        fetchDashboardData()
      })
      
      socket.on('usb_disconnected', () => {
        fetchDashboardData()
      })
      
      socket.on('scan_completed', () => {
        fetchDashboardData()
      })
    }
    
    // Cleanup
    return () => {
      if (socket) {
        socket.off('usb_connected')
        socket.off('usb_disconnected')
        socket.off('scan_completed')
      }
    }
  }, [socket])
  
  const fetchDashboardData = async () => {
    setIsLoading(true)
    
    try {
      // Fetch connected devices
      const devices = await fetchConnectedDevices()
      setConnectedDevices(devices)
      
      // Fetch recent alerts
      const alerts = await fetchAlerts({ limit: 5 })
      setRecentAlerts(alerts)
      
      // Fetch stats
      const scans = await fetchScans()
      
      // Calculate total threats
      const totalThreats = scans.reduce((total, scan) => {
        return total + scan.infected_files + scan.suspicious_files
      }, 0)
      
      setStats({
        totalDevices: devices.length,
        connectedDevices: devices.filter(d => d.is_connected).length,
        totalScans: scans.length,
        totalThreats: totalThreats,
      })
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setIsLoading(false)
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Connected Devices" 
          value={stats.connectedDevices} 
          icon={<FiHardDrive size={24} />} 
          color="blue" 
        />
        <StatCard 
          title="Total Devices" 
          value={stats.totalDevices} 
          icon={<FiHardDrive size={24} />} 
          color="gray" 
        />
        <StatCard 
          title="Total Scans" 
          value={stats.totalScans} 
          icon={<FiSearch size={24} />} 
          color="green" 
        />
        <StatCard 
          title="Detected Threats" 
          value={stats.totalThreats} 
          icon={<FiAlertTriangle size={24} />} 
          color={stats.totalThreats > 0 ? "red" : "green"} 
        />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Connected Devices */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
              Connected USB Devices
            </h2>
            <Link 
              to="/devices" 
              className="text-sm text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300"
            >
              View All
            </Link>
          </div>
          
          <div className="p-4">
            {connectedDevices.length > 0 ? (
              <div className="space-y-4">
                {connectedDevices.slice(0, 3).map(device => (
                  <DeviceCard key={device.id} device={device} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FiHardDrive size={48} className="mx-auto text-gray-400" />
                <p className="mt-2 text-gray-500 dark:text-gray-400">
                  No USB devices currently connected
                </p>
              </div>
            )}
          </div>
        </div>
        
        {/* Recent Alerts */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
              Recent Alerts
            </h2>
            <Link 
              to="/alerts" 
              className="text-sm text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300"
            >
              View All
            </Link>
          </div>
          
          <div>
            {recentAlerts.length > 0 ? (
              <div>
                {recentAlerts.map(alert => (
                  <AlertItem key={alert.id} alert={alert} />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <FiBell size={48} className="mx-auto text-gray-400" />
                <p className="mt-2 text-gray-500 dark:text-gray-400">
                  No recent alerts
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
