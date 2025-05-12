import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { 
  FiSearch, 
  FiHardDrive, 
  FiAlertTriangle, 
  FiAlertCircle, 
  FiCheckCircle,
  FiFile,
  FiClock
} from 'react-icons/fi'
import { format } from 'date-fns'
import { fetchScanById } from '../api/scans'
import { fetchDeviceById } from '../api/devices'

const ScanDetail = () => {
  const { id } = useParams()
  const [scan, setScan] = useState(null)
  const [device, setDevice] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    fetchScanData()
  }, [id])
  
  const fetchScanData = async () => {
    setIsLoading(true)
    
    try {
      // Fetch scan details
      const scanData = await fetchScanById(id)
      setScan(scanData)
      
      // Fetch device details
      if (scanData.device_id) {
        const deviceData = await fetchDeviceById(scanData.device_id)
        setDevice(deviceData)
      }
    } catch (error) {
      console.error('Error fetching scan data:', error)
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
  
  if (!scan) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
        <FiAlertTriangle size={48} className="mx-auto text-warning-500" />
        <h3 className="mt-4 text-lg font-medium text-gray-800 dark:text-white">
          Scan Not Found
        </h3>
        <p className="mt-2 text-gray-500 dark:text-gray-400">
          The scan you're looking for doesn't exist or has been removed.
        </p>
        <Link
          to="/scans"
          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          Back to Scans
        </Link>
      </div>
    )
  }
  
  // Determine scan status
  let StatusIcon = FiClock
  let statusBg = 'bg-gray-100'
  let statusText = 'text-gray-600'
  let statusLabel = 'In Progress'
  
  if (scan.status === 'completed') {
    if (scan.infected_files > 0) {
      StatusIcon = FiAlertCircle
      statusBg = 'bg-danger-100'
      statusText = 'text-danger-600'
      statusLabel = 'Threats Found'
    } else if (scan.suspicious_files > 0) {
      StatusIcon = FiAlertTriangle
      statusBg = 'bg-warning-100'
      statusText = 'text-warning-600'
      statusLabel = 'Suspicious'
    } else {
      StatusIcon = FiCheckCircle
      statusBg = 'bg-success-100'
      statusText = 'text-success-600'
      statusLabel = 'Clean'
    }
  } else if (scan.status === 'error') {
    StatusIcon = FiAlertTriangle
    statusBg = 'bg-danger-100'
    statusText = 'text-danger-600'
    statusLabel = 'Error'
  }
  
  // Format scan date
  const scanDate = scan.scan_date 
    ? format(new Date(scan.scan_date), 'PPP p')
    : 'Unknown'
  
  return (
    <div className="space-y-6">
      {/* Scan Info Card */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="p-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="flex items-center">
              <div className={`p-4 rounded-full ${statusBg} ${statusText}`}>
                <FiSearch size={24} />
              </div>
              
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-800 dark:text-white">
                  Scan Results
                </h1>
                <p className="text-gray-500 dark:text-gray-400">
                  {scanDate}
                </p>
              </div>
            </div>
            
            <div className="mt-4 md:mt-0">
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${statusBg} ${statusText}`}>
                <StatusIcon className="mr-1" />
                {statusLabel}
              </span>
            </div>
          </div>
          
          {device && (
            <div className="mt-6 flex items-center">
              <FiHardDrive className="text-gray-400" />
              <span className="ml-2 text-gray-500 dark:text-gray-400">Device:</span>
              <Link 
                to={`/devices/${device.id}`}
                className="ml-2 text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300"
              >
                {device.product_name || 'Unknown Device'}
              </Link>
            </div>
          )}
          
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Files</p>
              <p className="mt-1 text-2xl font-semibold text-gray-800 dark:text-white">{scan.total_files}</p>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Scanned Files</p>
              <p className="mt-1 text-2xl font-semibold text-gray-800 dark:text-white">{scan.scanned_files}</p>
            </div>
            
            <div className={`${scan.infected_files > 0 ? 'bg-danger-50 dark:bg-danger-900' : 'bg-gray-50 dark:bg-gray-700'} p-4 rounded-lg`}>
              <p className={`text-sm font-medium ${scan.infected_files > 0 ? 'text-danger-600 dark:text-danger-400' : 'text-gray-500 dark:text-gray-400'}`}>
                Infected Files
              </p>
              <p className={`mt-1 text-2xl font-semibold ${scan.infected_files > 0 ? 'text-danger-700 dark:text-danger-300' : 'text-gray-800 dark:text-white'}`}>
                {scan.infected_files}
              </p>
            </div>
            
            <div className={`${scan.suspicious_files > 0 ? 'bg-warning-50 dark:bg-warning-900' : 'bg-gray-50 dark:bg-gray-700'} p-4 rounded-lg`}>
              <p className={`text-sm font-medium ${scan.suspicious_files > 0 ? 'text-warning-600 dark:text-warning-400' : 'text-gray-500 dark:text-gray-400'}`}>
                Suspicious Files
              </p>
              <p className={`mt-1 text-2xl font-semibold ${scan.suspicious_files > 0 ? 'text-warning-700 dark:text-warning-300' : 'text-gray-800 dark:text-white'}`}>
                {scan.suspicious_files}
              </p>
            </div>
          </div>
          
          {scan.scan_duration && (
            <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
              Scan completed in {scan.scan_duration.toFixed(2)} seconds
            </p>
          )}
        </div>
      </div>
      
      {/* Infected Files */}
      {scan.infected_files > 0 && scan.infected_files && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-danger-50 dark:bg-danger-900">
            <h2 className="text-lg font-semibold text-danger-700 dark:text-danger-300 flex items-center">
              <FiAlertCircle className="mr-2" />
              Infected Files
            </h2>
          </div>
          
          <div className="p-4">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      File Path
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Threat Name
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Threat Type
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {scan.infected_files.filter(file => file.threat_type !== 'suspicious').map((file, index) => (
                    <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200 font-mono">
                        <div className="flex items-center">
                          <FiFile className="mr-2 text-danger-500" />
                          {file.file_path}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-danger-600 dark:text-danger-400">
                        {file.threat_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">
                        <span className="px-2 py-1 rounded-full text-xs bg-danger-100 text-danger-800 dark:bg-danger-800 dark:text-danger-100">
                          {file.threat_type}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
      
      {/* Suspicious Files */}
      {scan.suspicious_files > 0 && scan.infected_files && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-warning-50 dark:bg-warning-900">
            <h2 className="text-lg font-semibold text-warning-700 dark:text-warning-300 flex items-center">
              <FiAlertTriangle className="mr-2" />
              Suspicious Files
            </h2>
          </div>
          
          <div className="p-4">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      File Path
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Reason
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {scan.infected_files.filter(file => file.threat_type === 'suspicious').map((file, index) => (
                    <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200 font-mono">
                        <div className="flex items-center">
                          <FiFile className="mr-2 text-warning-500" />
                          {file.file_path}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-warning-600 dark:text-warning-400">
                        {file.threat_name}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
      
      {/* Clean Scan */}
      {scan.infected_files === 0 && scan.suspicious_files === 0 && scan.status === 'completed' && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
          <FiCheckCircle size={48} className="mx-auto text-success-500" />
          <h3 className="mt-4 text-lg font-medium text-gray-800 dark:text-white">
            No Threats Detected
          </h3>
          <p className="mt-2 text-gray-500 dark:text-gray-400">
            This scan did not detect any malicious or suspicious files on the device.
          </p>
        </div>
      )}
    </div>
  )
}

export default ScanDetail
