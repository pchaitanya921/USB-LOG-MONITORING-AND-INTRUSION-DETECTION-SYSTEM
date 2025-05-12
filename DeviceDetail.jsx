import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  FiHardDrive, 
  FiCheck, 
  FiX, 
  FiAlertTriangle, 
  FiClock, 
  FiCalendar,
  FiSearch,
  FiShield
} from 'react-icons/fi'
import { formatDistanceToNow, format } from 'date-fns'
import { toast } from 'react-toastify'
import { fetchDeviceById, setDevicePermission } from '../api/devices'
import { fetchDeviceScans } from '../api/scans'
import { startScan } from '../api/scans'
import ScanResultCard from '../components/ScanResultCard'

const DeviceDetail = ({ socket }) => {
  const { id } = useParams()
  const [device, setDevice] = useState(null)
  const [scans, setScans] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isScanLoading, setIsScanLoading] = useState(false)
  
  useEffect(() => {
    // Load initial data
    fetchDeviceData()
    
    // Set up socket event listeners
    if (socket) {
      socket.on('usb_connected', (data) => {
        if (data.device.id === parseInt(id)) {
          fetchDeviceData()
        }
      })
      
      socket.on('usb_disconnected', (data) => {
        if (data.device.id === parseInt(id)) {
          fetchDeviceData()
        }
      })
      
      socket.on('scan_completed', (data) => {
        if (data.device.id === parseInt(id)) {
          fetchDeviceData()
        }
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
  }, [id, socket])
  
  const fetchDeviceData = async () => {
    setIsLoading(true)
    
    try {
      // Fetch device details
      const deviceData = await fetchDeviceById(id)
      setDevice(deviceData)
      
      // Fetch device scans
      const scansData = await fetchDeviceScans(id)
      setScans(scansData)
    } catch (error) {
      console.error('Error fetching device data:', error)
      toast.error('Error loading device data')
    } finally {
      setIsLoading(false)
    }
  }
  
  const handlePermissionChange = async (isPermitted) => {
    try {
      const updatedDevice = await setDevicePermission(id, isPermitted)
      setDevice(updatedDevice)
      
      toast.success(`Device ${isPermitted ? 'permitted' : 'blocked'} successfully`)
    } catch (error) {
      console.error('Error changing device permission:', error)
      toast.error('Error changing device permission')
    }
  }
  
  const handleStartScan = async () => {
    if (!device.is_connected) {
      toast.warning('Cannot scan a disconnected device')
      return
    }
    
    if (!device.is_permitted) {
      toast.warning('Device must be permitted before scanning')
      return
    }
    
    setIsScanLoading(true)
    
    try {
      await startScan(id)
      toast.info('Scan started successfully')
      
      // Refresh scans after a short delay
      setTimeout(() => {
        fetchDeviceData()
      }, 1000)
    } catch (error) {
      console.error('Error starting scan:', error)
      toast.error('Error starting scan')
    } finally {
      setIsScanLoading(false)
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }
  
  if (!device) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
        <FiAlertTriangle size={48} className="mx-auto text-warning-500" />
        <h3 className="mt-4 text-lg font-medium text-gray-800 dark:text-white">
          Device Not Found
        </h3>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
          The device you're looking for doesn't exist or has been removed.
        </p>
        <Link
          to="/devices"
          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Back to Devices
        </Link>
      </div>
    )
  }
  
  // Format dates
  const firstConnected = device.first_connected_at 
    ? format(new Date(device.first_connected_at), 'PPP p')
    : 'Unknown'
  
  const lastConnected = device.last_connected_at 
    ? formatDistanceToNow(new Date(device.last_connected_at), { addSuffix: true })
    : 'Unknown'
  
  const lastDisconnected = device.last_disconnected_at 
    ? formatDistanceToNow(new Date(device.last_disconnected_at), { addSuffix: true })
    : 'Unknown'
  
  return (
    <div className="space-y-6">
      {/* Device Info Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="flex items-center">
              <div className={`p-4 rounded-full ${device.is_connected ? 'bg-success-100 text-success-600' : 'bg-gray-100 text-gray-500'}`}>
                <FiHardDrive size={24} />
              </div>
              
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
                  {device.product_name || 'Unknown Device'}
                </h1>
                <p className="text-gray-500 dark:text-gray-400">
                  {device.manufacturer || 'Unknown Manufacturer'}
                </p>
              </div>
            </div>
            
            <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
              {device.is_connected ? (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-success-100 text-success-800">
                  <FiCheck className="mr-1" />
                  Connected
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                  <FiX className="mr-1" />
                  Disconnected
                </span>
              )}
              
              {device.is_permitted ? (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                  <FiShield className="mr-1" />
                  Permitted
                </span>
              ) : (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-danger-100 text-danger-800">
                  <FiAlertTriangle className="mr-1" />
                  Blocked
                </span>
              )}
            </div>
          </div>
          
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Device Details</h3>
              <dl className="mt-2 space-y-1">
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">Serial Number</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{device.serial_number || 'Unknown'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">Vendor ID</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{device.vendor_id || 'Unknown'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">Product ID</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{device.product_id || 'Unknown'}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">Mount Point</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{device.mount_point || 'Unknown'}</dd>
                </div>
              </dl>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Connection History</h3>
              <dl className="mt-2 space-y-1">
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">First Connected</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{firstConnected}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">Last Connected</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{lastConnected}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-sm text-gray-500 dark:text-gray-400">Last Disconnected</dt>
                  <dd className="text-sm font-medium text-gray-900 dark:text-gray-100">{device.last_disconnected_at ? lastDisconnected : 'N/A'}</dd>
                </div>
              </dl>
            </div>
            
            <div>
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Actions</h3>
              <div className="mt-2 space-y-2">
                {device.is_connected && (
                  <>
                    {device.is_permitted ? (
                      <button
                        onClick={() => handlePermissionChange(false)}
                        className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-danger-600 hover:bg-danger-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-danger-500"
                      >
                        <FiX className="mr-2" />
                        Block Device
                      </button>
                    ) : (
                      <button
                        onClick={() => handlePermissionChange(true)}
                        className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-success-600 hover:bg-success-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-success-500"
                      >
                        <FiCheck className="mr-2" />
                        Permit Device
                      </button>
                    )}
                    
                    <button
                      onClick={handleStartScan}
                      disabled={!device.is_permitted || isScanLoading}
                      className={`w-full inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                        device.is_permitted
                          ? 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500'
                          : 'bg-gray-400 cursor-not-allowed'
                      }`}
                    >
                      {isScanLoading ? (
                        <>
                          <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                          Scanning...
                        </>
                      ) : (
                        <>
                          <FiSearch className="mr-2" />
                          Scan Device
                        </>
                      )}
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Scan History */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
            Scan History
          </h2>
        </div>
        
        <div className="p-6">
          {scans.length > 0 ? (
            <div className="space-y-4">
              {scans.map(scan => (
                <ScanResultCard 
                  key={scan.id} 
                  scan={scan} 
                  deviceName={device.product_name} 
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FiSearch size={48} className="mx-auto text-gray-400" />
              <p className="mt-2 text-gray-500 dark:text-gray-400">
                No scans have been performed on this device yet
              </p>
              {device.is_connected && device.is_permitted && (
                <button
                  onClick={handleStartScan}
                  disabled={isScanLoading}
                  className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  {isScanLoading ? (
                    <>
                      <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                      Scanning...
                    </>
                  ) : (
                    <>
                      <FiSearch className="mr-2" />
                      Start First Scan
                    </>
                  )}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DeviceDetail
