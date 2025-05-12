import React from 'react'

const StatCard = ({ title, value, icon, color }) => {
  // Define color classes based on the color prop
  const colorClasses = {
    blue: {
      bg: 'bg-primary-100',
      text: 'text-primary-600',
    },
    green: {
      bg: 'bg-success-100',
      text: 'text-success-600',
    },
    red: {
      bg: 'bg-danger-100',
      text: 'text-danger-600',
    },
    yellow: {
      bg: 'bg-warning-100',
      text: 'text-warning-600',
    },
    gray: {
      bg: 'bg-gray-100',
      text: 'text-gray-600',
    },
  }
  
  const { bg, text } = colorClasses[color] || colorClasses.blue
  
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-5">
      <div className="flex items-center">
        <div className={`p-3 rounded-full ${bg} ${text}`}>
          {icon}
        </div>
        
        <div className="ml-5">
          <p className="text-gray-500 dark:text-gray-400 text-sm font-medium uppercase">
            {title}
          </p>
          <p className="text-2xl font-semibold text-gray-800 dark:text-white">
            {value}
          </p>
        </div>
      </div>
    </div>
  )
}

export default StatCard
