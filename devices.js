import axios from 'axios'

const API_URL = '/api/devices'

export const fetchDevices = async () => {
  try {
    const response = await axios.get(API_URL)
    return response.data
  } catch (error) {
    console.error('Error fetching devices:', error)
    throw error
  }
}

export const fetchConnectedDevices = async () => {
  try {
    const response = await axios.get(`${API_URL}/connected`)
    return response.data
  } catch (error) {
    console.error('Error fetching connected devices:', error)
    throw error
  }
}

export const fetchDeviceById = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/${id}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching device ${id}:`, error)
    throw error
  }
}

export const setDevicePermission = async (id, isPermitted) => {
  try {
    const response = await axios.post(`${API_URL}/permission/${id}`, { is_permitted: isPermitted })
    return response.data
  } catch (error) {
    console.error(`Error setting permission for device ${id}:`, error)
    throw error
  }
}

export const refreshDevices = async () => {
  try {
    const response = await axios.get(`${API_URL}/refresh`)
    return response.data
  } catch (error) {
    console.error('Error refreshing devices:', error)
    throw error
  }
}
