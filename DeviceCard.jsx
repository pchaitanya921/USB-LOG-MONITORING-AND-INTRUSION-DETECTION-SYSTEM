import { Link } from 'react-router-dom'
import { FiHardDrive, FiCheck, FiX, FiAlertTriangle } from 'react-icons/fi'
import { formatDistanceToNow } from 'date-fns'

const DeviceCard = ({ device }) => {
  const isConnected = device.is_connected
  const isPermitted = device.is_permitted
  
  // Format the last connected time
  const lastConnectedTime = device.last_connected_at 
    ? formatDistanceToNow(new Date(device.last_connected_at), { addSuffix: true })
    : 'Unknown'
  
  return (
    <Link 
      to={`/devices/${device.id}`}
      className="block bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow p-4"
    >
      <div className="flex items-start">
        <div className={`p-3 rounded-full ${isConnected ? 'bg-success-100 text-success-600' : 'bg-gray-100 text-gray-500'}`}>
          <FiHardDrive size={24} />
        </div>
        
        <div className="ml-4 flex-1">
          <div className="flex justify-between">
            <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
              {device.product_name || 'Unknown Device'}
            </h3>
            
            <div className="flex space-x-2">
              {isConnected ? (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                  Connected
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Disconnected
                </span>
              )}
              
              {isPermitted ? (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                  <FiCheck className="mr-1" />
                  Permitted
                </span>
              ) : (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger-100 text-danger-800">
                  <FiX className="mr-1" />
                  Blocked
                </span>
              )}
            </div>
          </div>
          
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            {device.manufacturer || 'Unknown Manufacturer'}
          </p>
          
          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <div>
              <p className="text-gray-500 dark:text-gray-400">Serial Number</p>
              <p className="font-medium text-gray-800 dark:text-gray-200">
                {device.serial_number || 'Unknown'}
              </p>
            </div>
            
            <div>
              <p className="text-gray-500 dark:text-gray-400">Last Connected</p>
              <p className="font-medium text-gray-800 dark:text-gray-200">
                {lastConnectedTime}
              </p>
            </div>
          </div>
          
          {isConnected && !isPermitted && (
            <div className="mt-3 flex items-center text-warning-600 dark:text-warning-400">
              <FiAlertTriangle className="mr-1" />
              <span className="text-sm">Waiting for permission</span>
            </div>
          )}
        </div>
      </div>
    </Link>
  )
}

export default DeviceCard
