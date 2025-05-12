import axios from 'axios'

const API_URL = '/api/scans'

export const fetchScans = async () => {
  try {
    const response = await axios.get(API_URL)
    return response.data
  } catch (error) {
    console.error('Error fetching scans:', error)
    throw error
  }
}

export const fetchScanById = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/${id}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching scan ${id}:`, error)
    throw error
  }
}

export const fetchDeviceScans = async (deviceId) => {
  try {
    const response = await axios.get(`${API_URL}/device/${deviceId}`)
    return response.data
  } catch (error) {
    console.error(`Error fetching scans for device ${deviceId}:`, error)
    throw error
  }
}

export const startScan = async (deviceId) => {
  try {
    const response = await axios.post(`${API_URL}/start/${deviceId}`)
    return response.data
  } catch (error) {
    console.error(`Error starting scan for device ${deviceId}:`, error)
    throw error
  }
}
