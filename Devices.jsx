import { useState, useEffect } from 'react'
import { FiHardDrive, FiSearch } from 'react-icons/fi'
import { fetchDevices } from '../api/devices'
import DeviceCard from '../components/DeviceCard'

const Devices = ({ socket }) => {
  const [devices, setDevices] = useState([])
  const [filteredDevices, setFilteredDevices] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [filter, setFilter] = useState('all') // 'all', 'connected', 'disconnected'
  const [searchTerm, setSearchTerm] = useState('')
  
  useEffect(() => {
    // Load initial data
    fetchDevicesData()
    
    // Set up socket event listeners
    if (socket) {
      socket.on('usb_connected', () => {
        fetchDevicesData()
      })
      
      socket.on('usb_disconnected', () => {
        fetchDevicesData()
      })
    }
    
    // Cleanup
    return () => {
      if (socket) {
        socket.off('usb_connected')
        socket.off('usb_disconnected')
      }
    }
  }, [socket])
  
  useEffect(() => {
    // Apply filters and search
    let result = [...devices]
    
    // Apply connection filter
    if (filter === 'connected') {
      result = result.filter(device => device.is_connected)
    } else if (filter === 'disconnected') {
      result = result.filter(device => !device.is_connected)
    }
    
    // Apply search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(device => 
        (device.product_name && device.product_name.toLowerCase().includes(term)) ||
        (device.manufacturer && device.manufacturer.toLowerCase().includes(term)) ||
        (device.serial_number && device.serial_number.toLowerCase().includes(term))
      )
    }
    
    setFilteredDevices(result)
  }, [devices, filter, searchTerm])
  
  const fetchDevicesData = async () => {
    setIsLoading(true)
    
    try {
      const data = await fetchDevices()
      setDevices(data)
    } catch (error) {
      console.error('Error fetching devices:', error)
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
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setFilter('all')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'all'
                  ? 'bg-primary-100 text-primary-800 dark:bg-primary-800 dark:text-primary-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              All Devices
            </button>
            <button
              onClick={() => setFilter('connected')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'connected'
                  ? 'bg-success-100 text-success-800 dark:bg-success-800 dark:text-success-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Connected
            </button>
            <button
              onClick={() => setFilter('disconnected')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'disconnected'
                  ? 'bg-gray-300 text-gray-800 dark:bg-gray-600 dark:text-gray-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Disconnected
            </button>
          </div>
          
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FiSearch className="text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search devices..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>
      
      {filteredDevices.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDevices.map(device => (
            <DeviceCard key={device.id} device={device} />
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
          <FiHardDrive size={48} className="mx-auto text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-800 dark:text-white">
            No devices found
          </h3>
          <p className="mt-2 text-gray-500 dark:text-gray-400">
            {devices.length > 0
              ? 'No devices match your current filters'
              : 'No USB devices have been detected yet'}
          </p>
        </div>
      )}
    </div>
  )
}

export default Devices
