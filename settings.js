import axios from 'axios'

const API_URL = '/api/settings'

export const fetchSettings = async () => {
  try {
    const response = await axios.get(API_URL)
    return response.data
  } catch (error) {
    console.error('Error fetching settings:', error)
    throw error
  }
}

export const updateSettings = async (settings) => {
  try {
    const response = await axios.put(API_URL, settings)
    return response.data
  } catch (error) {
    console.error('Error updating settings:', error)
    throw error
  }
}
