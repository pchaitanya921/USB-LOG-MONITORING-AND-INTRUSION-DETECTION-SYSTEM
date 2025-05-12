import axios from 'axios'

const API_URL = '/api/alerts'

export const fetchAlerts = async (params = {}) => {
  try {
    const response = await axios.get(API_URL, { params })
    return response.data
  } catch (error) {
    console.error('Error fetching alerts:', error)
    throw error
  }
}

export const fetchAlertById = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/${id}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching alert ${id}:`, error)
    throw error
  }
}

export const markAlertAsRead = async (id) => {
  try {
    const response = await axios.post(`${API_URL}/${id}/read`)
    return response.data
  } catch (error) {
    console.error(`Error marking alert ${id} as read:`, error)
    throw error
  }
}

export const markAllAlertsAsRead = async () => {
  try {
    const response = await axios.post(`${API_URL}/read-all`)
    return response.data
  } catch (error) {
    console.error('Error marking all alerts as read:', error)
    throw error
  }
}

export const fetchUnreadAlertCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/unread-count`)
    return response.data.unread_count
  } catch (error) {
    console.error('Error fetching unread alert count:', error)
    throw error
  }
}
