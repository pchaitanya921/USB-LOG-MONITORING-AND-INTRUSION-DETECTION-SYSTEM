import { useState, useEffect } from 'react'
import { FiSettings, FiSave, FiMail, FiPhone, FiShield, FiSearch, FiBell } from 'react-icons/fi'
import { fetchSettings, updateSettings } from '../api/settings'
import { toast } from 'react-toastify'

const Settings = () => {
  const [settings, setSettings] = useState({
    email_notifications: true,
    sms_notifications: true,
    auto_scan: true,
    require_permission: true,
    email: '',
    phone: ''
  })
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  
  useEffect(() => {
    fetchSettingsData()
  }, [])
  
  const fetchSettingsData = async () => {
    setIsLoading(true)
    
    try {
      const data = await fetchSettings()
      setSettings(data)
    } catch (error) {
      console.error('Error fetching settings:', error)
      toast.error('Error loading settings')
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : value
    })
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSaving(true)
    
    try {
      await updateSettings(settings)
      toast.success('Settings saved successfully')
    } catch (error) {
      console.error('Error saving settings:', error)
      toast.error('Error saving settings')
    } finally {
      setIsSaving(false)
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
    <div className="max-w-3xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white flex items-center">
            <FiSettings className="mr-2" />
            System Settings
          </h2>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Notification Settings */}
          <div>
            <h3 className="text-md font-medium text-gray-800 dark:text-white mb-4 flex items-center">
              <FiBell className="mr-2" />
              Notification Settings
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="email_notifications" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Email Notifications
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Receive email alerts for USB events and threats
                  </p>
                </div>
                <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out rounded-full">
                  <input
                    type="checkbox"
                    id="email_notifications"
                    name="email_notifications"
                    checked={settings.email_notifications}
                    onChange={handleChange}
                    className="absolute w-6 h-6 transition duration-200 ease-in-out transform bg-white border-2 rounded-full appearance-none cursor-pointer peer border-gray-300 dark:border-gray-600 checked:translate-x-6 checked:border-primary-500 dark:checked:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50"
                  />
                  <label
                    htmlFor="email_notifications"
                    className="block w-full h-full transition duration-200 ease-in-out rounded-full cursor-pointer bg-gray-300 dark:bg-gray-600 peer-checked:bg-primary-500"
                  ></label>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="sms_notifications" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    SMS Notifications
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Receive SMS alerts for USB events and threats
                  </p>
                </div>
                <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out rounded-full">
                  <input
                    type="checkbox"
                    id="sms_notifications"
                    name="sms_notifications"
                    checked={settings.sms_notifications}
                    onChange={handleChange}
                    className="absolute w-6 h-6 transition duration-200 ease-in-out transform bg-white border-2 rounded-full appearance-none cursor-pointer peer border-gray-300 dark:border-gray-600 checked:translate-x-6 checked:border-primary-500 dark:checked:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50"
                  />
                  <label
                    htmlFor="sms_notifications"
                    className="block w-full h-full transition duration-200 ease-in-out rounded-full cursor-pointer bg-gray-300 dark:bg-gray-600 peer-checked:bg-primary-500"
                  ></label>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Email Address
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiMail className="text-gray-400" />
                    </div>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={settings.email}
                      onChange={handleChange}
                      className="pl-10 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white"
                      placeholder="you@example.com"
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    Phone Number
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <FiPhone className="text-gray-400" />
                    </div>
                    <input
                      type="tel"
                      id="phone"
                      name="phone"
                      value={settings.phone}
                      onChange={handleChange}
                      className="pl-10 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm dark:bg-gray-700 dark:text-white"
                      placeholder="+1234567890"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Security Settings */}
          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-md font-medium text-gray-800 dark:text-white mb-4 flex items-center">
              <FiShield className="mr-2" />
              Security Settings
            </h3>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="require_permission" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Require Permission for USB Devices
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Ask for permission before allowing access to USB devices
                  </p>
                </div>
                <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out rounded-full">
                  <input
                    type="checkbox"
                    id="require_permission"
                    name="require_permission"
                    checked={settings.require_permission}
                    onChange={handleChange}
                    className="absolute w-6 h-6 transition duration-200 ease-in-out transform bg-white border-2 rounded-full appearance-none cursor-pointer peer border-gray-300 dark:border-gray-600 checked:translate-x-6 checked:border-primary-500 dark:checked:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50"
                  />
                  <label
                    htmlFor="require_permission"
                    className="block w-full h-full transition duration-200 ease-in-out rounded-full cursor-pointer bg-gray-300 dark:bg-gray-600 peer-checked:bg-primary-500"
                  ></label>
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <label htmlFor="auto_scan" className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Auto-Scan USB Devices
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Automatically scan USB devices when connected
                  </p>
                </div>
                <div className="relative inline-block w-12 h-6 transition duration-200 ease-in-out rounded-full">
                  <input
                    type="checkbox"
                    id="auto_scan"
                    name="auto_scan"
                    checked={settings.auto_scan}
                    onChange={handleChange}
                    className="absolute w-6 h-6 transition duration-200 ease-in-out transform bg-white border-2 rounded-full appearance-none cursor-pointer peer border-gray-300 dark:border-gray-600 checked:translate-x-6 checked:border-primary-500 dark:checked:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-opacity-50"
                  />
                  <label
                    htmlFor="auto_scan"
                    className="block w-full h-full transition duration-200 ease-in-out rounded-full cursor-pointer bg-gray-300 dark:bg-gray-600 peer-checked:bg-primary-500"
                  ></label>
                </div>
              </div>
            </div>
          </div>
          
          <div className="pt-6 flex justify-end">
            <button
              type="submit"
              disabled={isSaving}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              {isSaving ? (
                <>
                  <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full"></div>
                  Saving...
                </>
              ) : (
                <>
                  <FiSave className="mr-2" />
                  Save Settings
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Settings
