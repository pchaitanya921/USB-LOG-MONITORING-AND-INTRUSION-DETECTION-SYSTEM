import { useState, useEffect } from 'react'
import { FiSearch, FiFilter } from 'react-icons/fi'
import { fetchScans } from '../api/scans'
import { fetchDevices } from '../api/devices'
import ScanResultCard from '../components/ScanResultCard'

const Scans = () => {
  const [scans, setScans] = useState([])
  const [devices, setDevices] = useState({})
  const [filteredScans, setFilteredScans] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [filter, setFilter] = useState('all') // 'all', 'clean', 'infected', 'suspicious'
  const [searchTerm, setSearchTerm] = useState('')
  
  useEffect(() => {
    // Load initial data
    fetchData()
  }, [])
  
  useEffect(() => {
    // Apply filters and search
    let result = [...scans]
    
    // Apply status filter
    if (filter === 'clean') {
      result = result.filter(scan => scan.infected_files === 0 && scan.suspicious_files === 0)
    } else if (filter === 'infected') {
      result = result.filter(scan => scan.infected_files > 0)
    } else if (filter === 'suspicious') {
      result = result.filter(scan => scan.suspicious_files > 0 && scan.infected_files === 0)
    }
    
    // Apply search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      result = result.filter(scan => {
        const device = devices[scan.device_id]
        if (!device) return false
        
        return (
          (device.product_name && device.product_name.toLowerCase().includes(term)) ||
          (device.manufacturer && device.manufacturer.toLowerCase().includes(term)) ||
          (device.serial_number && device.serial_number.toLowerCase().includes(term))
        )
      })
    }
    
    // Sort by scan date (newest first)
    result.sort((a, b) => new Date(b.scan_date) - new Date(a.scan_date))
    
    setFilteredScans(result)
  }, [scans, devices, filter, searchTerm])
  
  const fetchData = async () => {
    setIsLoading(true)
    
    try {
      // Fetch all scans
      const scansData = await fetchScans()
      setScans(scansData)
      
      // Fetch all devices and create a lookup map
      const devicesData = await fetchDevices()
      const devicesMap = {}
      devicesData.forEach(device => {
        devicesMap[device.id] = device
      })
      setDevices(devicesMap)
    } catch (error) {
      console.error('Error fetching data:', error)
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
              All Scans
            </button>
            <button
              onClick={() => setFilter('clean')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'clean'
                  ? 'bg-success-100 text-success-800 dark:bg-success-800 dark:text-success-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Clean
            </button>
            <button
              onClick={() => setFilter('infected')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'infected'
                  ? 'bg-danger-100 text-danger-800 dark:bg-danger-800 dark:text-danger-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Infected
            </button>
            <button
              onClick={() => setFilter('suspicious')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'suspicious'
                  ? 'bg-warning-100 text-warning-800 dark:bg-warning-800 dark:text-warning-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Suspicious
            </button>
          </div>
          
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FiSearch className="text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search by device..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
      </div>
      
      {filteredScans.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredScans.map(scan => (
            <ScanResultCard 
              key={scan.id} 
              scan={scan} 
              deviceName={devices[scan.device_id]?.product_name} 
            />
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
          <FiSearch size={48} className="mx-auto text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-800 dark:text-white">
            No scans found
          </h3>
          <p className="mt-2 text-gray-500 dark:text-gray-400">
            {scans.length > 0
              ? 'No scans match your current filters'
              : 'No scans have been performed yet'}
          </p>
        </div>
      )}
    </div>
  )
}

export default Scans
