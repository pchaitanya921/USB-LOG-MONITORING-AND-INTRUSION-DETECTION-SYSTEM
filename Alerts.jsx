import { useState, useEffect } from 'react'
import { FiBell, FiFilter, FiCheck } from 'react-icons/fi'
import { fetchAlerts, markAllAlertsAsRead } from '../api/alerts'
import AlertItem from '../components/AlertItem'
import { toast } from 'react-toastify'

const Alerts = ({ onAlertRead }) => {
  const [alerts, setAlerts] = useState([])
  const [filteredAlerts, setFilteredAlerts] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [filter, setFilter] = useState('all') // 'all', 'unread', 'critical', 'warning', 'info'
  
  useEffect(() => {
    fetchAlertsData()
  }, [])
  
  useEffect(() => {
    // Apply filters
    let result = [...alerts]
    
    if (filter === 'unread') {
      result = result.filter(alert => !alert.is_read)
    } else if (filter === 'critical') {
      result = result.filter(alert => alert.severity === 'critical')
    } else if (filter === 'warning') {
      result = result.filter(alert => alert.severity === 'warning')
    } else if (filter === 'info') {
      result = result.filter(alert => alert.severity === 'info')
    }
    
    // Sort by timestamp (newest first)
    result.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    
    setFilteredAlerts(result)
  }, [alerts, filter])
  
  const fetchAlertsData = async () => {
    setIsLoading(true)
    
    try {
      const data = await fetchAlerts()
      setAlerts(data)
    } catch (error) {
      console.error('Error fetching alerts:', error)
      toast.error('Error loading alerts')
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleMarkAllAsRead = async () => {
    try {
      await markAllAlertsAsRead()
      
      // Update local state
      setAlerts(alerts.map(alert => ({ ...alert, is_read: true })))
      
      // Call parent callback if provided
      if (onAlertRead) onAlertRead()
      
      toast.success('All alerts marked as read')
    } catch (error) {
      console.error('Error marking all alerts as read:', error)
      toast.error('Error marking alerts as read')
    }
  }
  
  const handleAlertRead = () => {
    // Refresh alerts after a short delay
    setTimeout(() => {
      fetchAlertsData()
      
      // Call parent callback if provided
      if (onAlertRead) onAlertRead()
    }, 500)
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
              All Alerts
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'unread'
                  ? 'bg-primary-100 text-primary-800 dark:bg-primary-800 dark:text-primary-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Unread
            </button>
            <button
              onClick={() => setFilter('critical')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'critical'
                  ? 'bg-danger-100 text-danger-800 dark:bg-danger-800 dark:text-danger-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Critical
            </button>
            <button
              onClick={() => setFilter('warning')}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                filter === 'warning'
                  ? 'bg-warning-100 text-warning-800 dark:bg-warning-800 dark:text-warning-100'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              Warning
            </button>
          </div>
          
          <button
            onClick={handleMarkAllAsRead}
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <FiCheck className="mr-2" />
            Mark All as Read
          </button>
        </div>
      </div>
      
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        {filteredAlerts.length > 0 ? (
          <div>
            {filteredAlerts.map(alert => (
              <AlertItem 
                key={alert.id} 
                alert={alert} 
                onAlertRead={handleAlertRead} 
              />
            ))}
          </div>
        ) : (
          <div className="p-8 text-center">
            <FiBell size={48} className="mx-auto text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-800 dark:text-white">
              No alerts found
            </h3>
            <p className="mt-2 text-gray-500 dark:text-gray-400">
              {alerts.length > 0
                ? 'No alerts match your current filters'
                : 'No alerts have been generated yet'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Alerts
