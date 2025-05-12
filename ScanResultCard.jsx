import { Link } from 'react-router-dom'
import { FiSearch, FiCheckCircle, FiAlertTriangle, FiAlertCircle, FiClock } from 'react-icons/fi'
import { formatDistanceToNow } from 'date-fns'

const ScanResultCard = ({ scan, deviceName }) => {
  // Format the scan date
  const scanTimeAgo = formatDistanceToNow(new Date(scan.scan_date), { addSuffix: true })
  
  // Determine status icon and color
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
  
  return (
    <Link 
      to={`/scans/${scan.id}`}
      className="block bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow p-4"
    >
      <div className="flex items-start">
        <div className={`p-3 rounded-full ${statusBg} ${statusText}`}>
          <FiSearch size={20} />
        </div>
        
        <div className="ml-4 flex-1">
          <div className="flex justify-between">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
              {deviceName || 'Unknown Device'}
            </h3>
            
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusBg} ${statusText}`}>
              <StatusIcon className="mr-1" />
              {statusLabel}
            </span>
          </div>
          
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Scan completed {scanTimeAgo}
          </p>
          
          <div className="mt-3 grid grid-cols-4 gap-2 text-sm">
            <div>
              <p className="text-gray-500 dark:text-gray-400">Total Files</p>
              <p className="font-medium text-gray-800 dark:text-gray-200">
                {scan.total_files}
              </p>
            </div>
            
            <div>
              <p className="text-gray-500 dark:text-gray-400">Scanned</p>
              <p className="font-medium text-gray-800 dark:text-gray-200">
                {scan.scanned_files}
              </p>
            </div>
            
            <div>
              <p className="text-gray-500 dark:text-gray-400">Infected</p>
              <p className={`font-medium ${scan.infected_files > 0 ? 'text-danger-600' : 'text-gray-800 dark:text-gray-200'}`}>
                {scan.infected_files}
              </p>
            </div>
            
            <div>
              <p className="text-gray-500 dark:text-gray-400">Suspicious</p>
              <p className={`font-medium ${scan.suspicious_files > 0 ? 'text-warning-600' : 'text-gray-800 dark:text-gray-200'}`}>
                {scan.suspicious_files}
              </p>
            </div>
          </div>
          
          {scan.status === 'completed' && scan.scan_duration && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Scan duration: {scan.scan_duration.toFixed(2)} seconds
            </p>
          )}
        </div>
      </div>
    </Link>
  )
}

export default ScanResultCard
