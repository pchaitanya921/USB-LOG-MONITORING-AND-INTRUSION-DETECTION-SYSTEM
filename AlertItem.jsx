import { useState } from 'react'
import { Link } from 'react-router-dom'
import { FiBell, FiHardDrive, FiSearch, FiCheck, FiX, FiAlertTriangle, FiAlertCircle } from 'react-icons/fi'
import { formatDistanceToNow } from 'date-fns'
import { markAlertAsRead } from '../api/alerts'

const AlertItem = ({ alert, onAlertRead }) => {
  const [isRead, setIsRead] = useState(alert.is_read)
  
  // Format the timestamp
  const timeAgo = formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })
  
  // Determine icon and color based on alert type and severity
  let Icon = FiBell
  let bgColor = 'bg-primary-100'
  let textColor = 'text-primary-600'
  
  if (alert.alert_type.includes('connection')) {
    Icon = FiHardDrive
    bgColor = 'bg-primary-100'
    textColor = 'text-primary-600'
  } else if (alert.alert_type.includes('scan')) {
    Icon = FiSearch
    bgColor = 'bg-primary-100'
    textColor = 'text-primary-600'
  } else if (alert.alert_type.includes('permission_granted')) {
    Icon = FiCheck
    bgColor = 'bg-success-100'
    textColor = 'text-success-600'
  } else if (alert.alert_type.includes('permission_denied')) {
    Icon = FiX
    bgColor = 'bg-danger-100'
    textColor = 'text-danger-600'
  } else if (alert.alert_type.includes('malware')) {
    Icon = FiAlertCircle
    bgColor = 'bg-danger-100'
    textColor = 'text-danger-600'
  }
  
  // Override colors based on severity
  if (alert.severity === 'critical') {
    bgColor = 'bg-danger-100'
    textColor = 'text-danger-600'
  } else if (alert.severity === 'warning') {
    bgColor = 'bg-warning-100'
    textColor = 'text-warning-600'
  }
  
  const handleMarkAsRead = async () => {
    if (isRead) return
    
    try {
      await markAlertAsRead(alert.id)
      setIsRead(true)
      if (onAlertRead) onAlertRead()
    } catch (error) {
      console.error('Error marking alert as read:', error)
    }
  }
  
  return (
    <div 
      className={`p-4 border-b border-gray-200 dark:border-gray-700 ${isRead ? 'bg-white dark:bg-gray-800' : 'bg-blue-50 dark:bg-gray-750'}`}
      onClick={handleMarkAsRead}
    >
      <div className="flex items-start">
        <div className={`p-2 rounded-full ${bgColor} ${textColor}`}>
          <Icon size={20} />
        </div>
        
        <div className="ml-3 flex-1">
          <div className="flex justify-between">
            <p className="text-sm font-medium text-gray-800 dark:text-white">
              {alert.message}
            </p>
            
            <div className="flex items-center">
              {!isRead && (
                <span className="h-2 w-2 bg-primary-500 rounded-full mr-2"></span>
              )}
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {timeAgo}
              </span>
            </div>
          </div>
          
          <div className="mt-2 flex justify-between items-center">
            <div className="flex space-x-2">
              {alert.device_id && (
                <Link 
                  to={`/devices/${alert.device_id}`}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600"
                  onClick={(e) => e.stopPropagation()}
                >
                  <FiHardDrive className="mr-1" />
                  View Device
                </Link>
              )}
              
              {alert.scan_id && (
                <Link 
                  to={`/scans/${alert.scan_id}`}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600"
                  onClick={(e) => e.stopPropagation()}
                >
                  <FiSearch className="mr-1" />
                  View Scan
                </Link>
              )}
            </div>
            
            <div>
              {alert.severity === 'critical' && (
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-danger-100 text-danger-800">
                  <FiAlertCircle className="mr-1" />
                  Critical
                </span>
              )}
              
              {alert.severity === 'warning' && (
                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-warning-100 text-warning-800">
                  <FiAlertTriangle className="mr-1" />
                  Warning
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AlertItem
